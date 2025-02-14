# dashboard/models.py

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


class UserBookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    url = models.URLField()
    favicon_url = models.URLField(blank=True, null=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'User Bookmark'
        verbose_name_plural = 'User Bookmarks'

    def __str__(self):
        return f"{self.user.email} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.order:
            # Get the highest order number and add 1
            last_order = UserBookmark.objects.filter(user=self.user).aggregate(
                models.Max('order'))['order__max']
            self.order = (last_order or 0) + 1
        super().save(*args, **kwargs)


class CompanyUpdate(models.Model):
    UPDATE_TYPES = [
        ('COMPANY', 'Company Update'),
        ('SUPPLIER', 'Supplier Update'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    update_type = models.CharField(
        max_length=10, 
        choices=UPDATE_TYPES, 
        default='COMPANY'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title

    @property
    def color(self):
        return '#9c85db' if self.update_type == 'COMPANY' else '#444a9f'

class UpdateAttachment(models.Model):
    update = models.ForeignKey(CompanyUpdate, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='updates/attachments/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename

    @property
    def file_type(self):
        """Returns the file extension for icon display"""
        ext = self.filename.split('.')[-1].lower()
        return ext