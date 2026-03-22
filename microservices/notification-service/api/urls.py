from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.send_notification, name='send-notification'),
    path('list/', views.list_notifications, name='list-notifications'),
    path('<int:pk>/read/', views.mark_as_read, name='mark-as-read'),
]
