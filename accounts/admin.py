from django.contrib import admin

from .models import Address


class AddressAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'phone_number', 'pin_code',
                    'city', 'state', 'created_at', 'updated_at')
    search_fields = ('name', 'user__username', 'phone_number',
                     'pin_code', 'city', 'state')
    list_filter = ('name', 'phone_number', 'city', 'state', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(Address, AddressAdmin)
