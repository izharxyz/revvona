from accounts.serializers import AddressSerializer
from products.serializers import ProductSerializer
from revvona.utils import CustomSerializer

from .models import Order, OrderItem, Payment


class OrderItemSerializer(CustomSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'discounted_price']


class OrderSerializer(CustomSerializer):
    shipping_address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'shipping_address', 'billing_address',
                  'items', 'total_price', 'delivery_charge', 'status', 'created_at', 'updated_at']
        read_only_fields = ['total_price',
                            'status', 'created_at', 'updated_at']


class PaymentSerializer(CustomSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'method', 'amount', 'razorpay_order_id', 'razorpay_payment_id',
                  'razorpay_signature', 'payment_status', 'created_at']
