from django.urls import path, include

urlpatterns = [
    path('web/', include('api.urls')),
    path('api/v1/', include('api.legacy_urls')),
]
