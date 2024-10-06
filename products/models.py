import cloudinary
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    description = models.TextField(null=False, blank=False)
    quote = models.CharField(max_length=200, null=False, blank=False)
    image = models.ImageField(upload_to='categories/', null=False, blank=False)
    featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        # Delete the image from Cloudinary
        if self.image:
            cloudinary.uploader.destroy(self.image.name)
        super().delete(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=200, blank=False, null=False)
    slug = models.SlugField(unique=True, null=True, blank=True)
    description = models.CharField(max_length=200, null=False, blank=False)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    detail = models.TextField(null=False, blank=False)
    discount = models.PositiveIntegerField(blank=True, null=True, validators=[
                                           MinValueValidator(0), MaxValueValidator(100)])
    stock = models.IntegerField(default=1)
    category = models.ForeignKey(
        'Category', related_name='products', on_delete=models.SET_NULL, null=True)

    average_rating = models.DecimalField(
        max_digits=2, decimal_places=1, default=0.0, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def total_reviews(self):
        return self.reviews.count()

    def update_average_rating(self):
        avg_rating = self.reviews.aggregate(average=Avg('rating'))['average']
        if avg_rating is not None:
            self.average_rating = avg_rating
        else:
            self.average_rating = 0.0  # Default to 0 if no reviews exist
        self.save(update_fields=['average_rating'])


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
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}/5)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Ensure product has been saved before updating the average rating
        if self.product.pk:
            self.product.update_average_rating()

    def delete(self, *args, **kwargs):
        product = self.product  # Save reference to product before deleting the review
        super().delete(*args, **kwargs)
        # Ensure product has been saved before updating the average rating
        if product.pk:
            product.update_average_rating()
