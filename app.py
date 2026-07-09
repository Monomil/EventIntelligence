import streamlit as st
from ticketmaster import fetch_events
import pandas as pd
from get_venues import get_venues
import plotly.express as px




col1, col2 = st.columns(2)


events_df = fetch_events()

cols_to_drop = ['date',	'time', 'multi_day_event', 'legal_age_enforced', 'category_segment', 'category_genre',	'category_sub_genre', 'all_inclusive_pricing','markets', 'markets_id', 'url', 'address','postcode','city']

try:
    df_dropped = events_df.drop(columns=cols_to_drop, errors='ignore')
    print("\nDataFrame after dropping columns:")
    print(df_dropped)
except KeyError as e:
    print(f"Error: {e}")

venue_counts = df_dropped.groupby(['venue_id','venue_name','longitude', 'latitude']).size().reset_index(name='events_per_venue')

# Sort descending so the slider always shows the top N venues
venue_counts = venue_counts.sort_values("events_per_venue", ascending=False).reset_index(drop=True)

max_venues = len(venue_counts)
min_venues = min(10, max_venues)

# Initialise session state on first run
if "num_venues" not in st.session_state:
    st.session_state.num_venues = min_venues

def apply_text_input():
    """Validate the text box value and push it into session state."""
    raw = st.session_state.venue_text_input
    try:
        val = int(raw)
        st.session_state.num_venues = max(min_venues, min(val, max_venues))
    except ValueError:
        pass  # ignore non-numeric input; slider keeps its current value




display_df = venue_counts.head(st.session_state.num_venues)

fig = px.bar(
    display_df, 
    x="venue_name", 
    y="events_per_venue",
    title=f"Number of Events per Venue (Top {st.session_state.num_venues})",
    labels={"venue_name": "<b>Venue Name<b>", "events_per_venue": "<b>Number of Events<b>"},
    hover_name="venue_name", # This puts the venue name in bold at the top of the tooltip
    color="events_per_venue",     # Optional: adds a nice color gradient based on counts
    height=600,
    color_continuous_scale="Viridis"
)

fig.update_layout(
    xaxis_tickangle=-45, # Tilts the venue names so they don't overlap
    plot_bgcolor="rgba(0,0,0,0)", # Gives it a clean white background
    title= {'x': 0.5,
            'xanchor': 'center'
    }
)

with col1:

    col_text, col_slider = st.columns([1, 3])

    with st.spinner("Loading Chart"): 
        col_text, col_slider = st.columns([1, 3])
        with col_text:
            st.text_input(
            "Enter a number",
            value=str(st.session_state.num_venues),
            key="venue_text_input",
            on_change=apply_text_input,
            help=f"Type a number between {min_venues} and {max_venues}, then press Enter"
            )

        with col_slider:
            num_venues = st.slider(
            "Number of venues to display",
            min_value=min_venues,
            max_value=max_venues,
            value=st.session_state.num_venues,
            step=1,
            key="num_venues"   # binds directly to session_state.num_venues
            )
        
        st.plotly_chart(fig, use_container_width=True)



with col2:
    st.write("hello")
    
    