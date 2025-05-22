import requests

def get_lv95_coordinates(search_text):
    if not search_text:
        return None  # Leerer Suchtext, keine Anfrage

    url = "https://api3.geo.admin.ch/rest/services/api/SearchServer"
    params = {
        "searchText": search_text,
        #"origins": "address",
        "type": "locations",
        "sr": "2056"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        try:
            # Zugriff auf das erste gefundene Resultat
            coords = data["results"][0]["attrs"]
            x = coords.get("y")  # Achtung: y = Ost (Easting), gemäss API
            y = coords.get("x")  # x = Nord (Northing), gemäss API
            return x, y
        except (IndexError, KeyError):
            return None  # Kein Ergebnis oder unerwartete Struktur
    else:
        print(f"Fehler: {response.status_code}")
        return None