from django import template
from ..models import PageBookmark

register = template.Library()

@register.filter
def has_bookmark(user, url):
    if user.is_authenticated:
        url = url.rstrip('/')  # same logic
        return PageBookmark.objects.filter(user=user, url=url).exists()
    return False