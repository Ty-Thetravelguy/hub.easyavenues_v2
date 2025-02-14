# dashboard/urls.py

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('bookmark/add/', views.add_bookmark, name='add_bookmark'),
    path('bookmark/<int:bookmark_id>/delete/', views.delete_bookmark, name='delete_bookmark'),
    path('bookmark/reorder/', views.reorder_bookmarks, name='reorder_bookmarks'),
    path('bookmark/<int:bookmark_id>/', views.get_bookmark, name='get_bookmark'),
    path('bookmark/<int:bookmark_id>/update/', views.update_bookmark, name='update_bookmark'),
    path('update/<int:pk>/', views.update_detail, name='update_detail'),

]
