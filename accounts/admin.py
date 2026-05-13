from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin panel for Eventify users.
    """
    list_display = ['username', 'email', 'role', 'phone', 'is_active', 'created_at']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'email', 'phone']
    ordering = ['-created_at']

    fieldsets = UserAdmin.fieldsets + (
        ('Eventify Info', {
            'fields': ('role', 'phone', 'profile_picture')
        }),
    )