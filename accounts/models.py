from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class Address(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)
    user = models.ForeignKey(User, related_name="address",
                             on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.CharField(max_length=10, validators=[
                                    RegexValidator(r'^\+?1?\d{9,15}$')], null=False, blank=False)
    pin_code = models.CharField(max_length=6, validators=[
                                RegexValidator(r'^\d{0,9}$')], null=False, blank=False)
    street = models.CharField(max_length=300, null=False, blank=False)
    landmark = models.CharField(max_length=120, null=False, blank=False)
    city = models.CharField(max_length=120, null=False, blank=False)
    state = models.CharField(max_length=120, null=False, blank=False)

    def __str__(self):
        return self.name
