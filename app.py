# streamlit run [filepath] for running web gui

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import os



# Streamlit GUI
st.title('Baugesuch Viewer')
st.write('Zeigt eine Übersicht der Baugesuche in der Umgebung an.')

left_column, right_column = st.columns(2)
with left_column:
    st.button("Baugesuch erfassen")
    st.text("ID")
    st.text("Kanton")
    st.text("Gemeinde")
    st.text("Strasse, Hausnummer")
    st.text("Baugesuchs-Nummer")
    st.text("Parzellennummer")
    st.text("Bauherrschaft")
    st.text("Bauobjekt")
    st.text("Datum der Baubewilligung")
    st.text("Status")

with right_column:
    map_data = pd.DataFrame(
        np.random.randn(1000, 2) / [50, 50] + [47.56, 7.58],  # Basel Beispiel
        columns=['lat', 'lon'])
    st.map(map_data)
