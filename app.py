# streamlit run [filepath] for running web gui

import streamlit as st
import pandas as pd
import numpy as np
from streamlit_folium import st_folium
from Karte import map_with_layers
import os

#st.set_page_config(layout="wide")

# Streamlit GUI
st.title('Baugesuch Viewer')
st.write('Zeigt eine Übersicht der Baugesuche in der Umgebung an.')

st_folium(map_with_layers, width=1000, height=800)