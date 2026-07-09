"""
ticketmaster.py

Utility functions for pulling data from the Ticketmaster Discovery API
and transforming it into clean, flat records ready for analysis.

Requires:
    - TICKET_API set in a .env file (loaded via python-dotenv)
    - requests, pandas, python-dotenv installed
"""

import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load the API key from the .env file
load_dotenv()
API_KEY = os.getenv("TICKET_API")

if not API_KEY:
    raise ValueError("TICKET_API not found in environment. Check your .env file.")

# Base URL and endpoint paths for the Ticketmaster Discovery API
BASE_URL = "https://app.ticketmaster.com"
EVENTS_ENDPOINT = "/discovery/v2/events"
VENUES_ENDPOINT = "/discovery/v2/venues"


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

def fetch_events(country_code: str = "GB", page_size: int = 200) -> list[dict]:
    """
    Fetch all events for a given country from the Ticketmaster API.

    Paginates through all available pages and returns the raw event records
    as a flat list of dicts straight from the API response.

    Args:
        country_code: ISO 3166-1 alpha-2 country code (default "GB").
        page_size:    Number of results per page (max 200).

    Returns:
        List of raw event dicts.
    """
    all_events = []
    current_page = 0
    total_pages = 1  # Updated after the first response

    while current_page < total_pages:
        url = (
            f"{BASE_URL}{EVENTS_ENDPOINT}.json"
            f"?apikey={API_KEY}&countryCode={country_code}"
            f"&size={page_size}&page={current_page}"
        )
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Extract the list of events from the nested response structure
        page_events = data.get("_embedded", {}).get("events", [])
        all_events.extend(page_events)

        # Update the total page count from the response metadata
        total_pages = data.get("page", {}).get("totalPages", 1)
        current_page += 1

    print(f"Fetched {len(all_events)} events.")
    return all_events


def clean_events(raw_events: list[dict]) -> pd.DataFrame:
    """
    Extract and flatten the fields we care about from raw event records.

    Pulls event metadata, classification (segment / genre / sub-genre),
    venue info, and market data into a tidy DataFrame.

    Args:
        raw_events: List of raw event dicts returned by fetch_events().

    Returns:
        A pandas DataFrame with one row per event.
    """
    records = []

    for event in raw_events:
        # Classifications (segment → genre → sub-genre)
        class_list = event.get("classifications") or []
        cls = class_list[0] if class_list else {}

        # Primary venue
        venue_list = event.get("_embedded", {}).get("venues") or []
        vn = venue_list[0] if venue_list else {}

        # Primary market for the venue
        market_list = vn.get("markets") or []
        mkt = market_list[0] if market_list else {}

        records.append({
            "event_id":             event.get("id"),
            "name":                 event.get("name"),
            "date":                 event.get("dates", {}).get("start", {}).get("localDate"),
            "time":                 event.get("dates", {}).get("start", {}).get("localTime"),
            "multi_day_event":      event.get("dates", {}).get("spanMultipleDays"),
            "legal_age_enforced":   event.get("ageRestrictions", {}).get("legalAgeEnforced"),

            # Category / classification fields
            "category_segment":     cls.get("segment", {}).get("name"),
            "category_genre":       cls.get("genre", {}).get("name"),
            "category_sub_genre":   cls.get("subGenre", {}).get("name"),

            "all_inclusive_pricing": event.get("ticketing", {}).get(
                                        "allInclusivePricing", {}
                                    ).get("enabled"),

            # Venue fields
            "venue_id":   vn.get("id"),
            "venue_name": vn.get("name"),
            "address":    vn.get("address", {}).get("line1"),
            "postcode":   vn.get("postalCode"),
            "city":       vn.get("city", {}).get("name"),
            "longitude":  vn.get("location", {}).get("longitude"),
            "latitude":   vn.get("location", {}).get("latitude"),

            # Market fields
            "market":    mkt.get("name"),
            "market_id": mkt.get("id"),

            "url": event.get("url"),
        })

    return pd.DataFrame(records)


def get_events_df(country_code: str = "GB") -> pd.DataFrame:
    """
    Convenience wrapper: fetch and clean events in one call.

    Args:
        country_code: ISO 3166-1 alpha-2 country code (default "GB").

    Returns:
        A clean pandas DataFrame of events.
    """
    raw = fetch_events(country_code)
    return clean_events(raw)


# ---------------------------------------------------------------------------
# Venues
# ---------------------------------------------------------------------------

def fetch_venues(country_code: str = "GB", page_size: int = 200) -> list[dict]:
    """
    Fetch all venues for a given country from the Ticketmaster API.

    Paginates through all available pages and returns the raw venue records
    as a flat list of dicts straight from the API response.

    Args:
        country_code: ISO 3166-1 alpha-2 country code (default "GB").
        page_size:    Number of results per page (max 200).

    Returns:
        List of raw venue dicts.
    """
    all_venues = []
    current_page = 0
    total_pages = 1  # Updated after the first response

    while current_page < total_pages:
        url = (
            f"{BASE_URL}{VENUES_ENDPOINT}.json"
            f"?apikey={API_KEY}&countryCode={country_code}"
            f"&size={page_size}&page={current_page}"
        )
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Extract the list of venues from the nested response structure
        page_venues = data.get("_embedded", {}).get("venues", [])
        all_venues.extend(page_venues)

        # Update the total page count from the response metadata
        total_pages = data.get("page", {}).get("totalPages", 1)
        current_page += 1

    print(f"Fetched {len(all_venues)} venues.")
    return all_venues


def clean_venues(raw_venues: list[dict]) -> pd.DataFrame:
    """
    Extract and flatten the fields we care about from raw venue records.

    Args:
        raw_venues: List of raw venue dicts returned by fetch_venues().

    Returns:
        A pandas DataFrame with one row per venue.
    """
    records = []

    for venue in raw_venues:
        records.append({
            "venue_id":  venue.get("id"),
            "name":      venue.get("name"),
            "city":      venue.get("city", {}).get("name"),
            "country":   venue.get("country", {}).get("name"),
            "longitude": venue.get("location", {}).get("longitude"),
            "latitude":  venue.get("location", {}).get("latitude"),
            "postcode":  venue.get("postalCode"),
        })

    return pd.DataFrame(records)


def get_venues_df(country_code: str = "GB") -> pd.DataFrame:
    """
    Convenience wrapper: fetch and clean venues in one call.

    Args:
        country_code: ISO 3166-1 alpha-2 country code (default "GB").

    Returns:
        A clean pandas DataFrame of venues.
    """
    raw = fetch_venues(country_code)
    return clean_venues(raw)
