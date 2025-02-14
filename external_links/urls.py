from django.urls import path
from . import views

urlpatterns = [
    path('', views.external_links, name='external_links'),
]

