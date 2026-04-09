from django.contrib import admin
from .models import Product, Category, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'is_featured', 'created_at')
    list_filter = ('category', 'is_featured')
    list_editable = ('is_featured',)
    search_fields = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'timestamp')
    list_filter = ('rating',)
    search_fields = ('user__username', 'product__name')
