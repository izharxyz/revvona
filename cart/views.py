from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Cart, CartItem, Product
from .serializers import CartItemSerializer, CartSerializer


# Get or create a cart for the authenticated user
class CartView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Get or create the cart for the user
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def get(self, request, *args, **kwargs):
        cart = self.get_object()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

# Add an item to the cart


class AddToCartView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def perform_create(self, serializer):
        # Ensure the product exists before adding to the cart
        product_id = self.request.data.get('product')
        try:
            product = Product.objects.get(id=product_id)
            cart, _ = Cart.objects.get_or_create(user=self.request.user)
            serializer.save(cart=cart, product=product)
        except Product.DoesNotExist:
            raise serializer.ValidationError("Product does not exist.")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Update the quantity of an item in the cart


class UpdateCartItemView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

# Remove an item from the cart


class RemoveCartItemView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)