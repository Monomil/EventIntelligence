import requests
import os
import re
import time
from typing import Optional
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

API_KEY = os.getenv("TICKET_API")

if not API_KEY:
    raise ValueError("That API key is not in your env, check your env for the correct variable name.")

BASE_URL = "https://app.ticketmaster.com"

EVENTS_ENDPOINT = "/discovery/v2/events"
VENUES_ENDPOINT = "/discovery/v2/venues"

def fetch_venues():
    all_venues = []
    current_page = 0
    total_pages = 1 

    while current_page < total_pages:
        venues_url = f"{BASE_URL}{VENUES_ENDPOINT}.json?apikey={API_KEY}&countryCode=GB&size=200&page={current_page}"
        venues_response = requests.get(venues_url).json()

        page_venues = venues_response.get('_embedded', {}).get('venues', [])
        all_venues.extend(page_venues)

        total_pages = venues_response.get('page', {}).get('totalPages', 1)
        current_page += 1
    return all_venues


def clean_venues(all_venues):
    uk_venues = []
    for venue in all_venues:
        venue_data = {
            "id":         venue.get("id"),
            "name":       venue.get("name"),
            "city":       venue.get("city", {}).get("name"),
            "country":    venue.get("country", {}).get("name"),
            "longitude":  venue.get("location", {}).get("longitude"),
            "latitude":   venue.get("location", {}).get("latitude"),
            "postcode": venue.get("postalCode")
            }
        uk_venues.append(venue_data)
    return uk_venues

def get_venues():
    venues_raw = fetch_venues()
    venues = clean_venues(venues_raw)
    return venues
