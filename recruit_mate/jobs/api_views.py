from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import JobDescription
from .serializers import JobDescriptionSerializer

class JobListCreateAPIView(generics.ListCreateAPIView):
    """API view for listing and creating jobs"""
    serializer_class = JobDescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return JobDescription.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class JobDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API view for job detail, update, delete"""
    serializer_class = JobDescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return JobDescription.objects.filter(user=self.request.user)