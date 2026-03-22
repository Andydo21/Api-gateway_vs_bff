from django.db import models

class UserInteraction(models.Model):
    INTERACTION_TYPES = [
        ('view', 'View'),
        ('click', 'Click'),
        ('pitch_request', 'Pitch Request'),
        ('like', 'Like'),
        ('review', 'Review'),
    ]
    
    user_id = models.BigIntegerField()
    startup_id = models.BigIntegerField()
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    weight = models.FloatField(default=1.0)  # Weight for recommendation algorithm
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_interactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', 'startup_id']),
            models.Index(fields=['user_id', 'created_at']),
        ]
    
    def __str__(self):
        return f"User #{self.user_id} - {self.interaction_type} - Startup #{self.startup_id}"


class StartupSimilarity(models.Model):
    """Pre-computed startup similarities for faster recommendations"""
    startup_id = models.BigIntegerField()
    similar_startup_id = models.BigIntegerField()
    similarity_score = models.FloatField()  # 0-1
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'startup_similarities'
        unique_together = ['startup_id', 'similar_startup_id']
        ordering = ['-similarity_score']
    
    def __str__(self):
        return f"Startup #{self.startup_id} similar to #{self.similar_startup_id} ({self.similarity_score})"


class MatchmakingOutboxEvent(models.Model):
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'matchmaking_outbox_events'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.event_type} - {self.id} (Processed: {self.processed})"
