from django.db import models

class EventResource(models.Model):
    """Event resources (Demo booths, equipment)"""
    startup_id = models.BigIntegerField(unique=True)
    startup_name = models.CharField(max_length=255)
    available_quantity = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10) # Minimum stock alert
    last_restocked = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'event_resources'
        verbose_name_plural = 'Event Resources'
    
    def __str__(self):
        return f"{self.startup_name} - Available: {self.available_quantity}"
    
    @property
    def total_quantity(self):
        return self.available_quantity + self.reserved_quantity
    
    @property
    def needs_restock(self):
        return self.available_quantity <= self.reorder_level


class ResourceReservation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('released', 'Released'),
        ('fulfilled', 'Fulfilled'),
        ('expired', 'Expired'),
    ]
    
    resource = models.ForeignKey(EventResource, related_name='reservations', on_delete=models.CASCADE)
    booking_id = models.BigIntegerField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resource_reservations'
    
    def __str__(self):
        return f"Reservation for Booking #{self.booking_id} - {self.quantity} units"


class ResourceOutboxEvent(models.Model):
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'resource_outbox_events'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.event_type} - {self.id} (Processed: {self.processed})"
