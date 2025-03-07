# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class Business(models.Model):
    id = models.AutoField(primary_key=True)
    business_name = models.CharField(max_length=255)
    main_contact = models.CharField(max_length=255)
    main_contact_email = models.EmailField()
    main_contact_phone = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.business_name
    class Meta:
        verbose_name_plural = "Businesses"

class BusinessDomain(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='domains')
    domain = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.domain} ({self.business.business_name})"  

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('superuser', 'Superuser'),
        ('admin', 'Admin'),
        ('agent', 'Agent'),
        ('marketing', 'Marketing'),
    ]

    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = None  # Remove username field
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='agent')
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        null=True,
        related_name='users'
    )

    # Fix conflicts with Django's auth.User model
    groups = models.ManyToManyField(Group, related_name="customuser_groups")
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def save(self, *args, **kwargs):
        # Ensure username is set to email if it's blank
        if not self.username and self.email:
            self.username = self.email

        # Set permissions based on role
        if self.role == 'superuser':
            self.is_superuser = True
            self.is_staff = True
        elif self.role in ['admin', 'agent']:
            self.is_superuser = False
            self.is_staff = True
        else:  # marketing
            self.is_superuser = False
            self.is_staff = False
            
        # Call parent save
        super(CustomUser, self).save(*args, **kwargs) 