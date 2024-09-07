from django.contrib import admin
from .models import Address


class AddressModelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "phone_number",
                    "pin_code", "street", "landmark", "city", "state")

admin.site.register(Address, AddressModelAdmin)
