from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Count


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    quote = models.CharField(max_length=200, null=False, blank=False)
    image = models.ImageField(upload_to='categories/', null=False, blank=False)
    featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, blank=False, null=False)
    description = models.TextField(null=False, blank=False)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    discount = models.PositiveIntegerField(blank=True, null=True, validators=[
                                           MinValueValidator(0), MaxValueValidator(100)])
    stock = models.IntegerField(default=1)
    image = models.ImageField(upload_to='products/', null=False, blank=False)
    category = models.ForeignKey(
        Category, related_name='products', on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    # Method to calculate the average rating
    @property
    def average_rating(self):
        reviews = self.reviews.aggregate(average=models.Avg('rating'))
        average = reviews['average']
        return round(average, 1) if average else 0.0

    # Method to calculate the total number of reviews
    @property
    def total_reviews(self):
        return self.reviews.aggregate(count=Count('id'))['count']

    # Overriding the save method to store these calculated fields in the model itself
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Optionally, you can precompute and store average ratings and total reviews in the DB


class Review(models.Model):
    product = models.ForeignKey(
        Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensures each user can only leave one review per product
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}/5)"
