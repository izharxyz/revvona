from django.contrib.auth.models import User
from django.db import models

from accounts.models import Address


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User, related_name='orders', on_delete=models.CASCADE)
    # this will be calculated using signals so it can be null
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    shipping_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, related_name='shipping_orders')
    billing_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='billing_orders')
    status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('cod', 'Cash on Delivery'),
        ('razorpay', 'Razorpay'),
    )

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    order = models.OneToOneField(
        Order, related_name='payment', on_delete=models.CASCADE)
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Razorpay payment details
    razorpay_order_id = models.CharField(
        max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(
        max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(
        max_length=255, blank=True, null=True)

    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id}"
