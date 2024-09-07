from django.db import models

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # This ensures that this model is used only as a base class and won't create its own table


class Category(TimestampedModel):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Product(TimestampedModel):
    name = models.CharField(max_length=200, blank=False, null=False)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.IntegerField(default=1)
    image = models.ImageField(null=True, blank=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
