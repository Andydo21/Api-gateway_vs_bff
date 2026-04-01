from django.db import models

class Meeting(models.Model):
    TYPE_CHOICES = [('ZOOM', 'Zoom'), ('GOOGLE_MEET', 'Google Meet')]
    STATUS_CHOICES = [('ONGOING', 'Ongoing'), ('ENDED', 'Ended')]
    
    booking_id = models.BigIntegerField() # Linked to PitchBooking in booking-service
    meeting_url = models.URLField(max_length=500)
    meeting_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ONGOING')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'meetings'

class MeetingOutboxEvent(models.Model):
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'meeting_outbox_events'
        ordering = ['created_at']


class ProcessedMessage(models.Model):
    message_id = models.CharField(max_length=255, unique=True)
    processed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'processed_messages'

    def __str__(self):
        return self.message_id
