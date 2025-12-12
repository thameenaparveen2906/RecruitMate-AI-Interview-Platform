from rest_framework import serializers
from .models import InterviewSession, InterviewQuestion, InterviewAnswer, InterviewResult

class InterviewQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewQuestion
        fields = ['id', 'question_text', 'question_type', 'difficulty', 'expected_key_points', 'order']

class InterviewAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewAnswer
        fields = ['id', 'question', 'answer_text', 'score', 'feedback', 'strengths', 'improvements', 'created_at']
        read_only_fields = ['score', 'feedback', 'strengths', 'improvements']

class InterviewResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewResult
        fields = ['overall_score', 'summary', 'strengths', 'weaknesses', 'recommendation', 'detailed_feedback']

class InterviewSessionSerializer(serializers.ModelSerializer):
    questions = InterviewQuestionSerializer(many=True, read_only=True)
    answers = InterviewAnswerSerializer(many=True, read_only=True)
    result = InterviewResultSerializer(read_only=True)
    
    class Meta:
        model = InterviewSession
        fields = ['id', 'job', 'candidate', 'token', 'status', 'started_at', 
                  'completed_at', 'expires_at', 'questions', 'answers', 'result', 'created_at']
        read_only_fields = ['token', 'created_at']