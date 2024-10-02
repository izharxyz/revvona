from django.urls import path

from . import views

urlpatterns = [
    # Order Management
    path('orders/',
         views.OrderViewSet.as_view({'get': 'list_orders'}), name="order-list"),
    path('orders/create/',
         views.OrderViewSet.as_view({'post': 'create_order'}), name="order-create"),
    path('orders/<int:pk>/',
         views.OrderViewSet.as_view({'get': 'retrieve_order'}), name="order-detail"),

    # Updates only shipping address
    path('orders/<int:pk>/update/',
         views.OrderViewSet.as_view({'put': 'update_order'}), name="order-update"),
    path('orders/<int:pk>/cancel/',
         views.OrderViewSet.as_view({'put': 'cancel_order'}), name="order-cancel"),
    path('orders/<int:pk>/return/',
         views.OrderViewSet.as_view({'put': 'return_order'}), name="order-return"),

    # Payment Management
    path('payments/create/',
         views.PaymentViewSet.as_view({'post': 'create_payment'}), name="payment-create"),
    path('payments/verify/',
         views.PaymentViewSet.as_view({'put': 'verify_payment'}), name="payment-verify"),
    path('payments/<int:order_id>/',
         views.PaymentViewSet.as_view({'get': 'retrieve_payment'}), name="payment-detail"),
]
