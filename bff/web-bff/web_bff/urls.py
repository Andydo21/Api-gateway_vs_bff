from django.urls import path, include

urlpatterns = [
    path('web/', include('api.urls')),
]
