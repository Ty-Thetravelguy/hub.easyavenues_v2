# account/urls.py

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='account_signup'),
    path('create-user/', views.create_user, name='create_user'),
    path('users/', views.user_list, name='user_list'),
]
