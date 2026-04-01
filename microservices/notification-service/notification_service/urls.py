from django.urls import path, include

urlpatterns = [
    path('api/notifications/', include('notification_app.urls')),

]
