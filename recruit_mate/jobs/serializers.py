from rest_framework import serializers
from .models import JobDescription

class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = ['id', 'title', 'description', 'requirements', 'skills', 
                  'location', 'employment_type', 'experience_level', 
                  'salary_range', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
