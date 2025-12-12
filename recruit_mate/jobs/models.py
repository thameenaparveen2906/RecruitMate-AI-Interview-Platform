from django.db import models
from django.conf import settings
from dashboard.models import TimeStampedModel

class JobDescription(TimeStampedModel):
    """Job description model"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_descriptions')
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    skills = models.JSONField(default=list, blank=True)
    location = models.CharField(max_length=255, blank=True)
    employment_type = models.CharField(max_length=50, default='full-time')
    experience_level = models.CharField(max_length=50, blank=True)
    salary_range = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
