# agent_support/models.py

from django.db import models

class AgentSupportSupplier(models.Model):
    
    SUPPLIER_TYPE = [
        ('air', 'Air'),
        ('accommodation', 'Accommodation'),
        ('ground_transportation', 'Ground Transportation'),
        ('rail', 'Rail'),
        ('other', 'Other'),
    ]

    supplier_type = models.CharField(max_length=25, choices=SUPPLIER_TYPE)
    supplier_name = models.CharField(max_length=255)
    agent_websites = models.JSONField(default=list, blank=True, null=True)
    contact_phone = models.JSONField(default=list, blank=True, null=True)
    general_email = models.JSONField(default=list, blank=True, null=True)
    group_phone = models.TextField(blank=True, null=True)
    group_email = models.TextField(blank=True, null=True)
    account_manager_name = models.TextField(blank=True, null=True)
    account_manager_email = models.EmailField(blank=True, null=True)
    account_manager_phone = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)