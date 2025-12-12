from django.contrib import admin
from .models import InterviewSession, InterviewQuestion, InterviewAnswer, InterviewResult

@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'job', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['candidate__name', 'candidate__email', 'job__title']
    ordering = ['-created_at']

@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ['session', 'question_type', 'difficulty', 'order']
    list_filter = ['question_type', 'difficulty']
    search_fields = ['question_text']

@admin.register(InterviewAnswer)
class InterviewAnswerAdmin(admin.ModelAdmin):
    list_display = ['session', 'question', 'score', 'created_at']
    list_filter = ['score', 'created_at']
    search_fields = ['answer_text']

@admin.register(InterviewResult)
class InterviewResultAdmin(admin.ModelAdmin):
    list_display = ['session', 'overall_score', 'recommendation', 'created_at']
    list_filter = ['recommendation', 'overall_score']
    search_fields = ['summary']

