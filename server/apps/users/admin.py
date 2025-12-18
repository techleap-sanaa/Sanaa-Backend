from django.contrib import admin
from .models import  TenantUser,AdminUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
class Administrator(BaseUserAdmin):
    list_display = ('first_name', 'last_name')

class TenantUserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'primary_email', 'phone_number', 'is_creator', 'locked', 'banned', 'two_factor_enabled', 'last_active_at')
    search_fields = ('primary_email', 'first_name', 'last_name', 'phone_number')
    list_filter = ('is_creator', 'locked', 'banned', 'two_factor_enabled')
    readonly_fields = ('created_at', 'updated_at', 'last_active_at')

admin.site.register(AdminUser,Administrator)
admin.site.register(TenantUser,TenantUserAdmin)