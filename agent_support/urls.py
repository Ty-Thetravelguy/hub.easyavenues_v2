from django.urls import path
from . import views

app_name = 'agent_support'

urlpatterns = [
    path('', views.agent_support_view, name='agent_support_view'),
]