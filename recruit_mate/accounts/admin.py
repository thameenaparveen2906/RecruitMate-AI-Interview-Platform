from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'company', 'is_staff', 'created_at']
    list_filter = ['is_staff', 'is_active', 'created_at']
    search_fields = ['email', 'username', 'company']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('company', 'phone')}),
    )
