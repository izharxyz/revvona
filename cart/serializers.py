from rest_framework import serializers

from products.serializers import ProductSerializer

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']
        extra_kwargs = {
            # Ensure quantity is always at least 1
            'quantity': {'min_value': 1}
        }


class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']

    def validate(self, data):
        product = data['product']
        if product.stock < data['quantity']:
            raise serializers.ValidationError('Not enough stock available')
        return data


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at', 'updated_at']
