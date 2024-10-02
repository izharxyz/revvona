from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from products.models import Product


class Cart(models.Model):
    user = models.OneToOneField(User, related_name='cart',
                                on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id} - User: {self.user}" if self.user else f"Cart {self.id} - Guest Cart"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        # Ensures the product can't be added multiple times
        unique_together = ('cart', 'product')

    def save(self, *args, **kwargs):
        # Check if this product already exists in the cart
        if CartItem.objects.filter(cart=self.cart, product=self.product).exists() and not self.pk:
            raise ValidationError(
                f"The product '{self.product}' is already in the cart.")

        # Proceed with saving if it's not a duplicate
        super().save(*args, **kwargs)
