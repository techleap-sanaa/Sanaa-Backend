from django.contrib import admin
from .models import AdminUser,User

admin.site.register(AdminUser)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'primary_email', 'phone_number', 'is_creator', 'locked', 'banned', 'two_factor_enabled', 'last_active_at')
    search_fields = ('primary_email', 'first_name', 'last_name', 'phone_number')
    list_filter = ('is_creator', 'locked', 'banned', 'two_factor_enabled')
    readonly_fields = ('user_id', 'created_at', 'updated_at', 'last_active_at')