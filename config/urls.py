# config/urls

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from accounts.views import signup

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('account_login'), name='root'), 
    path('accounts/', include('accounts.urls')), 
    path('', include('allauth.urls')),  
    path('signup/', signup, name='signup'), 
    path('dashboard/', include('dashboard.urls')),
    path('users/', include('users.urls', namespace='users')), 
    path('agent-support/', include('agent_support.urls')),
    path('crm/', include('crm.urls')),
    path('finance/', include('finance.urls')),
    path('office/', include('office.urls')),
    path('external-links/', include('external_links.urls')),
    path('query-log/', include('query_log.urls')),
    path('itineraries/', include('itineraries.urls')),
]

