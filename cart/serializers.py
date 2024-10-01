from rest_framework import serializers

from products.models import Product
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

    def validate(self, data):
        product = self.instance.product if self.instance else Product.objects.get(
            id=self.initial_data.get('product'))

        if isinstance(product, int):
            product = Product.objects.get(id=product)

        if data["quantity"] > product.stock:
            raise serializers.ValidationError({
                "stock_error": "Requested quantity exceeds available stock"})

        return data


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at', 'updated_at']
