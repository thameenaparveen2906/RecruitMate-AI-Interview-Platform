from django.urls import path
from . import api_views

app_name = 'candidates_api'

urlpatterns = [
    path('', api_views.CandidateListCreateAPIView.as_view(), name='list-create'),
    path('<int:pk>/', api_views.CandidateDetailAPIView.as_view(), name='detail'),
]
