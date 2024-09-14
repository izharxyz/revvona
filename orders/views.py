from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Address
from cart.models import CartItem

from .models import Order, OrderItem, Payment
from .serializers import (OrderItemSerializer, OrderSerializer,
                          PaymentSerializer)

# Order Views


class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        cart_items = CartItem.objects.filter(cart__user=user)
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        # Use the address provided by the user
        shipping_address_id = request.data.get('shipping_address')
        billing_address_id = request.data.get('billing_address', None)

        try:
            shipping_address = Address.objects.get(
                id=shipping_address_id, user=user)
            billing_address = Address.objects.get(
                id=billing_address_id, user=user) if billing_address_id else None
        except Address.DoesNotExist:
            return Response({'error': 'Invalid address'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            billing_address=billing_address,
            # total_price is nullable, and will be calculated via signals
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                # price is nullable, so it will be calculated on save()
            )

        # Clear the user's cart
        cart_items.delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # Only authenticated users can view order details
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # User can only view their own orders
        return Order.objects.filter(user=self.request.user)


class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # Only authenticated users can view their orders
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # User can only view their own orders
        return Order.objects.filter(user=self.request.user)


class OrderUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# Payment Views


class PaymentCreateView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        order_id = request.data.get('order')

        try:
            order = Order.objects.get(id=order_id, user=user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)

        if Payment.objects.filter(order=order).exists():
            return Response({'error': 'Payment already exists for this order'}, status=status.HTTP_400_BAD_REQUEST)

        amount = order.total_price
        payment_method = request.data.get('method')

        payment = Payment.objects.create(
            order=order,
            method='cod',  # razorpay will be used in the future
            amount=amount,
        )

        # Update order status after successful payment (assuming automatic completion for demo)
        order.status = 'confirmed'
        order.save()

        serializer = self.get_serializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaymentDetailView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # User can only view their own payments
        return Payment.objects.filter(order__user=self.request.user)
