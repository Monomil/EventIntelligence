# EventIntelligence

A live data pipeline and interactive dashboard for exploring UK event and venue data from the Ticketmaster Discovery API.

---

## How the Data Was Collected

All event and venue data is pulled **live** at runtime directly from the [Ticketmaster Discovery API](https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/). There are no pre-downloaded snapshots for events. Every time the dashboard loads, it makes fresh API calls and returns up-to-date results.

The API returns paginated responses, so the ingestion logic loops through every available page (up to the `totalPages` value returned in the response metadata), collecting all records before processing begins. With a page size of 200 and the country filter set to `GB`, this captures the full catalogue of UK events and venues available through the API at that moment.

Once all records are collected, the raw nested JSON is flattened into a clean, tabular pandas DataFrame ready for analysis and visualisation.

---

## Function Reference

### `ticketmaster.py`

| Function | What it does |
|---|---|
| `fetch_events()` | Paginates through the Ticketmaster Events endpoint for the UK, collecting every event across all pages. Flattens each raw JSON event into a flat record with fields like event name, date, venue, location, category, and pricing info. Then merges in venue capacity data before returning a single clean DataFrame. |

### `get_venues.py`

| Function | What it does |
|---|---|
| `fetch_venues()` | Paginates through the Ticketmaster Venues endpoint for the UK and returns the full list of raw venue records. |
| `clean_venues(all_venues)` | Takes the raw list from `fetch_venues()` and pulls out just the useful fields: venue ID, name, city, country, longitude, latitude, and postcode. |
| `get_venues()` | Convenience wrapper that calls `fetch_venues()` and `clean_venues()` in one go and returns the final DataFrame. |

---

## The Capacity Data: The Problem and the Workaround

### Why the API couldn't provide it

The Ticketmaster Discovery API does not expose venue capacity as a field. Capacity is considered commercially sensitive information and is not included in any API response, regardless of authentication level. This was a significant gap — capacity is a key dimension for understanding event scale and venue utilisation.

### First attempt: programmatic extraction from a hosted file

The initial approach was to host a Python dictionary containing manually researched capacity data (stored as `extracted_dictionary.txt`) on Google Drive, download it at runtime via `requests`, and parse it using `exec()`. The logic read the file content, replaced `null` values with Python `None`, then executed the string to extract the `data` variable and convert it to a DataFrame.

This worked locally but was ultimately **commented out** because Google Drive's download link behaviour is unreliable for programmatic access — Drive serves an HTML virus-warning page instead of the raw file once it detects an automated request, making the download unpredictable and not suitable for a live pipeline.

### Final solution: host as a CSV

The capacity data was converted into a CSV file and hosted on Google Drive with a direct export link (`?export=download`). This format bypasses the virus-warning interception that affects larger or unfamiliar file types. At runtime, `fetch_events()` reads the CSV directly into pandas with a single `pd.read_csv()` call using the raw export URL, then immediately merges it into the events DataFrame on `venue_name` using a left join.

This means every venue in the events data is looked up against the capacity dataset. Venues not present in the capacity CSV receive `NaN` for their capacity fields, which is handled gracefully in the dashboard by filling missing values with a default placeholder (1,000) purely for map bubble sizing purposes — the actual displayed label correctly shows "No capacity data" for those venues.

### What the capacity dataset contains

The capacity dataset (`extracted_dictionary.txt` / `df_capacity.csv`) was manually compiled and covers **~300 UK venues**, ranging from festival sites (Glastonbury: 210,000) down to small club venues (under 100). It includes:

- Major stadiums (Wembley, Old Trafford, London Stadium)
- Indoor arenas (The O2, Co-op Live, OVO Hydro)
- Festival grounds (Glastonbury, Download, Creamfields)
- Theatres, concert halls, and club venues

---

## Project Structure

```
EventIntelligence/
├── ticketmaster.py        # Core API ingestion and data processing logic
├── get_venues.py          # Standalone venue fetch and clean utilities
├── Dashboard.py           # Main Streamlit dashboard (bar charts, city breakdowns)
├── pages/
│   └── Event_Map.py       # Streamlit map page showing venue locations and capacity
├── extracted_dictionary.txt  # Source capacity data (manually compiled, ~300 UK venues)
├── df_capacity.csv        # Capacity data exported as CSV for live ingestion
├── df_events.csv          # Snapshot of events data
├── requirements.txt       # Python dependencies
└── .env                   # API key (not committed to version control)
```

---

## Setup

1. Clone the repository.
2. Create a `.env` file in the root with your Ticketmaster API key:
   ```
   TICKET_API=your_api_key_here
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the dashboard:
   ```
   streamlit run Dashboard.py
   ```
