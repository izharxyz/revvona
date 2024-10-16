from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('api/v1/', include('products.urls')),
    path('api/v1/account/', include('accounts.urls')),
    path('api/v1/cart/', include('cart.urls')),
    path('api/v1/checkout/', include('checkout.urls')),
    path('api/v1/about/', include('about.urls')),
    path('', admin.site.urls),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
