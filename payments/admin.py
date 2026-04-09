from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_amount', 'status', 'ref_id', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'transaction_uuid', 'ref_id')
