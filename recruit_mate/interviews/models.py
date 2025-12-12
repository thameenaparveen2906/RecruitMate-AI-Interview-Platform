from django.db import models
from django.conf import settings
from dashboard.models import TimeStampedModel
import uuid

class InterviewSession(TimeStampedModel):
    """Interview session model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interview_sessions')
    job = models.ForeignKey('jobs.JobDescription', on_delete=models.CASCADE, related_name='interview_sessions')
    candidate = models.ForeignKey('candidates.Candidate', on_delete=models.CASCADE, related_name='interview_sessions', null=True, blank=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    master_token = models.UUIDField(null=True, blank=True)  # Links candidate sessions to master session
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    # For anonymous candidates (when link is shared publicly)
    candidate_name = models.CharField(max_length=255, blank=True)
    candidate_email = models.EmailField(blank=True)
    candidate_phone = models.CharField(max_length=20, blank=True)
    candidate_resume_url = models.URLField(blank=True)
    candidate_resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.candidate:
            return f"{self.candidate.name} - {self.job.title}"
        elif self.candidate_name:
            return f"{self.candidate_name} - {self.job.title}"
        return f"Interview - {self.job.title}"

class InterviewQuestion(TimeStampedModel):
    """Interview question model"""
    QUESTION_TYPES = [
        ('technical', 'Technical'),
        ('behavioral', 'Behavioral'),
        ('situational', 'Situational'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS)
    expected_key_points = models.JSONField(default=list)
    order = models.IntegerField(default=0)
    is_mandatory = models.BooleanField(default=False)
    is_custom = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"

class InterviewAnswer(TimeStampedModel):
    """Interview answer model"""
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(InterviewQuestion, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    score = models.IntegerField(default=0)
    feedback = models.TextField(blank=True)
    strengths = models.JSONField(default=list)
    improvements = models.JSONField(default=list)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Answer to {self.question.question_text[:30]}"

class InterviewResult(TimeStampedModel):
    """Interview result model"""
    session = models.OneToOneField(InterviewSession, on_delete=models.CASCADE, related_name='result')
    overall_score = models.IntegerField()
    summary = models.TextField()
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    recommendation = models.CharField(max_length=20)
    detailed_feedback = models.TextField()
    
    def __str__(self):
        return f"Result for {self.session}"
