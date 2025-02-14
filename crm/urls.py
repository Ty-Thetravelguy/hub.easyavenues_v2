from django.urls import path
from . import views

urlpatterns = [
    path('', views.crm, name='crm'),
]
    