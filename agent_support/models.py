# agent_support/models.py

from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os
from django.utils.safestring import mark_safe

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
    other_notes = models.JSONField(
        default=list,
        blank=True, 
        null=True,
        help_text="Additional notes about the supplier"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    scribe_html = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Scribe HTML Content",
        help_text="Paste the Scribe HTML content here"
    )

    def get_safe_scribe_html(self):
        """Returns the Scribe HTML content marked as safe for rendering"""
        if self.scribe_html:
            return mark_safe(self.scribe_html)
        return ""

class SupplierAttachment(models.Model):
    supplier = models.ForeignKey('AgentSupportSupplier', on_delete=models.CASCADE, related_name='attachments')
    heading = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    pdf_file = models.FileField(
        upload_to='supplier_attachments/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.heading} - {self.supplier.supplier_name}"

@receiver(post_delete, sender=SupplierAttachment)
def delete_attachment_file(sender, instance, **kwargs):
    """
    Delete the file from filesystem when SupplierAttachment instance is deleted.
    """
    if instance.pdf_file:
        if os.path.isfile(instance.pdf_file.path):
            os.remove(instance.pdf_file.path)