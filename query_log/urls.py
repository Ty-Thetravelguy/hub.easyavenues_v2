from django.urls import path
from . import views

urlpatterns = [
    path('', views.query_log, name='query_log'),
]
