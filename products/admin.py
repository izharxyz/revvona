from django.contrib import admin
from django.db import models
from unfold.admin import ModelAdmin, TabularInline

from .models import Category, Product, Review


class ReviewInline(TabularInline):
    model = Review
    extra = 0
    can_delete = True
    readonly_fields = ('user', 'product', 'rating',
                       'comment', 'created_at', 'updated_at')
    fields = ('user', 'product', 'rating',
              'comment', 'created_at', 'updated_at')
    show_change_link = True


class ProductAdmin(ModelAdmin):
    list_display = ('name', 'price', 'stock', 'average_rating',
                    'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    # Ensures the average_rating is displayed as read-only
    readonly_fields = ('average_rating',)
    inlines = [ReviewInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Include the average_rating in the queryset
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


# Register your models here
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
