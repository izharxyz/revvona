from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order, OrderItem


@receiver(post_save, sender=Order)
def calculate_order_total(sender, instance, **kwargs):
    if instance.total_price == 0 or instance.total_price is None:  # Only calculate if total_price is None
        total = sum(item.price * item.quantity for item in instance.items.all())
        instance.total_price = total
        instance.save(update_fields=['total_price'])
