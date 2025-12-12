from django.urls import path
from . import api_views

app_name = 'jobs_api'

urlpatterns = [
    path('', api_views.JobListCreateAPIView.as_view(), name='list-create'),
    path('<int:pk>/', api_views.JobDetailAPIView.as_view(), name='detail'),
]
