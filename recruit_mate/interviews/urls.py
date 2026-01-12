from django.urls import path
from . import views

app_name = 'interviews'

urlpatterns = [
    path('', views.interview_list_view, name='list'),
    path('links/', views.interview_links_view, name='links'),
    path('create/', views.interview_create_view, name='create'),
    path('<int:pk>/', views.interview_detail_view, name='detail'),
    path('<int:pk>/results/', views.interview_results_view, name='results'),
    path('<int:pk>/candidates/', views.interview_candidates_view, name='candidates'),
    path('<int:pk>/toggle-status/', views.interview_toggle_status_view, name='toggle_status'),
    path('<int:pk>/delete/', views.interview_delete_view, name='delete'),
    path('<int:pk>/edit/', views.interview_edit_view, name='edit'),
    path('take/<uuid:token>/', views.interview_take_view, name='take'),
    path("interview/disqualify/", views.disqualify_interview, name="disqualify_interview"),
    path("interview/disqualified/", views.interview_disqualified, name="interview_disqualified"),
]
