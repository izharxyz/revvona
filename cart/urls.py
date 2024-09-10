from django.urls import path

from .views import (AddToCartView, CartItemListView, CartView, ClearCartView,
                    RemoveCartItemView)

urlpatterns = [
    # List all items in cart
    path('', CartView.as_view(), name='cart-create-or-retrieve'),
    path('items/', CartItemListView.as_view(), name='cart-items'),
    path('add/', AddToCartView.as_view(),
         name='add-to-cart'),
    path('remove/<int:pk>/', RemoveCartItemView.as_view(),
         name='remove-cart-item'),
    path('clear/', ClearCartView.as_view(), name='clear-cart'),
]
