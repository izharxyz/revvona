from rest_framework import serializers

from products.models import Product
from products.serializers import ProductSerializer

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

    def validate(self, data):
        # Get the product instance
        product = self.instance.product if self.instance else Product.objects.get(
            id=self.initial_data.get('product'))

        # Set default quantity if not provided
        quantity = data.get('quantity', 1)  # Default to 1 if not provided
        # Ensure quantity is in data for further validation
        data['quantity'] = quantity

        if quantity > product.stock:
            raise serializers.ValidationError({
                "stock_error": "Requested quantity exceeds available stock"})

        return data

    def create(self, validated_data):
        # If quantity is not in the validated data, set it to the default
        quantity = validated_data.get('quantity', 1)
        validated_data['quantity'] = quantity
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # If quantity is not in the validated data, set it to the default
        quantity = validated_data.get('quantity', 1)
        validated_data['quantity'] = quantity
        return super().update(instance, validated_data)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at', 'updated_at']
