from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from products.models import Product
from .models import Cart, CartItem


def get_or_create_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return cart


@login_required
def cart_detail(request):
    cart = get_or_create_cart(request)
    return render(request, 'cart/cart.html', {'cart': cart})


@require_POST
@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    # Stock check
    if not product.in_stock:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': f'"{product.name}" is out of stock.'})
        messages.error(request, f'"{product.name}" is out of stock.')
        return redirect(request.POST.get('next', 'product_list'))

    cart = get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    new_quantity = quantity if created else item.quantity + quantity

    # Don't allow adding more than available stock
    if new_quantity > product.stock:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': f'Only {product.stock} unit(s) available.'})
        messages.error(request, f'Only {product.stock} unit(s) of "{product.name}" available.')
        return redirect(request.POST.get('next', 'product_list'))

    item.quantity = new_quantity
    item.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'"{product.name}" added to cart.',
            'cart_count': cart.get_total_items(),
        })

    messages.success(request, f'"{product.name}" added to cart.')
    return redirect(request.POST.get('next', 'product_list'))


@require_POST
@login_required
def cart_update(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart = item.cart
    quantity = int(request.POST.get('quantity', 1))
    removed = False

    if quantity > 0:
        item.quantity = quantity
        item.save()
        item_subtotal = str(item.get_subtotal())
    else:
        item.delete()
        item_subtotal = '0'
        removed = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart.refresh_from_db()
        return JsonResponse({
            'success': True,
            'item_subtotal': item_subtotal,
            'cart_subtotal': str(cart.get_subtotal()),
            'cart_tax': str(cart.get_tax()),
            'cart_total': str(cart.get_total()),
            'cart_count': cart.get_total_items(),
            'removed': removed,
        })

    return redirect('cart_detail')


@require_POST
@login_required
def cart_remove(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart = item.cart
    product_name = item.product.name
    item.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart.refresh_from_db()
        return JsonResponse({
            'success': True,
            'message': f'"{product_name}" removed from cart.',
            'cart_subtotal': str(cart.get_subtotal()),
            'cart_tax': str(cart.get_tax()),
            'cart_total': str(cart.get_total()),
            'cart_count': cart.get_total_items(),
        })

    messages.success(request, f'"{product_name}" removed from cart.')
    return redirect('cart_detail')
