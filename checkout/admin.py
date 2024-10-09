from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Order, OrderItem, Payment


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0  # Number of empty forms to display
    can_delete = True  # Allow deletion of order items in admin


class OrderAdmin(ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'delivery_charge', 'shipping_address',
                    'billing_address', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__username', 'shipping_address__street',
                     'billing_address__street')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('user', 'total_price', 'delivery_charge', 'shipping_address', 'billing_address', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


class PaymentAdmin(ModelAdmin):
    list_display = ('id', 'order', 'method', 'amount',
                    'payment_status', 'created_at')
    list_filter = ('method', 'payment_status', 'created_at')
    search_fields = ('order__id', 'order__user__username')
    readonly_fields = ('razorpay_order_id', 'razorpay_payment_id',
                       'razorpay_signature', 'created_at')

    fieldsets = (
        (None, {
            'fields': ('order', 'method', 'amount', 'payment_status')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
