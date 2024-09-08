from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer

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
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # Unauthenticated users can access

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        