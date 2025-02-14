# itineraries/utils.py

from .models import PNR, TravelSegment

def process_pnr_data(trip, pnr_locator, data):
    """
    Takes the PNR API response and saves it in the database.
    """
    pnr_obj, created = PNR.objects.get_or_create(trip=trip, locator=pnr_locator)
    
    for segment in data.get("segments", []):
        TravelSegment.objects.create(
            PNR=pnr_obj,
            segment_type=segment["type"],
            carrier=segment.get("carrierCode"),
            flight_number=segment.get("flightNumber"),
            departure_date=segment["departure"]["at"],
            arrival_date=segment["arrival"]["at"],
            departure_airport=segment["departure"]["iataCode"],
            arrival_airport=segment["arrival"]["iataCode"],
            booking_status=segment["bookingStatus"]
        )
