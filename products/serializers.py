from rest_framework import serializers

from .models import Category, Image, Product, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Display username instead of ID

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating',
                  'comment', 'created_at', 'updated_at']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    average_rating = serializers.DecimalField(
        max_digits=2, decimal_places=1, read_only=True
    )
    # To include product images
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'discount', 'stock', 'images',
                  'category', 'category_id', 'average_rating', 'created_at', 'updated_at']
