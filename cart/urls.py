from django.urls import path

from .views import CartViewSet

urlpatterns = [
    path(
        '', CartViewSet.as_view({'get': 'retrieve_cart'}), name='cart-detail'),
    path('add/',
         CartViewSet.as_view({'post': 'add_to_cart'}), name='cart-add'),
    path('item/<int:pk>/update/',
         CartViewSet.as_view({'patch': 'update_cart_item'}), name='cart-item-update'),
    path('item/<int:pk>/remove/',
         CartViewSet.as_view({'delete': 'remove_cart_item'}), name='cart-item-remove'),
    path('clear/',
         CartViewSet.as_view({'delete': 'clear_cart'}), name='cart-clear'),
]
