from django.db import models
from django.utils import timezone
from django.conf import settings

PROPERTY_TYPES = [
    ('House', 'House'),
    ('Apartment', 'Apartment'),
    ('Studio', 'Studio'),
]

STATUS_CHOICES = [
    ('Vacant', 'Vacant'),
    ('Occupied', 'Occupied'),
]

class Property(models.Model):
    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='property_listings'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    address = models.CharField(max_length=300)
    main_image = models.ImageField(upload_to='properties/', blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def total_units(self):
        return self.apartments.count()

    def occupied_units(self):
        return self.apartments.filter(status='Occupied').count()

class Apartment(models.Model):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='apartments'
    )
    title = models.CharField(max_length=255)
    unit_number = models.CharField(max_length=50, blank=True, null=True)
    bedrooms = models.PositiveIntegerField(default=1)
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Vacant')
    tenant_name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='apartments/', blank=True, null=True)
    video = models.FileField(upload_to='apartments/videos/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.property.title} - {self.title or self.unit_number or 'Apartment'}"
