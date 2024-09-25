
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from unfold.admin import ModelAdmin

from .models import Address

admin.site.unregister(User)
admin.site.unregister(Group)


class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass


class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


class AddressAdmin(ModelAdmin):
    list_display = ('name', 'user', 'phone_number', 'pin_code',
                    'city', 'state', 'created_at', 'updated_at')
    search_fields = ('name', 'user__username', 'phone_number',
                     'pin_code', 'city', 'state')
    list_filter = ('name', 'phone_number', 'city', 'state', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Address, AddressAdmin)
