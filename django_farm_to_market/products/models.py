from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('piece', 'Piece'),
        ('dozen', 'Dozen'),
        ('box', 'Box'),
        ('bundle', 'Bundle'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='piece')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        from django.db.models import Avg
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0 