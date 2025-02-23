# users/views.py
import logging
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import PageBookmark

logger = logging.getLogger(__name__)

@login_required
def toggle_bookmark(request):
    if request.method == 'POST':
        raw_url = request.POST.get('url', '')
        normalized_url = raw_url.rstrip('/')

        try:
            bookmark = PageBookmark.objects.filter(
                user=request.user, 
                url=normalized_url
            ).first()

            if bookmark:
                bookmark.delete()
                return JsonResponse({'status': 'removed'})
            else:
                order = PageBookmark.objects.filter(user=request.user).count()
                
                # Extract the last path segment, transform underscores/dashes into spaces
                # e.g. '/agent_support'.strip('/') -> 'agent_support' 
                # -> split('/')[-1] -> 'agent_support'
                # -> replace('_', ' ') -> 'agent support' 
                # -> title() -> 'Agent Support'
                last_segment = normalized_url.strip('/').split('/')[-1]
                custom_title = (
                    last_segment
                    .replace('-', ' ')
                    .replace('_', ' ')
                    .title()
                )

                # Create the bookmark
                PageBookmark.objects.create(
                    user=request.user,
                    url=normalized_url,
                    title=custom_title,
                    order=order
                )
                return JsonResponse({'status': 'added'})

        except Exception as e:
            logger.error(f"Error toggling bookmark: {str(e)}")
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