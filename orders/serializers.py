from rest_framework import serializers

from accounts.models import Address
from accounts.serializers import AddressSerializer

from .models import Order, OrderItem, Payment


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    shipping_address = AddressSerializer()
    billing_address = AddressSerializer(allow_null=True, required=False)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'total_price', 'shipping_address', 'billing_address',
            'status', 'items', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        shipping_address_data = validated_data.pop('shipping_address')
        billing_address_data = validated_data.pop('billing_address', None)

        # Save the order
        order = Order.objects.create(**validated_data)

        # Save the order items
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        shipping_address_data = validated_data.pop('shipping_address', None)
        billing_address_data = validated_data.pop('billing_address', None)

        # Update order fields
        instance.status = validated_data.get('status', instance.status)
        instance.total_price = validated_data.get(
            'total_price', instance.total_price)

        # Update order items if provided
        if items_data:
            instance.items.all().delete()
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)

        # Update addresses if provided
        if shipping_address_data:
            shipping_address = Address.objects.create(**shipping_address_data)
            instance.shipping_address = shipping_address

        if billing_address_data:
            billing_address = Address.objects.create(**billing_address_data)
            instance.billing_address = billing_address

        instance.save()
        return instance


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'method', 'amount',
                  'payment_status', 'created_at']
