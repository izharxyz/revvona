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


# Register models with admin site
admin.site.register(Cart, CartAdmin)
