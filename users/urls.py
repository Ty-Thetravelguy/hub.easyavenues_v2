from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('toggle-bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('reorder-bookmarks/', views.reorder_bookmarks, name='reorder_bookmarks'),
    path('cleanup-bookmarks/', views.cleanup_duplicate_bookmarks, name='cleanup_bookmarks'),
    path('get-bookmarks/', views.get_bookmarks, name='get_bookmarks'),
]