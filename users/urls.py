from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('bookmark/toggle/', views.toggle_bookmark, name='toggle_bookmark'),
    path('bookmark/reorder/', views.reorder_bookmarks, name='reorder_bookmarks'),
]