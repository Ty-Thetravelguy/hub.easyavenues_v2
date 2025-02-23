from django.utils import timezone
from django.urls import resolve, Resolver404
from .models import RecentlyViewed

class RecentlyViewedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated and request.method == 'GET':
            skip_paths = [
                '/admin/',
                '/static/',
                '/media/',
                '/accounts/login/',
                '/accounts/logout/',
                '/microsoft/',
                '/socialaccount/',
                '/favicon.ico',
                '/dashboard/',
            ]
            
            current_path = request.path
            
            if not any(current_path.startswith(path) for path in skip_paths):
                try:
                    title = None
                    
                    if hasattr(response, 'context_data') and 'title' in response.context_data:
                        title = response.context_data['title']
                    
                    if not title:
                        try:
                            resolver_match = resolve(current_path)
                            view_name = resolver_match.url_name
                            app_name = resolver_match.app_name or resolver_match.namespace
                            
                            if app_name and view_name:
                                title = f"{app_name.title()} - {view_name.replace('_', ' ').title()}"
                            elif view_name:
                                title = view_name.replace('_', ' ').title()
                        except Resolver404:
                            pass
                    
                    if not title:
                        title = current_path.strip('/').replace('/', ' - ').title()
                    
                    entry, _ = RecentlyViewed.objects.update_or_create(
                        user=request.user,
                        url=current_path,
                        defaults={
                            'title': title,
                            'viewed_at': timezone.now()
                        }
                    )
                    
                    # Keep only last 10 entries
                    entries = RecentlyViewed.objects.filter(user=request.user)
                    if entries.count() > 10:
                        entries.order_by('-viewed_at')[10:].delete()
                        
                except Exception:
                    pass

        return response