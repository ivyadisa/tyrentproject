from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    """
    Custom User model for Tyrent System accounts app.
    Extends Django's AbstractUser with UUID primary key,
    user role management, verification, and status tracking.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture_url = models.URLField(max_length=500, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("LANDLORD", "Landlord"),
        ("TENANT", "Tenant"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
        ("SUSPENDED", "Suspended"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="ACTIVE")

    VERIFICATION_CHOICES = [
        ("PENDING", "Pending"),
        ("VERIFIED", "Verified"),
        ("REJECTED", "Rejected"),
    ]
    verification_status = models.CharField(max_length=10, choices=VERIFICATION_CHOICES, default="PENDING")
    verification_notes = models.TextField(null=True, blank=True)
    verification_date = models.DateTimeField(null=True, blank=True)

    verified_by_admin = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_accounts',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['email', 'full_name', 'phone_number']

    def __str__(self):
        return f"{self.full_name} ({self.role})"


class TenantProfile(models.Model):
    """
    Extended profile for tenants — linked one-to-one with User.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tenant_profile')
    current_address = models.CharField(max_length=255, null=True, blank=True)
    preferred_location = models.CharField(max_length=255, null=True, blank=True)
    occupation = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Tenant Profile: {self.user.full_name}"


class LandlordProfile(models.Model):
    """
    Extended profile for landlords — linked one-to-one with User.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='landlord_profile')
    property_name = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    business_permit_number = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    national_id = models.CharField(max_length=20, null=True, blank=True)  # added this field

    def __str__(self):
        return f"Landlord Profile: {self.user.full_name}"

def house_image_upload_path(instance, filename):
    """
    File will be uploaded to MEDIA_ROOT/houses/<landlord_id>/<filename>
    """
    return f'houses/{instance.landlord.user.id}/{filename}'

class VacantHouse(models.Model):
    landlord = models.ForeignKey(
        'accounts.LandlordProfile',  # Assuming your landlord profile model is named LandlordProfile
        on_delete=models.CASCADE,
        related_name='houses'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to=house_image_upload_path, null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Vacant House"
        verbose_name_plural = "Vacant Houses"

    def __str__(self):
        return f"{self.title} - {self.landlord.user.full_name}"
