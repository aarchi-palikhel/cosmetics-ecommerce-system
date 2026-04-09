from decimal import Decimal
from products.models import Product

CART_SESSION_KEY = 'cart'
TAX_RATE = Decimal('0.13')  # 13% VAT (Nepal)


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if not cart:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        pid = str(product.id)
        if pid not in self.cart:
            self.cart[pid] = {'quantity': 0, 'price': str(product.price)}
        if override_quantity:
            self.cart[pid]['quantity'] = quantity
        else:
            self.cart[pid]['quantity'] += quantity
        self.save()

    def remove(self, product):
        pid = str(product.id)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['subtotal'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_subtotal(self):
        return round(sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values()), 2)

    def get_tax(self):
        return round(self.get_subtotal() * TAX_RATE, 2)

    def get_total(self):
        return round(self.get_subtotal() + self.get_tax(), 2)

    def clear(self):
        del self.session[CART_SESSION_KEY]
        self.save()
