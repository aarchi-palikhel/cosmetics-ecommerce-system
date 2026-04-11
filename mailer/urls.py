from django.urls import path
from . import views

urlpatterns = [
    path('', views.compose, name='mailer_compose'),
]
