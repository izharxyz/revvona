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
