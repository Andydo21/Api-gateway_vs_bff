from django.urls import path, include

urlpatterns = [
    path('', include('matchmaking_app.urls')),

]
