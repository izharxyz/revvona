import razorpay
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Address
from cart.models import CartItem
from revvona.utils import CustomPagination, error_response, success_response

from .models import Order, OrderItem, Payment
from .serializers import OrderSerializer, PaymentSerializer


class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create_order(self, request):
        try:
            user = request.user
            cart_items = CartItem.objects.filter(cart__user=user)
            if not cart_items.exists():
                return error_response("Cart is empty", status_code=status.HTTP_400_BAD_REQUEST)

            shipping_address_id = request.data.get('shipping_address')
            billing_address_id = request.data.get('billing_address', None)

            try:
                shipping_address = Address.objects.get(
                    id=shipping_address_id, user=user)
                billing_address = Address.objects.get(
                    id=billing_address_id, user=user) if billing_address_id else None
            except Address.DoesNotExist:
                return error_response("Invalid address", status_code=status.HTTP_400_BAD_REQUEST)

            total_price = sum(item.product.price *
                              item.quantity for item in cart_items)

            # Create the order
            order = Order.objects.create(
                user=user,
                shipping_address=shipping_address,
                billing_address=billing_address,
                total_price=total_price,
            )

            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                )

            cart_items.delete()  # Clear cart after order creation

            serializer = OrderSerializer(order)
            return success_response(serializer.data, "Order created successfully", status_code=status.HTTP_201_CREATED)
        except Exception as e:
            return error_response("An error occurred while creating the order.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list_orders(self, request):
        try:
            orders = Order.objects.filter(user=request.user)
            paginator = CustomPagination()
            paginated_orders = paginator.paginate_queryset(orders, request)

            if paginated_orders is None:
                return error_response("No orders found", status_code=status.HTTP_404_NOT_FOUND)

            serializer = OrderSerializer(paginated_orders, many=True)
            return success_response({
                "orders": serializer.data,
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link()
            }, message="Orders retrieved successfully")

        except Exception as e:
            return error_response("An error occurred while fetching orders.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve_order(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
            serializer = OrderSerializer(order)
            return success_response(serializer.data, "Order details retrieved successfully")
        except Order.DoesNotExist:
            return error_response("Order not found", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while fetching the order.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update_order(self, request, pk=None):
        """Update only the shipping address of an order if it's confirmed."""
        try:
            order = Order.objects.get(pk=pk, user=request.user)

            # Check if the order is already cancelled, delivered, or returned
            if order.status != 'confirmed':
                return error_response("Oreder not eligible for updating", status_code=status.HTTP_400_BAD_REQUEST)

            # Ensure only the shipping address is being updated
            if 'shipping_address' not in request.data or 'billing_address' in request.data:
                return error_response("Only the shipping address can be updated.", status_code=status.HTTP_400_BAD_REQUEST)

            # Update shipping address
            shipping_address_id = request.data.get('shipping_address')
            try:
                shipping_address = Address.objects.get(
                    id=shipping_address_id, user=request.user)
            except Address.DoesNotExist:
                return error_response("Invalid shipping address.", status_code=status.HTTP_404_NOT_FOUND)

            order.shipping_address = shipping_address
            order.save()

            serializer = OrderSerializer(order)
            return success_response(serializer.data, "Shipping address updated successfully.")
        except Order.DoesNotExist:
            return error_response("Order not found.", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while updating the order.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def cancel_order(self, request, pk=None):
        """Cancel an order by setting its status to 'cancelled'."""
        try:
            order = Order.objects.get(pk=pk, user=request.user)

            if order.status != 'confirmed':
                return error_response("Only confirmed orders can be cancelled.", status_code=status.HTTP_400_BAD_REQUEST)

            # Set the order status to 'cancelled'
            order.status = 'cancelled'
            order.save()

            return success_response(None, "Order has been cancelled.", status_code=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return error_response("Order not found.", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while cancelling the order.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def return_order(self, request, pk=None):
        """Return an order by setting its status to 'returned'."""
        try:
            order = Order.objects.get(pk=pk, user=request.user)

            # Check if the order is already returned
            if order.status == 'returned':
                return error_response("Order is already returned.", status_code=status.HTTP_400_BAD_REQUEST)
            if order.status == 'return_initiated':
                return error_response("Order return procedure is already initiated.", status_code=status.HTTP_400_BAD_REQUEST)

            # Check if the order has been delivered before allowing a return
            if order.status != 'delivered':
                return error_response("Only delivered orders can be returned.", status_code=status.HTTP_400_BAD_REQUEST)

            order.status = 'return_initiated'
            order.save()

            return success_response(None, "Order return procedure initiated successfully", status_code=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return error_response("Order not found.", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while returning the order.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create_payment(self, request):
        try:
            user = request.user
            order_id = request.data.get('order')
            payment_method = request.data.get('method')

            if not order_id or not payment_method:
                return error_response("Order ID and payment method (cod or razorpay) are required.", status_code=status.HTTP_400_BAD_REQUEST)

            try:
                order = Order.objects.get(id=order_id, user=user)
                if order.status != 'pending':
                    return error_response("Order not eligible for payment", status_code=status.HTTP_400_BAD_REQUEST)

            except Order.DoesNotExist:
                return error_response("Order not found or unauthorized", status_code=status.HTTP_404_NOT_FOUND)

            if Payment.objects.filter(order=order).exists():
                return error_response("Payment already exists for this order", status_code=status.HTTP_400_BAD_REQUEST)

            amount = order.total_price

            if payment_method == 'cod':
                payment = Payment.objects.create(
                    order=order, method='cod', amount=amount)
                order.status = 'confirmed'
                order.save()
                serializer = PaymentSerializer(payment)
                return success_response(serializer.data, "Payment created successfully", status_code=status.HTTP_201_CREATED)

            elif payment_method == 'razorpay':
                client = razorpay.Client(
                    auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
                razorpay_order = client.order.create({
                    'amount': int(amount) * 100,
                    'currency': 'INR',
                    'payment_capture': 1
                })

                payment = Payment.objects.create(
                    order=order,
                    method='razorpay',
                    amount=amount,
                    razorpay_order_id=razorpay_order['id'],
                )

                serializer = PaymentSerializer(payment)
                return success_response({
                    'payment': serializer.data,
                    'razorpay_order_id': razorpay_order['id'],
                    'amount': amount
                }, "Razorpay payment initiated", status_code=status.HTTP_201_CREATED)

            return error_response("Invalid payment method", status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return error_response("An error occurred while creating the payment.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def verify_payment(self, request):
        try:
            razorpay_order_id = request.data.get('razorpay_order_id')
            razorpay_payment_id = request.data.get('razorpay_payment_id')
            razorpay_signature = request.data.get('razorpay_signature')

            try:
                payment = Payment.objects.get(
                    razorpay_order_id=razorpay_order_id, order__user=request.user)
            except Payment.DoesNotExist:
                return error_response("Payment not found or unauthorized", status_code=status.HTTP_404_NOT_FOUND)

            client = razorpay.Client(
                auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

            try:
                client.utility.verify_payment_signature({
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_signature': razorpay_signature,
                })
            except razorpay.errors.SignatureVerificationError:
                payment.status = 'failed'
                payment.save()
                return error_response("Payment signature verification failed", status_code=status.HTTP_400_BAD_REQUEST)

            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'completed'
            payment.save()

            payment.order.status = 'confirmed'
            payment.order.save()

            return success_response(None, "Payment successful", status_code=status.HTTP_200_OK)
        except Exception as e:
            return error_response("An error occurred during payment verification.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve_payment(self, request, order_id=None):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            payment = Payment.objects.filter(order=order).first()

            if not payment:
                return error_response("Payment not found for this order", status_code=status.HTTP_404_NOT_FOUND)

            serializer = PaymentSerializer(payment)
            return success_response(serializer.data, "Payment details retrieved successfully")
        except Order.DoesNotExist:
            return error_response("Order not found or unauthorized", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while retrieving payment details.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
