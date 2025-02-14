# itineraries/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Trip
from .services import fetch_pnr_details
from .utils import process_pnr_data
from django.contrib.auth.decorators import login_required

@login_required
def import_pnr(request, trip_id, pnr_locator):
    trip = get_object_or_404(Trip, id=trip_id)
    pnr_data = fetch_pnr_details(pnr_locator)
    
    if pnr_data:
        process_pnr_data(trip, pnr_locator, pnr_data)
        return JsonResponse({"message": "PNR imported successfully!"}, status=200)
    else:
        return JsonResponse({"error": "Failed to retrieve PNR data"}, status=400)

@login_required
def itinerary_list(request):
    if request.method == 'POST':
        # Create new itinerary directly from the list view
        trip = Trip.objects.create(name="New Itinerary")
        return redirect('itineraries:detail', trip_id=trip.id)
    
    trips = Trip.objects.all()
    context = {
        'trips': trips
    }
    return render(request, 'itineraries/itinerary_list.html', context)

@login_required
def itinerary_detail(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    context = {
        'trip': trip
    }
    return render(request, 'itineraries/itinerary_detail.html', context)