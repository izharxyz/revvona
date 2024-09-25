from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Cart, CartItem


class CartItemInline(TabularInline):
    model = CartItem
    extra = 0  # No extra empty forms by default
    can_delete = True  # Allow deletion of cart items in admin


class CartAdmin(ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username',)  # Search by username
    inlines = [CartItemInline]
    # Makes timestamps read-only in admin
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(Cart, CartAdmin)
