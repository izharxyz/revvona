from django.contrib import admin

from .models import Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # Number of empty forms to display


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'shipping_address',
                    'billing_address', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__username', 'shipping_address__street',
                     'billing_address__street')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('user', 'total_price', 'shipping_address', 'billing_address', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'method', 'amount',
                    'payment_status', 'created_at')
    list_filter = ('method', 'payment_status', 'created_at')
    search_fields = ('order__id', 'order__user__username')
    readonly_fields = ('created_at',)

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
