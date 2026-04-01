"""User Service Models"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Extended User model"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('investor', 'Investor'),
        ('founder', 'Founder'),
        ('user', 'User'),
    ]
    
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    banned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.email




class UserOutboxEvent(models.Model):
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'user_outbox_events'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.event_type} - {self.id} (Processed: {self.processed})"


class ProcessedMessage(models.Model):
    message_id = models.CharField(max_length=255, unique=True)
    processed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'processed_messages'

    def __str__(self):
        return self.message_id
