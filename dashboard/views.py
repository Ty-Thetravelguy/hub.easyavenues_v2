#dashboard/views.py

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .models import UserBookmark, CompanyUpdate

@login_required
def dashboard(request):
    bookmarks = UserBookmark.objects.filter(user=request.user)
    updates = CompanyUpdate.objects.all()[:10]  # Limit to 10 most recent updates
    
    return render(request, 'dashboard/dashboard.html', {
        'bookmarks': bookmarks,
        'updates': updates
    })

@login_required
@require_http_methods(["POST"])
def add_bookmark(request):
    try:
        data = json.loads(request.body)
        url = data.get('url')
        title = data.get('title')

        if not url or not title:
            return JsonResponse({'error': 'URL and title are required'}, status=400)

        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Fetch favicon
        favicon_url = fetch_favicon(url)

        bookmark = UserBookmark.objects.create(
            user=request.user,
            url=url,
            title=title,
            favicon_url=favicon_url
        )

        return JsonResponse({
            'id': bookmark.id,
            'title': bookmark.title,
            'url': bookmark.url,
            'favicon_url': bookmark.favicon_url
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST", "DELETE"])
def delete_bookmark(request, bookmark_id):
    try:
        bookmark = get_object_or_404(UserBookmark, id=bookmark_id, user=request.user)
        bookmark.delete()
        return JsonResponse({'status': 'success', 'message': 'Bookmark deleted successfully'})
    except UserBookmark.DoesNotExist:
        return JsonResponse({'error': 'Bookmark not found'}, status=404)
    except Exception as e:
        print(f"Error deleting bookmark {bookmark_id}: {str(e)}")  # For server logs
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def reorder_bookmarks(request):
    try:
        data = json.loads(request.body)
        items = data.get('items', [])

        for item in items:
            bookmark = UserBookmark.objects.get(
                id=item['id'], 
                user=request.user
            )
            bookmark.order = item['order']
            bookmark.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def fetch_favicon(url):
    try:
        # Get the webpage content
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for favicon in different locations
        favicon = None
        
        # 1. Check for apple-touch-icon first (usually higher quality)
        apple_icon = soup.find('link', rel=lambda x: x and 'apple-touch-icon' in x.lower())
        if apple_icon:
            favicon = apple_icon.get('href')
        
        # 2. Check for standard icon tags
        if not favicon:
            icons = soup.find_all('link', rel=lambda x: x and ('icon' in x.lower() or 'shortcut icon' in x.lower()))
            if icons:
                favicon = icons[0].get('href')
        
        # 3. Try the default location
        if not favicon:
            favicon = urljoin(url, '/favicon.ico')
            
        # Make sure we have an absolute URL
        favicon = urljoin(url, favicon)
        
        # 4. If all else fails, use Google's favicon service
        try:
            requests.head(favicon).raise_for_status()
        except:
            # Extract domain from URL
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            favicon = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"  
        
        return favicon
    except:
        # If everything fails, use Google's favicon service
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            return f"https://www.google.com/s2/favicons?domain={domain}&sz=128" 
        except:
            return None

@login_required
def get_bookmark(request, bookmark_id):
    try:
        bookmark = get_object_or_404(UserBookmark, id=bookmark_id, user=request.user)
        return JsonResponse({
            'id': bookmark.id,
            'title': bookmark.title,
            'url': bookmark.url,
            'favicon_url': bookmark.favicon_url
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["PUT"])
def update_bookmark(request, bookmark_id):
    try:
        bookmark = get_object_or_404(UserBookmark, id=bookmark_id, user=request.user)
        data = json.loads(request.body)
        
        url = data.get('url')
        title = data.get('title')

        if not url or not title:
            return JsonResponse({'error': 'URL and title are required'}, status=400)

        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Update bookmark
        bookmark.url = url
        bookmark.title = title
        bookmark.favicon_url = fetch_favicon(url)
        bookmark.save()

        return JsonResponse({
            'id': bookmark.id,
            'title': bookmark.title,
            'url': bookmark.url,
            'favicon_url': bookmark.favicon_url
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def update_detail(request, pk):
    update = get_object_or_404(CompanyUpdate, pk=pk)
    
    data = {
        'id': update.id,
        'title': update.title,
        'content': update.content,
        'created_at': update.created_at.isoformat(),
        'modified_at': update.updated_at.isoformat(),  # Changed from modified_at to updated_at
        'attachments': [
            {
                'file': attachment.file.url,
                'filename': attachment.filename
            }
            for attachment in update.attachments.all()
        ]
    }
    
    return JsonResponse(data)
