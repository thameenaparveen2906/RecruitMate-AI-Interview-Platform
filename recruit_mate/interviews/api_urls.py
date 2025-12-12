from django.urls import path
from . import api_views

app_name = 'interviews_api'

urlpatterns = [
    path('', api_views.InterviewSessionListCreateAPIView.as_view(), name='list-create'),
    path('<int:pk>/', api_views.InterviewSessionDetailAPIView.as_view(), name='detail'),
    path('<uuid:token>/start/', api_views.InterviewStartAPIView.as_view(), name='start'),
    path('<uuid:token>/answer/', api_views.InterviewAnswerAPIView.as_view(), name='answer'),
]