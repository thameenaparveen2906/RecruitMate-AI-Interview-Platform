from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import InterviewSession, InterviewAnswer
from .serializers import InterviewSessionSerializer, InterviewAnswerSerializer

class InterviewSessionListCreateAPIView(generics.ListCreateAPIView):
    """API view for listing and creating interview sessions"""
    serializer_class = InterviewSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return InterviewSession.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class InterviewSessionDetailAPIView(generics.RetrieveAPIView):
    """API view for interview session detail"""
    serializer_class = InterviewSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return InterviewSession.objects.filter(user=self.request.user)

class InterviewStartAPIView(APIView):
    """API view to start interview"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, token):
        try:
            session = InterviewSession.objects.get(token=token)
            if session.status == 'pending':
                session.status = 'in_progress'
                session.save()
            return Response({'status': 'started'})
        except InterviewSession.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_404_NOT_FOUND)

class InterviewAnswerAPIView(APIView):
    """API view to submit answer"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, token):
        try:
            session = InterviewSession.objects.get(token=token)
            serializer = InterviewAnswerSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(session=session)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except InterviewSession.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_404_NOT_FOUND)