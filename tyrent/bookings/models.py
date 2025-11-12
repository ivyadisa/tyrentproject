from django.db import models
from django.utils import timezone
from django.conf import settings
from listings.models import Apartment

User = settings.AUTH_USER_MODEL

class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
    ]

    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.tenant} → {self.apartment} ({self.status})"

    class Meta:
        ordering = ['-created_at']
