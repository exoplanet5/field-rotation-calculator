"""
Field Rotation Calculator — Streamlit entrypoint.

Run:  streamlit run app.py
"""

import streamlit as st

st.set_page_config(page_title='Alt-Az Telescope Specs', layout='wide')

nav = st.navigation([
    st.Page('track_specs.py',  title='Az-Alt Track Specs',  default=True),
    st.Page('zenith_polar.py', title='Zenith Polar Specs'),
])
nav.run()
