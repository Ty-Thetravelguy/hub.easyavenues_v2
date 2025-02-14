## itineraries/models.py

from django.db import models

class Trip(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class PNR(models.Model):
    trip = models.ForeignKey(Trip, related_name="pnrs", on_delete=models.CASCADE)
    locator = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PNR {self.locator} for Trip {self.trip.name}"

class TravelSegment(models.Model):
    PNR = models.ForeignKey(PNR, related_name="segments", on_delete=models.CASCADE)
    segment_type = models.CharField(max_length=50, choices=[('FLIGHT', 'Flight'), ('HOTEL', 'Hotel'), ('CAR', 'Car Rental')])
    carrier = models.CharField(max_length=50, blank=True, null=True)
    flight_number = models.CharField(max_length=10, blank=True, null=True)
    departure_date = models.DateTimeField()
    arrival_date = models.DateTimeField()
    departure_airport = models.CharField(max_length=10)
    arrival_airport = models.CharField(max_length=10)
    booking_status = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.segment_type} {self.carrier}{self.flight_number} ({self.departure_airport} -> {self.arrival_airport})"

