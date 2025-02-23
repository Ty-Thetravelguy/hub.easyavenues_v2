from .models import RecentlyViewed

def recently_viewed(request):
    # We don't need to return anything here since the related_name 
    # on the model makes it accessible via user.recently_viewed
    return {}
