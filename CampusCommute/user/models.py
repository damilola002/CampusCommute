from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomerUser(AbstractUser):
    RIDER  = 'rider'
    DRIVER = 'driver'
    ROLE_CHOICES = [
        (RIDER,  'Rider'),
        (DRIVER, 'Driver'),
    ]

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['user', 'full_name']

    full_name = models.CharField("Enter full name", max_length=225)
    email     = models.EmailField("Enter email .edu", unique=True)
    user      = models.CharField("Username", max_length=225)

    role       = models.CharField(max_length=10, choices=ROLE_CHOICES, default=RIDER)

    # Profile fields
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(blank=True, help_text="Short bio about yourself")

    # Driver location — Option A: stored home/campus base
    # Option B: overwritten with live GPS each time driver opens dashboard
    driver_lat = models.FloatField(null=True, blank=True)
    driver_lng = models.FloatField(null=True, blank=True)

    # Driver Vehicle details
    vehicle_model = models.CharField(max_length=100, blank=True)
    vehicle_type = models.CharField(max_length=50, blank=True, help_text="e.g. Sedan, SUV")
    vehicle_year = models.PositiveIntegerField(null=True, blank=True)
    license_plate = models.CharField(max_length=20, blank=True)

    # Driver Metrics
    average_rating = models.FloatField(default=0.0)
    total_passengers = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.full_name} ({self.role})"


class VerificationCode(models.Model):
    PURPOSE_CHOICES = [
        ('password_reset', 'Password Reset'),
        ('two_factor', 'Two-Factor Authentication'),
    ]
    email = models.EmailField()
    code = models.CharField(max_length=4)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        from django.utils import timezone
        import datetime
        return timezone.now() > self.created_at + datetime.timedelta(minutes=10)

    def __str__(self):
        return f"{self.email} - {self.code} ({self.purpose})"
