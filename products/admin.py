from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Category, Product


class ProductAdmin(ModelAdmin):
    list_display = ('name', 'price', 'stock', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')


class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'featured', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('featured', 'created_at', 'updated_at')


# Register your models here
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
