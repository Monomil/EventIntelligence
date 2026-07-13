import streamlit as st
from ticketmaster import fetch_events
import pandas as pd
from get_venues import get_venues
import plotly.express as px
import seaborn as sns


st.markdown(
    "<h1 style='text-align: center;'>Event Intelligence Dashboard</h1>",
    unsafe_allow_html=True,
)

colour_palette = ["#1A3A8F", # Deep navy blue 
               "#6B35C8", # Mid purple 
               "#00B4C8", # Teal/cyan 
               "#0D1F5C", # Near-black navy 
               "#C8B8F0", # Pale lavender 
               "#F4F4F6"  # Off-white  
]

st.set_page_config(
    page_title="Event Intelligence",
    layout="wide"
)



c = st.container(border = True)
# col1, col2 = st.columns(2)

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
        pass 




display_df = venue_counts.head(st.session_state.num_venues)

fig = px.bar(
    display_df, 
    x="venue_name", 
    y="events_per_venue",
    title=f"Number of Events per Venue (Top {st.session_state.num_venues})",
    labels={"venue_name": "<b>Venue Name<b>", "events_per_venue": "<b>Number of Events<b>"},
    hover_name="venue_name", # This puts the venue name in bold at the top of the tooltip
    color="events_per_venue",     # Optional: adds a nice color gradient based on counts
    height=800,
    color_continuous_scale= colour_palette,
)

fig.update_layout(
    xaxis_tickangle=-45, 
    plot_bgcolor="rgba(0,0,0,0)", 
    title= {'x': 0.5,
            'xanchor': 'center',
            "font": {"size": 28}
    },
    xaxis_title_font=dict(size=20),
    yaxis_title_font=dict(size=20)
)

fig.update_xaxes(
    tickfont=dict(size=14)
)
fig.update_yaxes(
    tickfont=dict(size=14)
)


with c:

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
            key="num_venues"  
            )
        
        st.plotly_chart(fig, use_container_width=True)



# Second plot



c2 = st.container(border=True)


venue_totals_segment = (
    events_df["venue_name"]
    .value_counts()
    .reset_index()
)

venue_totals_segment.columns = [
    "venue_name",
    "total_events",
]

max_segment_venues = len(venue_totals_segment)
min_segment_venues = min(10, max_segment_venues)

# Initialise session state

if "num_segment_venues" not in st.session_state:
    st.session_state.num_segment_venues = min_segment_venues

# Update slider value from text input

def apply_segment_text_input():
    raw = st.session_state.segment_venue_text_input

    try:
        value = int(raw)

        st.session_state.num_segment_venues = max(
            min_segment_venues,
            min(value, max_segment_venues),
        )

    except ValueError:
        pass

with c2:
    with st.spinner("Loading Graph..."):

        col_text_2, col_slider_2 = st.columns([1, 3])

        with col_text_2:
            st.text_input(
                "Enter a number",
                value=str(
                    st.session_state.num_segment_venues
                ),
                key="segment_venue_text_input",
                on_change=apply_segment_text_input,
                help=(
                    f"Type a number between "
                    f"{min_segment_venues} and "
                    f"{max_segment_venues}, then press Enter"
                ),
            )

        with col_slider_2:
            st.slider(
                "Number of venues to display",
                min_value=min_segment_venues,
                max_value=max_segment_venues,
                value=st.session_state.num_segment_venues,
                step=1,
                key="num_segment_venues",
            )

        # Get the selected number of busiest venues

        top_venue_names = (
            venue_totals_segment
            .head(
                st.session_state.num_segment_venues
            )["venue_name"]
            .tolist()
        )

        # Count events by venue and category

        venue_segments = (
            events_df
            .groupby(
                [
                    "venue_name",
                    "category_segment",
                ]
            )
            .size()
            .reset_index(name="event_count")
        )

        # Keep only the selected busiest venues

        display_segment_df = venue_segments[
            venue_segments["venue_name"].isin(
                top_venue_names
            )
        ].copy()

      

        display_segment_df["venue_name"] = pd.Categorical(
            display_segment_df["venue_name"],
            categories=top_venue_names,
            ordered=True,
        )

        display_segment_df = (
            display_segment_df
            .sort_values("venue_name")
        )

        # stacked bar chart

        fig_stacked = px.bar(
            display_segment_df,
            x="venue_name",
            y="event_count",
            color="category_segment",
            title=(
                f"Top "
                f"{st.session_state.num_segment_venues} "
                f"Busiest Venues by Event Category"
            ),
            labels={
                "event_count": "<b>Number of Events</b>",
                "venue_name": "<b>Venue Name</b>",
                "category_segment": "<b>Category</b>",
            },
            barmode="stack",
            template="plotly_dark",
            height=800,
        )

        fig_stacked.update_layout(
            xaxis_tickangle=-45,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font={
                "color": "white",
            },
            title={
                "x": 0.5,
                "xanchor": "center",
                "font": {
                    "size": 28,
                    "color": "white",
                    "family": "Arial Black",
                },
            },
            xaxis_title_font={
                "size": 20,
                "color": "white",
                "family": "Arial Black",
            },
            yaxis_title_font={
                "size": 20,
                "color": "white",
                "family": "Arial Black",
            },
            legend={
                "title": {
                    "text": "Event Category",
                    "font": {
                        "size": 14,
                        "color": "white",
                        "family": "Arial Black",
                    },
                },
                "font": {
                    "size": 12,
                    "color": "white",
                },
                "orientation": "v",
                "yanchor": "top",
                "y": 1,
                "xanchor": "left",
                "x": 1.02,
                "bgcolor": "rgba(0,0,0,0)",
            },
            margin={
                "r": 180,
                "b": 160,
            },
        )

        fig_stacked.update_xaxes(
            tickfont={
                "size": 14,
                "color": "white",
            },
            title_font={
                "size": 20,
                "color": "white",
                "family": "Arial Black",
            },
        )

        fig_stacked.update_yaxes(
            tickfont={
                "size": 14,
                "color": "white",
            },
            title_font={
                "size": 20,
                "color": "white",
                "family": "Arial Black",
            },
        )

        st.plotly_chart(
            fig_stacked,
            use_container_width=True,
        )

# Third plot

c3 = st.container(border=True)

city_counts = (
    events_df.groupby("city")["event_id"]
    .count()
    .reset_index()
)

venue_counts = (
    events_df.groupby("city")["venue_id"]
    .nunique()
    .reset_index()
)

ratios = city_counts.merge(
    venue_counts,
    on="city"
)

ratios["ratio"] = (
    ratios["event_id"] /
    ratios["venue_id"]
)

plot_df = (
    ratios.sort_values(
        "ratio",
        ascending=False,
    )
)

fig = px.bar(
    plot_df,
    x="city",
    y="ratio",
    color="ratio",
    color_continuous_scale=colour_palette,
    title="Average Events per Venue by City",
    labels={
        "city": "<b>City</b>",
        "ratio": "<b>Events per Venue</b>",
    },
    height=800,
)

fig.update_layout(
    xaxis_tickangle=-45,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font={
        "color": "white",
    },
    title={
        "x": 0.5,
        "xanchor": "center",
        "font": {
            "size": 28,
            "color": "white",
            "family": "Arial Black",
        },
    },
    xaxis_title_font={
        "size": 20,
        "color": "white",
        "family": "Arial Black",
    },
    yaxis_title_font={
        "size": 20,
        "color": "white",
        "family": "Arial Black",
    },
    coloraxis_colorbar={
        "title": {
            "text": "Events per Venue",
            "font": {
                "size": 14,
                "color": "white",
                "family": "Arial Black",
            },
        },
        "tickfont": {
            "size": 12,
            "color": "white",
        },
    },
)

fig.update_xaxes(
    tickfont={
        "size": 14,
        "color": "white",
    },
    title_font={
        "size": 20,
        "color": "white",
        "family": "Arial Black",
    },
)

fig.update_yaxes(
    tickfont={
        "size": 14,
        "color": "white",
    },
    title_font={
        "size": 20,
        "color": "white",
        "family": "Arial Black",
    },
)

with c3:
    st.plotly_chart(
        fig,
        use_container_width=True,
    )




# Fourth plot

c4 = st.container(border=True)

venue_counts_by_city = (
    events_df
    .groupby("city")["venue_id"]
    .nunique()
    .reset_index(name="venue_count")
    .sort_values("venue_count", ascending=False)
)

fig_city_venues = px.bar(
    venue_counts_by_city,
    x="city",
    y="venue_count",
    color="venue_count",
    color_continuous_scale=colour_palette,
    title="Number of Venues per City",
    labels={
        "city": "<b>City</b>",
        "venue_count": "<b>Number of Venues</b>",
    },
    hover_name="city",
    hover_data={
        "city": False,
        "venue_count": True,
    },
    height=800,
)

fig_city_venues.update_layout(
    xaxis_tickangle=-45,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font={
        "color": "white",
    },
    title={
        "x": 0.5,
        "xanchor": "center",
        "font": {
            "size": 28,
            "color": "white",
            "family": "Arial Black",
        },
    },
    xaxis_title_font={
        "size": 20,
        "color": "white",
        "family": "Arial Black",
    },
    yaxis_title_font={
        "size": 20,
        "color": "white",
        "family": "Arial Black",
    },
    coloraxis_colorbar={
        "title": {
            "text": "Venues",
            "font": {
                "size": 14,
                "color": "white",
                "family": "Arial Black",
            },
        },
        "tickfont": {
            "size": 12,
            "color": "white",
        },
    },
    margin={
        "t": 100,
        "b": 170,
    },
)

fig_city_venues.update_xaxes(
    tickfont={
        "size": 14,
        "color": "white",
    },
    title_font={
        "size": 20,
        "color": "white",
        "family": "Arial Black",
    },
)

fig_city_venues.update_yaxes(
    tickfont={
        "size": 14,
        "color": "white",
    },
    title_font={
        "size": 20,
        "color": "white",
        "family": "Arial Black",
    },
    gridcolor="rgba(255,255,255,0.15)",
)

with c4:
    st.plotly_chart(
        fig_city_venues,
        use_container_width=True,
    )







    
    