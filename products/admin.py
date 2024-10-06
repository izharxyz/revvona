import uuid

from django.contrib import admin
from django.db import models
from django.db.models import Avg
from django.utils.text import slugify
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.forms.widgets import WysiwygWidget

from .models import Category, Image, Product, Review


class ImageInline(TabularInline):
    model = Image
    extra = 0
    can_delete = True
    fields = ('image',)
    show_change_link = True
    hide_title = True


class ReviewInline(TabularInline):
    model = Review
    extra = 0
    can_delete = True
    readonly_fields = ('created_at', 'updated_at')
    fields = ('user', 'product', 'rating',
              'comment')
    show_change_link = True


class ProductAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'price', 'stock',
                    'average_rating_display', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'slug')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('average_rating',)
    inlines = [ImageInline, ReviewInline]

    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'detail', 'price', 'discount', 'stock', 'category', 'average_rating')
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Rename the annotated field to avoid conflict with the 'average_rating' model field
        queryset = queryset.annotate(avg_review_rating=Avg('reviews__rating'))
        return queryset

    def average_rating_display(self, obj):
        # Access the annotated field for the display
        return round(obj.avg_review_rating, 1) if obj.avg_review_rating else 'N/A'
    average_rating_display.short_description = 'Avg Rating'

    def save_model(self, request, obj, form, change):
        # Auto-generate the slug if it's not provided
        if not obj.slug:
            obj.slug = slugify(obj.name)

        # Ensure the slug is unique
        original_slug = obj.slug
        queryset = self.model.objects.filter(
            slug=original_slug).exclude(pk=obj.pk)
        counter = 1

        # Keep appending a short UUID until the slug is unique
        while queryset.exists():
            obj.slug = f"{original_slug}-{uuid.uuid4().hex[:6]}"
            queryset = self.model.objects.filter(
                slug=obj.slug).exclude(pk=obj.pk)
            counter += 1

        super().save_model(request, obj, form, change)


class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'featured', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'slug')
    list_filter = ('featured', 'created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'quote', 'image', 'featured')
        }),
    )

    def save_model(self, request, obj, form, change):
        # Auto-generate the slug if it's not provided
        if not obj.slug:
            obj.slug = slugify(obj.name)

        # Ensure the slug is unique
        original_slug = obj.slug
        queryset = self.model.objects.filter(
            slug=original_slug).exclude(pk=obj.pk)
        counter = 1

        # Keep appending a short UUID until the slug is unique
        while queryset.exists():
            obj.slug = f"{original_slug}-{uuid.uuid4().hex[:6]}"
            queryset = self.model.objects.filter(
                slug=obj.slug).exclude(pk=obj.pk)
            counter += 1

        super().save_model(request, obj, form, change)


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
