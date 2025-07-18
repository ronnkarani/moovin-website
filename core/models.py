# core/models.py
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Property(models.Model):
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='properties')
    tenant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rented_properties')
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='property_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Add landlord = models.ForeignKey(...) if needed
    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    size = models.CharField(max_length=50, blank=True)  # e.g., "95 m²"
    status = models.CharField(max_length=50, default="Available")
    furnished = models.BooleanField(default=False)
    parking = models.CharField(max_length=50, default="Available")

    def __str__(self):
        return self.title

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')

    def __str__(self):
        return f"Image for {self.property.title}"
    

class RepairRequest(models.Model):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repair_requests')
    property = models.ForeignKey('Property', on_delete=models.CASCADE, related_name='repairs')
    issue = models.TextField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Fixed', 'Fixed')], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tenant.username} - {self.property.title} - {self.status}"