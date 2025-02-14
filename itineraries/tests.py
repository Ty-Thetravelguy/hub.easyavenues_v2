# itineraries/tests.py

from django.test import TestCase
from .auth import get_access_token
from .services import fetch_pnr_details, USE_MOCK

class AmadeusAPITest(TestCase):

    def test_get_access_token(self):
        """
        Ensure we can retrieve an Amadeus access token.
        """
        if USE_MOCK:
            print("🟢 Skipping Access Token Test (Mock Mode Enabled)")
            return

        token = get_access_token()
        self.assertIsNotNone(token, "Failed to retrieve Amadeus API access token.")
        print(f"Access Token: {token}")

    def test_fetch_pnr_details(self):
        """
        Ensure we can retrieve PNR details (mocked for now).
        """
        pnr_locator = "MOCK123"  # Use a fake test PNR
        data = fetch_pnr_details(pnr_locator)
        self.assertIsNotNone(data, "Failed to retrieve PNR details.")
        print(f"Mocked PNR Data: {data}")