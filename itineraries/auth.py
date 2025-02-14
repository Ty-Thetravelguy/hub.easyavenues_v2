# itineraries/auth.py

import requests
from django.conf import settings

AMADEUS_AUTH_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"

def get_access_token():
    """
    Retrieves the Amadeus API access token.
    """
    payload = {
        "grant_type": "client_credentials",
        "client_id": settings.AMADEUS_API_KEY,
        "client_secret": settings.AMADEUS_API_SECRET
    }

    response = requests.post(AMADEUS_AUTH_URL, data=payload)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        return None  # Handle authentication failure

