from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistrationForm, LoginForm, ProfileForm


def home_view(request):
    featured_products = []
    try:
        from products.models import Product
        featured_products = Product.objects.filter(is_featured=True).select_related('category')[:8]
    except Exception:
        pass
    return render(request, 'accounts/home.html', {'featured_products': featured_products})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Registration successful! Welcome {user.username}.')
            return redirect('dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard_view(request):
    from cart.models import Cart
    from payments.models import Payment
    from products.models import Review

    cart = Cart.objects.filter(user=request.user).first()
    cart_items_count = cart.get_total_items() if cart else 0

    total_orders = Payment.objects.filter(user=request.user, status='COMPLETE').count()
    total_spent = Payment.objects.filter(user=request.user, status='COMPLETE').values_list('total_amount', flat=True)
    total_spent = sum(total_spent)

    total_reviews = Review.objects.filter(user=request.user).count()

    recent_orders = Payment.objects.filter(user=request.user).order_by('-created_at')[:5]

    return render(request, 'accounts/dashboard.html', {
        'cart_items_count': cart_items_count,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'total_reviews': total_reviews,
        'recent_orders': recent_orders,
    })


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})
