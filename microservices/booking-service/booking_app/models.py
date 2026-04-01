from django.db import models

class PitchRequest(models.Model):
    """Formal application for pitching"""
    STATUS_CHOICES = [
        ('REGISTERED', 'Registered'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
    ]
    
    startup_id = models.BigIntegerField()
    title = models.CharField(max_length=255)
    pitch_deck_url = models.URLField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REGISTERED')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pitch_requests'

class PitchBooking(models.Model):
    STATUS_CHOICES = [
        ('INITIALIZED', 'Initialized'),
        ('SCHEDULED', 'Scheduled'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    pitch_request = models.ForeignKey(PitchRequest, on_delete=models.CASCADE)
    pitch_slot_id = models.BigIntegerField() # Linked to PitchSlot in scheduling-service
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='INITIALIZED')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pitch_bookings'

class Waitlist(models.Model):
    pitch_request = models.ForeignKey(PitchRequest, on_delete=models.CASCADE)
    pitch_slot_id = models.BigIntegerField()
    investor_id = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'waitlists'

class PitchBookingHistory(models.Model):
    ACTION_CHOICES = [('RESCHEDULE', 'Reschedule'), ('CANCEL', 'Cancel')]
    booking = models.ForeignKey(PitchBooking, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    old_slot_id = models.BigIntegerField(null=True)
    new_slot_id = models.BigIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pitch_booking_history'

class BookingOutboxEvent(models.Model):
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'booking_outbox_events'
        ordering = ['created_at']


class ProcessedMessage(models.Model):
    message_id = models.CharField(max_length=255, unique=True)
    processed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'processed_messages'

    def __str__(self):
        return self.message_id
