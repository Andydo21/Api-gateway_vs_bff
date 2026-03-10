from django.db import models

class UserInteraction(models.Model):
    INTERACTION_TYPES = [
        ('view', 'View'),
        ('click', 'Click'),
        ('add_to_cart', 'Add to Cart'),
        ('purchase', 'Purchase'),
        ('like', 'Like'),
        ('review', 'Review'),
    ]
    
    user_id = models.IntegerField()
    product_id = models.IntegerField()
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    weight = models.FloatField(default=1.0)  # Weight for recommendation algorithm
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_interactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', 'product_id']),
            models.Index(fields=['user_id', 'created_at']),
        ]
    
    def __str__(self):
        return f"User #{self.user_id} - {self.interaction_type} - Product #{self.product_id}"


class ProductSimilarity(models.Model):
    """Pre-computed product similarities for faster recommendations"""
    product_id = models.IntegerField()
    similar_product_id = models.IntegerField()
    similarity_score = models.FloatField()  # 0-1
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_similarities'
        unique_together = ['product_id', 'similar_product_id']
        ordering = ['-similarity_score']
    
    def __str__(self):
        return f"Product #{self.product_id} similar to #{self.similar_product_id} ({self.similarity_score})"
