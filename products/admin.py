from django.contrib import admin
from django.db import models
from unfold.admin import ModelAdmin, TabularInline

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
    list_display = ('name', 'price', 'stock', 'average_rating',
                    'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('average_rating',)
    inlines = [ImageInline, ReviewInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            average_rating=models.Avg('reviews__rating'))
        return queryset

    def average_rating(self, obj):
        return round(obj.average_rating, 1) if obj.average_rating else 'N/A'
    average_rating.short_description = 'Avg Rating'


class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'featured', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('featured', 'created_at', 'updated_at')


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
