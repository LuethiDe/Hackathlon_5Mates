# streamlit run [filepath] for running web gui

import streamlit as st
import pandas as pd
import numpy as np
from streamlit_folium import st_folium
from Karte import map_with_layers
import os

st.set_page_config(layout="wide")

# Streamlit GUI
st.title('Baugesuch Viewer')
left_column, right_column = st.columns([4,1])
left_column.write('Zeigt eine Übersicht der Baugesuche in der Umgebung an.')

right_column.button("Neues Baugesuch erfassen", key="new_application")


with open("data/map.html", "r", encoding="utf-8") as f:
    html_data = f.read()
# In Streamlit anzeigen
st.components.v1.html(html_data, height=600, width=1300)