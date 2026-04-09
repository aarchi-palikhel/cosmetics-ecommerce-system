from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.initiate_payment, name='esewa_checkout'),
    path('success/', views.payment_success, name='esewa_success'),
    path('failure/', views.payment_failure, name='esewa_failure'),
]
