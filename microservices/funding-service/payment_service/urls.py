from django.urls import path, include

urlpatterns = [
    path('', include('funding_app.urls')),

]
