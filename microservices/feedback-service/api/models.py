from django.db import models

class Feedback(models.Model):
    booking_id = models.BigIntegerField()
    investor_id = models.BigIntegerField()
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'feedbacks'

class InvestmentInterest(models.Model):
    STATUS_CHOICES = [
        ('INTERESTED', 'Interested'),
        ('NOT_INTERESTED', 'Not Interested'),
        ('FOLLOW_UP', 'Follow Up'),
    ]
    booking_id = models.BigIntegerField()
    investor_id = models.BigIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'investment_interests'

class FeedbackOutboxEvent(models.Model):
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'feedback_outbox_events'
        ordering = ['created_at']
