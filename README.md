# EventIntelligence

Live event and venue intelligence dashboard for the UK, powered by the Ticketmaster Discovery API.

---

## Data Pipeline

**Ingestion:** At runtime, the pipeline paginates through the Ticketmaster Discovery API (`countryCode=GB`, `size=200`) collecting every available UK event and venue across all pages.

**Transformation:** Raw nested JSON is flattened into clean tabular DataFrames, extracting fields like event name, date, venue, location, category, and pricing.

**Capacity enrichment:** The API does not expose venue capacity. A manually compiled CSV of ~300 UK venues was hosted on Google Drive and merged into the events DataFrame on `venue_name` at runtime via a left join.

**Capacity limitation:** The original approach downloaded a hosted Python dictionary and parsed it with `exec()`. Google Drive intercepts automated requests with an HTML warning page, making it unreliable. Switching to a CSV with a direct export link resolved this.

**Missing values:** Venues absent from the capacity dataset receive `NaN`. The map uses a default placeholder of 1,000 for bubble sizing only; the tooltip correctly displays "No capacity data".

---

## Functions

| File | Function | What it does |
|---|---|---|
| `ticketmaster.py` | `fetch_events()` | Paginates through the Events endpoint, flattens each record, and merges in capacity data before returning a single DataFrame. |
| `get_venues.py` | `fetch_venues()` | Paginates through the Venues endpoint and returns all raw venue records. |
| `get_venues.py` | `clean_venues()` | Extracts venue ID, name, city, country, coordinates, and postcode from raw records. |
| `get_venues.py` | `get_venues()` | Convenience wrapper that calls `fetch_venues()` and `clean_venues()` in one call. |

---

## Setup

```
# .env
TICKET_API=your_api_key_here
```
```
pip install -r requirements.txt
streamlit run Dashboard.py
```
