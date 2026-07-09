import streamlit as st
import pandas as pd
from ticketmaster import fetch_events
import streamlit as st
import plotly.express as px
from app import venue_counts





venue_counts['latitude'] = pd.to_numeric(venue_counts['latitude'], errors='coerce')
venue_counts['longitude'] = pd.to_numeric(venue_counts['longitude'], errors='coerce')

# Remove any rows with invalid coordinates (NaN values)
venue_counts = venue_counts.dropna(subset=['latitude', 'longitude'])

# Create the scatter map with properly formatted numeric coordinates
map_plot = px.scatter_map(
    venue_counts, 
    lat="latitude", 
    lon="longitude", 
    hover_name="venue_name", 
    size="events_per_venue",
    color="events_per_venue",
    zoom=0.9, 
    height=1000
)

# Tell Plotly to use open-street-map (so you don't need a Mapbox API token)
map_plot.update_layout(mapbox_style="open-street-map")
map_plot.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# Display map in python
map_plot.show()


# Display the map in Streamlit
st.plotly_chart(map_plot, use_container_width=True)