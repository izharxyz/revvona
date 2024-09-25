import razorpay
from django.conf import settings
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
            return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        # Use the address provided by the user
        shipping_address_id = request.data.get('shipping_address')
        billing_address_id = request.data.get('billing_address', None)

        try:
            shipping_address = Address.objects.get(
                id=shipping_address_id, user=user)
            billing_address = Address.objects.get(
                id=billing_address_id, user=user) if billing_address_id else None
        except Address.DoesNotExist:
            return Response({'detail': 'Invalid address'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total price of all cart items
        total_price = 0
        for item in cart_items:
            total_price += item.product.price * item.quantity

        # Create the order
        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            billing_address=billing_address,
            total_price=total_price,
        )

        # Create order items and assign prices
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
            )

        # Clear the user's cart after the order is created
        cart_items.delete()

        # Serialize the order and return the response
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
        payment_method = request.data.get('method')

        try:
            order = Order.objects.get(id=order_id, user=user)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)

        if Payment.objects.filter(order=order).exists():
            return Response({'detail': 'Payment already exists for this order'}, status=status.HTTP_400_BAD_REQUEST)

        amount = order.total_price

        # If payment method is Cash on Delivery (COD)
        if payment_method == 'cod':
            payment = Payment.objects.create(
                order=order,
                method='cod',
                amount=amount,
            )
            # Mark the order as confirmed for COD
            order.status = 'confirmed'
            order.save()

            serializer = self.get_serializer(payment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # If payment method is Razorpay
        elif payment_method == 'razorpay':
            client = razorpay.Client(
                auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

            # Create a Razorpay order
            razorpay_order = client.order.create({
                # Razorpay expects amount in paise
                'amount': int(amount) * 100,
                'currency': 'INR',
                'payment_capture': 1  # auto-capture payment
            })

            payment = Payment.objects.create(
                order=order,
                method='razorpay',
                amount=amount,
                # Store Razorpay order ID
                razorpay_order_id=razorpay_order['id'],
            )

            serializer = self.get_serializer(payment)
            return Response({
                'payment': serializer.data,
                'razorpay_order_id': razorpay_order['id'],
                'amount': amount
            }, status=status.HTTP_201_CREATED)

        return Response({'detail': 'Invalid payment method'}, status=status.HTTP_400_BAD_REQUEST)


class PaymentVerifyView(generics.UpdateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature')

        try:
            payment = Payment.objects.get(
                razorpay_order_id=razorpay_order_id, order__user=request.user)
        except Payment.DoesNotExist:
            return Response({'detail': 'Payment not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)

        client = razorpay.Client(
            auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

        # Verify the payment signature
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
            })
        except razorpay.errors.SignatureVerificationError:
            return Response({'detail': 'Payment signature verification failed'}, status=status.HTTP_400_BAD_REQUEST)

        # If verification succeeds, mark the payment as complete
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = 'confirmed'
        payment.save()

        payment.order.status = 'confirmed'
        payment.order.save()

        return Response({'detail': 'Payment successful'}, status=status.HTTP_200_OK)


class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Get order_id from the URL parameters
        order_id = self.kwargs['order_id']

        # Check if the order exists and is owned by the user
        order = Order.objects.filter(
            id=order_id, user=self.request.user).first()

        if not order:
            return Response({'detail': 'Order not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)

        # Fetch the payment related to the order
        payment = Payment.objects.filter(order=order).first()

        if not payment:
            return Response({'detail': 'Payment not found for this order'}, status=status.HTTP_404_NOT_FOUND)

        return payment

    def retrieve(self, request, *args, **kwargs):
        payment = self.get_object()

        # If the get_object method returns a Response, it means there was an error
        if isinstance(payment, Response):
            return payment

        serializer = self.get_serializer(payment)
        return Response(serializer.data)
