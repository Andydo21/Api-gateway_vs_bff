from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home_page, name='home'),
    path('startups/<int:startup_id>/', views.startup_detail, name='startup_detail'),
    path('startups/<int:startup_id>/approve/', views.approve_startup, name='approve_startup'),
    path('startups/<int:startup_id>/reject/', views.reject_startup, name='reject_startup'),
    
    # Investor
    path('investor/profile/', views.investor_profile, name='investor_profile'),
    
    # Pitching
    path('pitch/submit/', views.submit_pitch_request, name='submit_pitch'),
    path('pitch/list/', views.list_pitch_requests, name='list_pitch_requests'),
    path('pitch/<int:request_id>/approve/', views.approve_pitch_request, name='approve_pitch'),
    path('pitch/<int:request_id>/reject/', views.reject_pitch_request, name='reject_pitch'),
    path('slots/', views.list_pitch_slots, name='list_slots'),
    path('slots/<int:slot_id>/book/', views.book_pitch_slot, name='book_slot'),
    path('availability-templates/', views.list_create_availability_templates, name='availability_templates'),
    path('meetings/', views.list_meetings, name='list_meetings'),
    path('feedback/submit/', views.submit_feedback, name='submit_feedback'),
]
