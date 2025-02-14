# itineraries/urls.py

from django.urls import path
from .views import import_pnr
from . import views

app_name = 'itineraries'

urlpatterns = [
    path('import-pnr/<int:trip_id>/<str:pnr_locator>/', import_pnr, name='import_pnr'),
    path('', views.itinerary_list, name='itinerary_list'),
    path('<int:trip_id>/', views.itinerary_detail, name='detail'),
]
