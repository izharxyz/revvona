from rest_framework import serializers

from .models import Category, Product, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'quote',
                  'image', 'featured', 'created_at', 'updated_at']


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Display username instead of ID

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating',
                  'comment', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    average_rating = serializers.DecimalField(
        max_digits=2, decimal_places=1, read_only=True
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'discount', 'stock', 'image',
                  'category', 'category_id', 'average_rating', 'created_at', 'updated_at']


class ProductDetailSerializer(ProductSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['reviews']
