from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('jobs/', include('jobs.api_urls')),
    path('candidates/', include('candidates.api_urls')),
    path('interviews/', include('interviews.api_urls')),
]
