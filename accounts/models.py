from django.contrib.auth.models import User
from django.db import models


class Address(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)
    user = models.ForeignKey(User, related_name="address",
                             on_delete=models.CASCADE, null=True, blank=True)

    # Phone number max length set to 13 to accommodate formatting (e.g., +91XXXXXXXXXX)
    # This is India specific, you may need to adjust based on your country's phone number format
    phone_number = models.CharField(max_length=13, null=False, blank=False)
    pin_code = models.CharField(max_length=6, null=False, blank=False)

    street = models.CharField(max_length=300, null=False, blank=False)
    landmark = models.CharField(max_length=120, null=False, blank=False)
    city = models.CharField(max_length=120, null=False, blank=False)
    state = models.CharField(max_length=120, null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
