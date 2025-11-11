from django.db import models
from django.utils import timezone

# ---------- Choices ----------
PROPERTY_TYPES = [
    ('House', 'House'),
    ('Apartment', 'Apartment'),
    ('Studio', 'Studio'),
]

STATUS_CHOICES = [
    ('Vacant', 'Vacant'),
    ('Occupied', 'Occupied'),
]

# ---------- Property Model ----------
class Property(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    address = models.CharField(max_length=300)
    main_image = models.ImageField(upload_to='properties/')
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def total_units(self):
        return self.apartments.count()

    def occupied_units(self):
        return self.apartments.filter(status='Occupied').count()

    def vacancy_rate(self):
        total = self.total_units()
        if total == 0:
            return 0
        return ((total - self.occupied_units()) / total) * 100

    def occupancy_rate(self):
        total = self.total_units()
        if total == 0:
            return 0
        return (self.occupied_units() / total) * 100

# ---------- Apartment Model ----------
class Apartment(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='apartments')
    unit_number = models.CharField(max_length=50)
    bedrooms = models.PositiveIntegerField(default=1)  # Number of bedrooms
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Vacant')
    tenant_name = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.property.title} - Unit {self.unit_number}"

    def mark_occupied(self, tenant_name):
        self.status = 'Occupied'
        self.tenant_name = tenant_name
        self.save()

    def mark_vacant(self):
        self.status = 'Vacant'
        self.tenant_name = None
        self.save()
