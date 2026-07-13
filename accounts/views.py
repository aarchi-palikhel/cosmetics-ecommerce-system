import logging

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum

from .forms import RegistrationForm, LoginForm, ProfileForm

logger = logging.getLogger(__name__)


def home_view(request):
    featured_products = []
    wishlist_ids = set()
    try:
        from products.models import Product, Wishlist
        featured_products = Product.objects.filter(
            is_featured=True
        ).select_related('category')[:8]
        if request.user.is_authenticated:
            wishlist_ids = set(
                Wishlist.objects.filter(
                    user=request.user
                ).values_list('product_id', flat=True)
            )
    except Exception:
        logger.exception("Failed to load featured products on home page")
    return render(request, 'accounts/home.html', {
        'featured_products': featured_products,
        'wishlist_ids': wishlist_ids,
    })


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
    if request.method == 'POST':
        logout(request)
    return redirect('home')


@login_required
def dashboard_view(request):
    from cart.models import Cart
    from payments.models import Payment
    from products.models import Review

    cart = Cart.objects.filter(user=request.user).first()
    cart_items_count = cart.get_total_items() if cart else 0

    completed_payments = Payment.objects.filter(user=request.user, status='COMPLETE')
    total_orders = completed_payments.count()
    total_spent = completed_payments.aggregate(s=Sum('total_amount'))['s'] or 0

    total_reviews = Review.objects.filter(user=request.user).count()

    recent_orders = Payment.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]

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
