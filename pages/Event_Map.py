import pandas as pd
import plotly.express as px
import streamlit as st

from ticketmaster import fetch_events



# Page setup

st.set_page_config(
    page_title="Event Map",
    layout="wide",
)

# Page header

st.markdown(
    "<h1 style='text-align: center;'>Event Distribution Across UK Venues</h1>",
    unsafe_allow_html=True,)

# Colour palette

colour_palette = [
    "#C8B8F0",
    "#6B35C8",
    "#1A3A8F",
    "#0D1F5C",
]

# Load data

events_df = fetch_events()

# Validate columns

required_columns = [
    "event_id",
    "venue_id",
    "venue_name",
    "longitude",
    "latitude",
    "total_capacity",
]

missing_columns = [
    column
    for column in required_columns
    if column not in events_df.columns
]

if missing_columns:
    st.error(f"Missing required columns: {missing_columns}")
    st.write("Available columns:", events_df.columns.tolist())
    st.stop()

# Clean data

events_df["latitude"] = pd.to_numeric(
    events_df["latitude"],
    errors="coerce",
)

events_df["longitude"] = pd.to_numeric(
    events_df["longitude"],
    errors="coerce",
)

events_df["total_capacity"] = pd.to_numeric(
    events_df["total_capacity"],
    errors="coerce",
)

events_df = events_df.dropna(
    subset=[
        "venue_id",
        "venue_name",
        "latitude",
        "longitude",
    ]
)

# Aggregate venues

venue_counts = (
    events_df
    .groupby(
        [
            "venue_id",
            "venue_name",
            "longitude",
            "latitude",
        ],
        dropna=False,
    )
    .agg(
        events_per_venue=("event_id", "count"),
        total_capacity=("total_capacity", "max"),
    )
    .reset_index()
)

# Create plotting columns

venue_counts["capacity_plot"] = (
    venue_counts["total_capacity"]
    .fillna(1000)
    .clip(lower=100)
)

venue_counts["capacity_label"] = (
    venue_counts["total_capacity"]
    .apply(
        lambda value: (
            f"{int(value):,}"
            if pd.notna(value)
            else "No capacity data"
        )
    )
)

# Create map

map_plot = px.scatter_map(
    venue_counts,
    lat="latitude",
    lon="longitude",
    hover_name="venue_name",
    size="capacity_plot",
    color="events_per_venue",
    color_continuous_scale=colour_palette,
    hover_data={
        "events_per_venue": True,
        "capacity_label": True,
        "capacity_plot": False,
        "total_capacity": False,
        "latitude": False,
        "longitude": False,
        "venue_id": False,
    },
    labels={
        "events_per_venue": "Number of events",
        "capacity_label": "Venue capacity",
    },
    size_max=50,
    zoom=0.75,
    height=1000,
)

# Style map

map_plot.update_layout(
    mapbox_style="open-street-map",
    margin={
        "r": 0,
        "t": 0,
        "l": 0,
        "b": 0,
    },
    coloraxis_colorbar={
        "title": "Events",
        "tickfont": {
            "color": "white",
        },
        "title_font": {
            "color": "white",
        },
    },
)

# Display map

st.plotly_chart(
    map_plot,
    use_container_width=True,
)