from decimal import Decimal
from django.db import models
from django.conf import settings
from products.models import Product

TAX_RATE = Decimal('0.13')


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    def get_subtotal(self):
        return round(sum(item.get_subtotal() for item in self.items.all()), 2)

    def get_tax(self):
        return round(self.get_subtotal() * TAX_RATE, 2)

    def get_total(self):
        return round(self.get_subtotal() + self.get_tax(), 2)

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_subtotal(self):
        return round(self.product.price * self.quantity, 2)
