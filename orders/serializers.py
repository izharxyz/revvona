from rest_framework import serializers

from accounts.models import Address
from accounts.serializers import AddressSerializer

from .models import Order, OrderItem, Payment


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'shipping_address', 'billing_address',
                  'order_items', 'total_price', 'status', 'created_at', 'updated_at']
        read_only_fields = ['total_price',
                            'status', 'created_at', 'updated_at']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'method', 'amount', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature',
                  'payment_status', 'created_at']
