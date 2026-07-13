from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.initiate_payment, name='esewa_checkout'),
    path('success/', views.payment_success, name='esewa_success'),
    path('failure/', views.payment_failure, name='esewa_failure'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/retry/', views.retry_payment, name='retry_payment'),
    path('orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
]
