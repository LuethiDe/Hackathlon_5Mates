#app.py in integriertem Terminal ausführen (rechtsklick auf den Dateinamen)
# conda activate [env_name]
# streamlit run app.py
#http://localhost:8501

from main import process_csv
from Karte import exp_geojson
import streamlit as st
import pandas as pd
import numpy as np
from streamlit_folium import st_folium
from Karte import *
import os

st.set_page_config(
    page_title="streamlit-folium documentation",
    page_icon=":world_map:️",
    layout="wide",
)

# Streamlit GUI
st.title('Baugesuch Übersicht')

#Baugesuch erfassen
csv_path = "data/Datensatz_Bauobjekte_test.csv"

@st.dialog("Baugesuch erfassen")
def Formular(item):
    #st.write("Bitte Formular ausfüllen")
    ID = st.text_input("ID")
    BGNr = st.text_input("Baugesuchs-Nummer")
    Status = st.selectbox("Status", ["Bewilligt", "Abgelehnt", "In Bearbeitung"])
    Bauobjekt = st.text_input("Bauobjekt")
    Bewilligung = st.date_input("Datum Baubewilligung")
    Kanton = st.text_input("Kanton")
    Gemeinde = st.text_input("Gemeinde")
    PLZ = st.text_input("PLZ")
    col1, col2 = st.columns([2, 1])
    with col1:
        Strasse = st.text_input("Strasse")
    with col2:
        HausNr = st.text_input("Hausnummer")
    ParzNr = st.text_input("Parzellennummer")
    Name = st.text_input("Name")
    Vorname = st.text_input("Vorname")
    submitted = st.button("Absenden")
    if submitted:
            # robust lesen/schreiben wie vorher
            if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
                try:
                    df = pd.read_csv(csv_path)
                except Exception as e:
                    st.warning(f"Fehler beim Einlesen der CSV: {e}")
                    df = pd.DataFrame()
            else:
                df = pd.DataFrame()

            new_entry = {
                "ID": ID,
                "Status": Status,
                "BGNr": BGNr,
                "Bauobjekt": Bauobjekt,
                "Bewilligung": Bewilligung,
                "Kanton": Kanton,
                "Gemeinde": Gemeinde,
                "PLZ": PLZ,
                "Strasse": Strasse,
                "HausNr": HausNr,
                "ParzNr": ParzNr,
                "Name": Name,
                "Vorname": Vorname
            }
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(csv_path, index=False, sep=";")
            st.success("Neues Baugesuch erfasst!")
            gdf = process_csv()
            if gdf is not None:
                st.success("GeoPackage erfolgreich erstellt!")
            else:
                st.error("Fehler beim Erstellen des GeoPackage.")
            exp_geojson()
            st.session_state["show_dialog"] = False
            st.rerun()


if st.button("Neus Baugesuch erfassen"):
    Formular("A")

# Ausgabe gewähltes Baugesuch
left_column, right_column = st.columns([2,4])
# left_column.write(f"Baugesuch Nr: {bgnr} ({status})")
# left_column.write(f"Bauobjekt: {bauobjekt}")
# left_column.write(f"Bewilligung: {bewilligung}")
# left_column.write(f"Adresse: {strasse} {hausnr}")
# left_column.write(f"Gemeinde: {plz} {gemeinde}")
# left_column.write(f"Kanton: {kanton}")
# left_column.write(f"Parzelle: {parznr}")
# left_column.write(f"Eigentümer: {vorname} {name}")


with right_column:
    with open("map.html", "r", encoding="utf-8") as f:
        html_data = f.read()
    st.components.v1.html(html_data, height=500, width=900)
