# itineraries/admin.py

from django.contrib import admin
from .models import Trip, PNR, TravelSegment

admin.site.register(Trip)
admin.site.register(PNR)
admin.site.register(TravelSegment)
