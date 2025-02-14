# users/models.py

from django.db import models
from django.conf import settings

class RecentlyViewed(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recently_viewed'
    )
    url = models.URLField()
    title = models.CharField(max_length=255)
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-viewed_at']
        verbose_name = 'Recently Viewed Page'
        verbose_name_plural = 'Recently Viewed Pages'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'url'],
                name='unique_user_url'
            )
        ]

    def __str__(self):
        return f"{self.user.email} - {self.title}"