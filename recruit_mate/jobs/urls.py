from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list_view, name='lists'),
    path('create/', views.job_create_view, name='create'),
    path('<int:pk>/', views.job_detail_view, name='detail'),
    path('<int:pk>/edit/', views.job_edit_view, name='edit'),
    path('<int:pk>/delete/', views.job_delete_view, name='delete'),
]
