# users/middleware.py

from django.utils import timezone
from .models import RecentlyViewed

from django.utils import timezone
from django.urls import resolve, Resolver404
from .models import RecentlyViewed

class RecentlyViewedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated and request.method == 'GET':
            # Skip these paths
            skip_paths = [
                '/admin/',
                '/static/',
                '/media/',
                '/accounts/',
                '/microsoft/',
                '/socialaccount/',
                '/favicon.ico',
                '/',
            ]
            
            if not any(request.path.startswith(path) for path in skip_paths):
                try:
                    # Get the URL name from the resolver
                    resolver_match = resolve(request.path)
                    view_name = resolver_match.url_name or ''
                    
                    # Convert URL name to a readable title
                    title = view_name.replace('_', ' ').replace('-', ' ').title()
                    
                    # Only store if we have a valid title
                    if title:
                        RecentlyViewed.objects.update_or_create(
                            user=request.user,
                            url=request.path,
                            defaults={
                                'title': title,
                                'viewed_at': timezone.now()
                            }
                        )
                        
                        # Keep only last 10 entries
                        entries = RecentlyViewed.objects.filter(user=request.user)
                        if entries.count() > 10:
                            entries.last().delete()
                            
                except Resolver404:
                    # If the URL doesn't resolve, don't store it
                    pass

        return response