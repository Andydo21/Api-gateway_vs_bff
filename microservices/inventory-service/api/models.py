from django.db import models

class Inventory(models.Model):
    product_id = models.IntegerField(unique=True)
    product_name = models.CharField(max_length=255)
    available_quantity = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    last_restocked = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inventory'
        verbose_name_plural = 'Inventories'
    
    def __str__(self):
        return f"{self.product_name} - Available: {self.available_quantity}"
    
    @property
    def total_quantity(self):
        return self.available_quantity + self.reserved_quantity
    
    @property
    def needs_restock(self):
        return self.available_quantity <= self.reorder_level


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('released', 'Released'),
        ('fulfilled', 'Fulfilled'),
        ('expired', 'Expired'),
    ]
    
    inventory = models.ForeignKey(Inventory, related_name='reservations', on_delete=models.CASCADE)
    order_id = models.IntegerField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reservations'
    
    def __str__(self):
        return f"Reservation for Order #{self.order_id} - {self.quantity} units"
