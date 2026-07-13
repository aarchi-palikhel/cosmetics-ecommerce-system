from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Avg
from .models import Product, Category, Review, Wishlist
from .forms import ReviewForm


def product_search_suggestions(request):
    q = request.GET.get('q', '').strip()
    results = []
    if len(q) >= 2:
        products = Product.objects.filter(name__icontains=q).select_related('category')[:6]
        results = [
            {
                'id': p.id,
                'name': p.name,
                'category': p.category.name if p.category else '',
                'price': str(p.price),
                'image': p.image.url if p.image else None,
            }
            for p in products
        ]
    return JsonResponse({'results': results})


def product_list(request):
    products = Product.objects.select_related('category').all()
    categories = Category.objects.all()

    query       = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    sort        = request.GET.get('sort', '')

    if query:
        products = products.filter(name__icontains=query)
    if category_id:
        products = products.filter(category__id=category_id)

    SORT_OPTIONS = {
        'price_asc':  'price',
        'price_desc': '-price',
        'newest':     '-created_at',
        'top_rated':  '-avg_rating',
    }
    if sort in SORT_OPTIONS:
        if sort == 'top_rated':
            products = products.annotate(avg_rating=Avg('reviews__rating'))
        products = products.order_by(SORT_OPTIONS[sort])

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(
            Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    return render(request, 'products/product_list.html', {
        'products': page_obj,           # page_obj is iterable like a queryset
        'page_obj': page_obj,
        'paginator': paginator,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'sort': sort,
        'wishlist_ids': wishlist_ids,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.select_related('user').all()
    user_review = None
    in_wishlist = False

    if request.user.is_authenticated:
        user_review = Review.objects.filter(product=product, user=request.user).first()
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

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
        'in_wishlist': in_wishlist,
    })


@login_required
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if not created:
        item.delete()
        in_wishlist = False
    else:
        in_wishlist = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'in_wishlist': in_wishlist})

    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


@login_required
def wishlist_page(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product', 'product__category')
    return render(request, 'products/wishlist.html', {'items': items})
