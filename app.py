import streamlit as st
from ticketmaster import fetch_events

st.write(fetch_events())

import pandas as pd
from get_venues import get_venues

venues_df = pd.DataFrame(get_venues())
st.write(venues_df)
