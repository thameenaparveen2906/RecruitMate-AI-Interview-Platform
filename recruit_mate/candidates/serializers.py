from rest_framework import serializers
from .models import Candidate

class CandidateSerializer(serializers.ModelSerializer):
    resume_file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'email', 'phone', 'resume_url', 'resume_file', 'resume_file_url',
                  'resume_data', 'skills', 'experience_years', 'education', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'resume_file_url']
    
    def get_resume_file_url(self, obj):
        if obj.resume_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.resume_file.url)
            return obj.resume_file.url
        return None