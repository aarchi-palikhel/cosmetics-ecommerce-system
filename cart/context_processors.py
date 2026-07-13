from .models import Cart


def cart(request):
    """
    Inject the current user's cart into every template context.
    Uses get() instead of get_or_create() so we never write to the DB
    on every page load — the cart is created on first add-to-cart instead.
    """
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        return {'cart': cart}
    return {'cart': None}
