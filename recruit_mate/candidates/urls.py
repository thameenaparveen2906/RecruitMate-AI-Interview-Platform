from django.urls import path
from . import views

app_name = 'candidates'

urlpatterns = [
    path('', views.candidate_list_view, name='list'),
    path('all/', views.candidates_all_view, name='all'),
    path('profile/<str:email>/', views.candidate_profile_view, name='profile'),
    path('interview/<int:pk>/report/', views.interview_report_view, name='interview_report'),
    path('create/', views.candidate_create_view, name='create'),
    path('<int:pk>/', views.candidate_detail_view, name='detail'),
    path('<int:pk>/edit/', views.candidate_edit_view, name='edit'),
    path('<int:pk>/delete/', views.candidate_delete_view, name='delete'),
]