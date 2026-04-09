from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Review
from .forms import ReviewForm


def product_list(request):
    products = Product.objects.select_related('category').all()
    categories = Category.objects.all()

    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')

    if query:
        products = products.filter(name__icontains=query)
    if category_id:
        products = products.filter(category__id=category_id)

    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.select_related('user').all()
    user_review = None

    if request.user.is_authenticated:
        user_review = Review.objects.filter(product=product, user=request.user).first()

    form = ReviewForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to leave a review.')
            return redirect('login')
        if user_review:
            messages.error(request, 'You have already reviewed this product.')
        else:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, 'Your review has been submitted.')
                return redirect('product_detail', pk=pk)

    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
        'user_review': user_review,
    })
