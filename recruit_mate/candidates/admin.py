from django.contrib import admin
from .models import Candidate

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'experience_years', 'created_at']
    list_filter = ['experience_years', 'created_at']
    search_fields = ['name', 'email', 'phone']
    ordering = ['-created_at']
