from django.contrib import admin
from .models import Payment, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_price', 'quantity', 'subtotal')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_uuid', 'total_amount', 'status', 'ref_id', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'transaction_uuid', 'ref_id')
    inlines = [OrderItemInline]
