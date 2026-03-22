"""Product Service Models"""
from django.db import models


class Category(models.Model):
    """Product categories"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'startup_categories'
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name


class Startup(models.Model):
    """Startups"""
    user_id = models.IntegerField(null=True, blank=True) # Startup Owner
    company_name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    industry = models.CharField(max_length=100, blank=True, null=True) # AI, Fintech...
    website = models.URLField(max_length=255, blank=True, null=True)
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='startups')
    image_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'startups'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.company_name


class Investor(models.Model):
    """Investor profiles"""
    user_id = models.IntegerField(unique=True)
    company_name = models.CharField(max_length=255)
    bio = models.TextField()
    interests = models.CharField(max_length=255, blank=True, null=True) # comma separated
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'investors'
    
    def __str__(self):
        return self.company_name


class Review(models.Model):
    """Startup reviews"""
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='reviews')
    user_id = models.IntegerField()
    username = models.CharField(max_length=255, default='Khách hàng')  # Store username for display
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.startup.company_name} by User {self.user_id}"


class StartupOutboxEvent(models.Model):
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'startup_outbox_events'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.event_type} - {self.processed}"
