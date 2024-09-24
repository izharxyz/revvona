from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'quote',
                  'image', 'featured', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    # Nested serializer for category
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )  # For writing the category via ID

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'discount', 'stock',
                  'image', 'category', 'category_id', 'created_at', 'updated_at']
