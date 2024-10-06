from rest_framework import serializers

from revvona.utils import CustomSerializer

from .models import Category, Image, Product, Review


class CategorySerializer(CustomSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ReviewSerializer(CustomSerializer):
    user = serializers.StringRelatedField()  # Display username instead of ID

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating',
                  'comment', 'created_at', 'updated_at']


class ImageSerializer(CustomSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']


class ProductSerializer(CustomSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    average_rating = serializers.DecimalField(
        max_digits=2, decimal_places=1, read_only=True
    )
    images = ImageSerializer(many=True, read_only=True)
    total_reviews = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'price', 'discount', 'stock', 'images',
                  'category', 'category_id', 'average_rating', 'total_reviews',
                  'created_at', 'updated_at']


class ProductDetailSerializer(ProductSerializer):
    detail = serializers.CharField(read_only=True)

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['detail']
