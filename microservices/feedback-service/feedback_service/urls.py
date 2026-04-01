from django.urls import path, include

urlpatterns = [
    path('api/', include('feedback_app.urls')),
    path('', include('feedback_app.urls')),
 # Fallback for health check
]
