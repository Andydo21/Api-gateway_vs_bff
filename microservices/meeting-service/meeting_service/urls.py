from django.urls import path, include

urlpatterns = [
    path('api/', include('meeting_app.urls')),
    path('', include('meeting_app.urls')),
 # Fallback for health check
]
