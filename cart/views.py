from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cart, CartItem, Product
from .serializers import CartItemSerializer, CartSerializer


### Helper Functions for Consistent Responses ###
def success_response(data, message="Success", status_code=status.HTTP_200_OK):
    return Response({
        "success": True,
        "message": message,
        "data": data
    }, status=status_code)


def error_response(message="Error", details=None, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({
        "success": False,
        "message": message,
        "details": details
    }, status=status_code)


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve_cart(self, request):
        """ Retrieve the authenticated user's cart. Creates one if it doesn't exist. """
        try:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            serializer = CartSerializer(cart)
            return success_response(serializer.data)
        except Exception as e:
            return error_response("An error occurred while retrieving the cart.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def add_to_cart(self, request):
        product_id = request.data.get('product')
        if not product_id:
            return error_response("Product ID is required.", status_code=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
            cart, _ = Cart.objects.get_or_create(user=request.user)
            serializer = CartItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(cart=cart, product=product)
                return success_response(serializer.data, "Item added to cart.", status_code=status.HTTP_201_CREATED)
            return error_response("Invalid data.", serializer.errors)
        except Product.DoesNotExist:
            return error_response("Product not found.", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while adding item to cart.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update_cart_item(self, request, pk=None):
        try:
            cart_item = CartItem.objects.get(pk=pk, cart__user=request.user)
            serializer = CartItemSerializer(cart_item, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return success_response(serializer.data, "Item updated successfully.")
            return error_response("Invalid data.", serializer.errors)
        except CartItem.DoesNotExist:
            return error_response("Item not found in your cart.", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while updating the item.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def remove_cart_item(self, request, pk=None):
        try:
            cart_item = CartItem.objects.get(pk=pk, cart__user=request.user)
            cart_item.delete()
            return success_response(None, "Item removed from cart.", status_code=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return error_response("Item not found in your cart.", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while removing the item.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def clear_cart(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            CartItem.objects.filter(cart=cart).delete()
            return success_response(None, "Cart cleared successfully.", status_code=status.HTTP_204_NO_CONTENT)
        except Cart.DoesNotExist:
            return error_response("Cart not found.", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while clearing the cart.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
