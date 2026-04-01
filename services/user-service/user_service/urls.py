from django.urls import path, include

urlpatterns = [
    path('', include('user_app.urls')),

]
