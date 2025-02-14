# itineraries/services.py

import requests
from django.conf import settings
from .auth import get_access_token 

AMADEUS_PNR_URL = "https://test.api.amadeus.com/v1/travel/pnr/v1/retrieve"
# Toggle this to True to enable mock mode
USE_MOCK = True

def fetch_pnr_details(pnr_locator, office_id=None):
    """
    Retrieves PNR details from Amadeus or returns mock data if enabled.
    """
    office_id = office_id or settings.AMADEUS_OFFICE_ID  # Ensure we use the correct Office ID

    print(f"🔍 Using Office ID: {office_id}")  # ✅ Debugging statement to check Office ID

    if USE_MOCK:
        print("🟢 Using Mock Mode for PNR Retrieval")
        return {
            "pnr": pnr_locator,
            "segments": [
                {
                    "type": "FLIGHT",
                    "carrierCode": "BA",
                    "flightNumber": "123",
                    "departure": {"iataCode": "LHR", "at": "2025-02-01T10:00:00"},
                    "arrival": {"iataCode": "JFK", "at": "2025-02-01T14:00:00"},
                    "bookingStatus": "CONFIRMED"
                }
            ]
        }
    
    # If not using mock, proceed with real API call
    access_token = get_access_token()
    
    if not access_token:
        print("❌ Failed to retrieve access token!")
        return None  # No token, fail gracefully

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "recordLocator": pnr_locator,
        "officeID": office_id or settings.AMADEUS_OFFICE_ID
    }


    response = requests.post(AMADEUS_PNR_URL, json=payload, headers=headers)

    print(f"🔍 API Status Code: {response.status_code}")
    print(f"🔍 API Response: {response.text}")  # Print full API response for debugging

    if response.status_code == 200:
        return response.json()  # Returns structured PNR data
    else:
        return None  # Handle API failure
