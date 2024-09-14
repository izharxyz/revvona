from django.urls import path

from .views import (OrderCreateView, OrderDetailView, OrderListView,
                    PaymentCreateView, PaymentDetailView)

urlpatterns = [
    # List all orders for the authenticated user
    path('', OrderListView.as_view(), name='order-list'),
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),

    # Payment views
    path('payment/create/', PaymentCreateView.as_view(), name='payment-create'),
    path('<int:order_id>/payment/',
         PaymentDetailView.as_view(), name='payment-detail'),
]
