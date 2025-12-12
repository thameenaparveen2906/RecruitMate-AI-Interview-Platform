from django.db import models
from dashboard.models import TimeStampedModel

class Candidate(TimeStampedModel):
    """Candidate model"""
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    resume_url = models.URLField(blank=True)
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    resume_data = models.JSONField(default=dict, blank=True)
    skills = models.JSONField(default=list, blank=True)
    experience_years = models.IntegerField(null=True, blank=True)
    education = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.email})"
