from django.contrib import admin
from .models import Address


class AddressModelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "phone_number",
                    "pin_code", "street", "landmark", "city", "state")


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "card_number", "address", "ordered_item",
                    "paid_status", "paid_at", "total_price", "is_delivered", "delivered_at", "user")


admin.site.register(Address, AddressModelAdmin)
