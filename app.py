#app.py in integriertem Terminal ausführen (rechtsklick auf den Dateinamen)
# conda activate [env_name]
# streamlit run [filepath] for running web gui
#http://localhost:8501

import streamlit as st
import pandas as pd
import numpy as np
from streamlit_folium import st_folium
from Karte import map_with_layers
import os

st.set_page_config(
    page_title="streamlit-folium documentation",
    page_icon=":world_map:️",
    layout="wide",
)

# Streamlit GUI
st.title('Baugesuch Übersicht_test')

#Baugesuch erfassen
csv_path = "data/Datensatz_Bauobjekte_test.csv"

@st.dialog("Cast your vote")
def Formular(item):
    st.write("Bitte Formular ausfüllen")
    ID = st.text_input("ID")
    Kanton = st.text_input("Kanton")
    Gemeinde = st.text_input("Gemeinde")
    Strasse_Hausnummer = st.text_input("Strasse, Hausnummer")
    Baugesuchs_Nummer = st.text_input("Baugesuchs-Nummer")
    Parzellennummer = st.text_input("Parzellennummer")
    Bauherrschaft = st.text_input("Bauherrschaft")
    Bauobjekt = st.text_input("Bauobjekt")
    Datum_Baubewilligung = st.date_input("Datum Baubewilligung")
    Status = st.selectbox("Status", ["Bewilligt", "Abgelehnt", "In Bearbeitung"])
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
                "Kanton": Kanton,
                "Gemeinde": Gemeinde,
                "Strasse, Hausnummer": Strasse_Hausnummer,
                "Baugesuchs-Nummer": Baugesuchs_Nummer,
                "Parzellennummer": Parzellennummer,
                "Bauherrschaft": Bauherrschaft,
                "Bauobjekt": Bauobjekt,
                "Datum Baubewilligung": Datum_Baubewilligung,
                "Status": Status
            }
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(csv_path, index=False)
            st.success("Neues Baugesuch erfasst!")
            st.session_state["show_dialog"] = False
            st.rerun()


if st.button("Neus Baugesuch erfassen"):
    Formular("A")

    

left_column, right_column = st.columns([2,4])

left_column.write("ID:")
left_column.write("Kanton:")
left_column.write("Gemeinde:")
left_column.write("Strasse, Hausnummer:")
left_column.write("Baugesuchs-Nummer:")
left_column.write("Parzellennummer:")
left_column.write("Bauherrschaft:")
left_column.write("Bauobjekt:")
left_column.write("Datum Baubewilligung:")
left_column.write("Status:")

with right_column:
    with open("data/map.html", "r", encoding="utf-8") as f:
        html_data = f.read()
    st.components.v1.html(html_data, height=500, width=900)



