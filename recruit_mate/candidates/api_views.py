from rest_framework import generics, permissions
from .models import Candidate
from .serializers import CandidateSerializer

class CandidateListCreateAPIView(generics.ListCreateAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [permissions.IsAuthenticated]

class CandidateDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [permissions.IsAuthenticated]
