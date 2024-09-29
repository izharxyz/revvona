import cloudinary
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

    def delete(self, *args, **kwargs):
        # Delete the image from Cloudinary
        if self.image:
            cloudinary.uploader.destroy(self.image.name)
        super().delete(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=200, blank=False, null=False)
    description = models.TextField(null=False, blank=False)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    discount = models.PositiveIntegerField(blank=True, null=True, validators=[
                                           MinValueValidator(0), MaxValueValidator(100)])
    stock = models.IntegerField(default=1)
    category = models.ForeignKey(
        'Category', related_name='products', on_delete=models.SET_NULL, null=True)

    average_rating_value = models.DecimalField(
        max_digits=2, decimal_places=1, default=0.0, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        return self.average_rating_value

    @average_rating.setter
    def average_rating(self, value):
        self.average_rating_value = round(value, 1) if value else 0.0

    @property
    def total_reviews(self):
        return self.reviews.aggregate(count=Count('id'))['count']

    def calculate_average_rating(self):
        # Calculate average rating only if the product already has an ID (i.e., it's been saved)
        if self.pk:
            reviews = self.reviews.aggregate(average=Avg('rating'))
            average = reviews['average']
            self.average_rating = average if average else 0.0

    def save(self, *args, **kwargs):
        # Calculate average rating before saving
        self.calculate_average_rating()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the images associated with the product
        for image in self.images.all():
            image.delete()
        super().delete(*args, **kwargs)


class Image(models.Model):
    product = models.ForeignKey(
        Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', null=False, blank=False)

    def __str__(self):
        return self.product.name

    def delete(self, *args, **kwargs):
        # Delete the image from Cloudinary
        if self.image:
            cloudinary.uploader.destroy(self.image.name)
        super().delete(*args, **kwargs)


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
