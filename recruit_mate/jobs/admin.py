from django.contrib import admin
from .models import JobDescription

@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'location', 'employment_type', 'is_active', 'created_at']
    list_filter = ['is_active', 'employment_type', 'created_at']
    search_fields = ['title', 'description', 'user__email']
    ordering = ['-created_at']
