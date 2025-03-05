# users/views.py
import logging
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import PageBookmark
from django.shortcuts import render

logger = logging.getLogger(__name__)

@login_required
def toggle_bookmark(request):
    if request.method == 'POST':
        raw_url = request.POST.get('url', '')
        
        # Improved URL normalization
        normalized_url = raw_url.lower()  # Convert to lowercase
        normalized_url = normalized_url.rstrip('/')  # Remove trailing slashes
        normalized_url = normalized_url.replace('_', '-')  # Standardize separators to hyphens

        try:
            # First clean any potential duplicates
            duplicates = PageBookmark.objects.filter(
                user=request.user, 
                url__iexact=normalized_url
            ).order_by('created_at')
            
            if duplicates.count() > 1:
                # Keep the oldest one and delete the rest
                keep_bookmark = duplicates.first()
                duplicates.exclude(id=keep_bookmark.id).delete()
                bookmark = keep_bookmark
            else:
                bookmark = duplicates.first()

            if bookmark:
                title = bookmark.title
                bookmark.delete()
                return JsonResponse({
                    'status': 'removed',
                    'message': f'"{title}" removed from bookmarks',
                    'title': title
                })
            else:
                order = PageBookmark.objects.filter(user=request.user).count()
                
                # Extract the last path segment and create title
                last_segment = normalized_url.strip('/').split('/')[-1]
                custom_title = (
                    last_segment
                    .replace('-', ' ')
                    .title()
                )

                # Create the bookmark
                bookmark = PageBookmark.objects.create(
                    user=request.user,
                    url=normalized_url,
                    title=custom_title,
                    order=order
                )
                return JsonResponse({
                    'status': 'added',
                    'message': f'"{custom_title}" added to bookmarks',
                    'title': custom_title,
                    'bookmark_html': f'''
                        <a href="{normalized_url}" class="list-group-item list-group-item-action bg-gradient-blue-purple text-white border-0 mb-2">
                            {custom_title}
                            <button class="btn btn-sm btn-link text-white float-end remove-bookmark" data-url="{normalized_url}">
                                <i class="fas fa-times"></i>
                            </button>
                        </a>
                    '''
                })

        except Exception as e:
            logger.error(f"Error toggling bookmark: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def cleanup_duplicate_bookmarks(request):
    """
    Clean up duplicate bookmarks for the current user.
    """
    if request.method == 'POST':
        try:
            # Get all bookmarks for the user
            bookmarks = PageBookmark.objects.filter(user=request.user)
            cleaned = 0
            
            # Group by normalized URL
            url_groups = {}
            for bookmark in bookmarks:
                normalized_url = bookmark.url.lower().rstrip('/').replace('_', '-')
                if normalized_url not in url_groups:
                    url_groups[normalized_url] = []
                url_groups[normalized_url].append(bookmark)
            
            # Keep oldest of each group, delete others
            for url_group in url_groups.values():
                if len(url_group) > 1:
                    # Sort by created_at and keep the oldest
                    url_group.sort(key=lambda x: x.created_at)
                    for bookmark in url_group[1:]:
                        bookmark.delete()
                        cleaned += 1
            
            return JsonResponse({
                'status': 'success',
                'cleaned': cleaned
            })
            
        except Exception as e:
            logger.error(f"Error cleaning up bookmarks: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def reorder_bookmarks(request):
    """
    Reorder existing bookmarks based on a list of bookmark IDs
    sent in the POST data.
    """
    if request.method == 'POST':
        try:
            bookmark_ids = request.POST.getlist('bookmarks[]')
            for index, bookmark_id in enumerate(bookmark_ids):
                PageBookmark.objects.filter(
                    id=bookmark_id,
                    user=request.user
                ).update(order=index)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Error reordering bookmarks: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def get_bookmarks(request):
    """Return the bookmark list HTML for AJAX refresh."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'users/includes/bookmark_list.html')
    return JsonResponse({'error': 'Invalid request'}, status=400)