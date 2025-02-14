# users/middleware.py

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
                    
                    # Get a better title based on the view name
                    view_name = resolver_match.url_name or ''
                    app_name = resolver_match.app_name or ''
                    title = view_name.replace('_', ' ').title()
                    
                    # Create a more descriptive title
                    if app_name and view_name:
                        title = f"{app_name.title()} - {view_name.replace('_', ' ').title()}"
                    else:
                        title = view_name.replace('_', ' ').title()
                    
                    # Only store if we have a valid title
                    if title:
                        # Get the full URL including query parameters
                        full_url = request.build_absolute_uri()
                        
                        RecentlyViewed.objects.update_or_create(
                            user=request.user,
                            url=full_url,  # Use full URL instead of just path
                            defaults={
                                'title': title,
                                'viewed_at': timezone.now()
                            }
                        )
                        
                        # Keep only last 10 entries
                        old_entries = RecentlyViewed.objects.filter(user=request.user).order_by('-viewed_at')[10:]
                        if old_entries.exists():
                            old_entries.delete()
                            
                except Resolver404:
                    pass

        return response