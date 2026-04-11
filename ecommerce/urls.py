from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('__reload__/', include('django_browser_reload.urls')),
    path('payments/', include('payments.urls')),
    path('mailer/', include('mailer.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
