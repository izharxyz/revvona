from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0  # No extra empty forms by default
    can_delete = True  # Allow deletion of cart items in admin


class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username',)  # Search by username
    inlines = [CartItemInline]
    # Makes timestamps read-only in admin
    readonly_fields = ('created_at', 'updated_at')


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    list_filter = ('cart__user', 'product')  # Filter by user and product
    search_fields = ('product__name',)  # Search by product name
    # Makes cart and product read-only in admin
    readonly_fields = ('cart', 'product')


# Register models with admin site
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
