from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Category, Product, Review
from .serializers import (CategorySerializer, ProductDetailSerializer,
                          ProductSerializer, ReviewSerializer)


# List all products
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        if not self.queryset.exists():
            return Response({"detail": "No products found."}, status=status.HTTP_404_NOT_FOUND)
        return super().get(request, *args, **kwargs)


# Retrieve product details
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]  # Unauthenticated users can access

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)


# List all categories
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]  # Unauthenticated users can access

    def get(self, request, *args, **kwargs):
        if not self.queryset.exists():
            return Response({"detail": "No categories found."}, status=status.HTTP_404_NOT_FOUND)
        return super().get(request, *args, **kwargs)


# List featured categories
class FeaturedCategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(featured=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]  # Unauthenticated users can access

    def get(self, request, *args, **kwargs):
        if not self.queryset.exists():
            return Response({"detail": "No featured categories found."}, status=status.HTTP_404_NOT_FOUND)
        return super().get(request, *args, **kwargs)

# List products by category


class ProductByCategoryView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # Unauthenticated users can access

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        queryset = Product.objects.filter(category__slug=category_slug)
        if not queryset.exists():
            raise NotFound(
                detail="Invalid category or no products found in this category.", code=status.HTTP_404_NOT_FOUND)
        return queryset


class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        product_id = self.request.data.get(
            'product_id')  # Get product_id from POST data
        if not product_id:
            raise ValidationError('Product ID is required to create a review.')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValidationError('Product not found.')

        # Ensure the user hasn't already reviewed this product
        if Review.objects.filter(product=product, user=self.request.user).exists():
            raise ValidationError('You have already reviewed this product.')

        serializer.save(user=self.request.user, product=product)


class ReviewUpdateView(generics.UpdateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Limit the queryset to the reviews made by the current user.
        return Review.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        review = self.get_object()
        if review.user != self.request.user:
            raise ValidationError('You can only update your own review.')
        serializer.save()


class ReviewDeleteView(generics.DestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Limit the queryset to the reviews made by the current user.
        return Review.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise ValidationError('You can only delete your own review.')
        instance.delete()
