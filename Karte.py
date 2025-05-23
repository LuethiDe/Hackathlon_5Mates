import folium
import json
from pyproj import Transformer
from branca.element import Element

# Karte initialisieren
map_with_layers = folium.Map(location=[46.8, 8.3], zoom_start=8, control_scale=True)

# Beispiel: GeoJSON laden (Pfad anpassen!)
geojson_path = "data/bauobjekte.geojson"
with open(geojson_path, encoding="utf-8") as f:
    geojson_data = json.load(f)

# Koordinatentransformator (Swiss CH1903+ / EPSG:2056 -> WGS84)
transformer = Transformer.from_crs("EPSG:2056", "EPSG:4326", always_xy=True)

status_colors = {
    "bewilligt": "green",
    "Auflage": "orange",
    "Gesuch": "blue",
    "abgelehnt": "red"
}

marker_js = """
var markers = [];

// Info-Panel unten rechts erstellen
var infoPanel = L.control({position: 'bottomright'});
infoPanel.onAdd = function(map) {
    this._div = L.DomUtil.create('div', 'info-panel');
    this.update();
    return this._div;
};
infoPanel.update = function(props) {
    this._div.innerHTML = props ? `
    <h4>Baugesuch Details</h4>
    <table style="font-size:12px;">
        <tr><td><b>Baugesuch Nr:</b></td><td>${props.bgnr} (${props.status})</td></tr>
        <tr><td><b>Bauobjekt:</b></td><td>${props.bauobjekt}</td></tr>
        <tr><td><b>Bewilligung:</b></td><td>${props.bewilligung}</td></tr>
        <tr><td><b>Adresse:</b></td><td>${props.strasse} ${props.hausnr}</td></tr>
        <tr><td><b>Gemeinde:</b></td><td>${props.plz} ${props.gemeinde}</td></tr>
        <tr><td><b>Kanton:</b></td><td>${props.kanton}</td></tr>
        <tr><td><b>Parzelle:</b></td><td>${props.parznr}</td></tr>
        <tr><td><b>Eigentümer:</b></td><td>${props.vorname} ${props.name}</td></tr>
        <tr><td><b>Koordinaten:</b></td><td>${props.lat}, ${props.lon}</td></tr>
    </table>
    ` : '<h4>Bitte Marker anklicken</h4>';
};
infoPanel.addTo(map);
"""

# Marker mit Klick-Events erzeugen und JS ergänzen
for feature in geojson_data["features"]:
    if feature["geometry"]["type"] != "Point":
        continue

    easting, northing = feature["geometry"]["coordinates"]
    lon, lat = transformer.transform(easting, northing)
    props = feature["properties"]

    bgnr = props.get("BGNr", "Unbekannt")
    status = props.get("Status", "Unbekannt")
    color = status_colors.get(status, "gray")
    bauobjekt = props.get("Bauobjekt", "Unbekannt")
    bewilligung = props.get("Bewilligung", "Unbekannt")
    kanton = props.get("Kanton", "Unbekannt")
    gemeinde = props.get("Gemeinde", "Unbekannt")
    plz = props.get("PLZ", "Unbekannt")
    strasse = props.get("Strasse", "Unbekannt")
    hausnr = props.get("HausNr", "Unbekannt")
    parznr = props.get("ParzNr", "Unbekannt")
    name = props.get("Name", "Unbekannt")
    vorname = props.get("Vorname", "Unbekannt")

    tooltip_text = f"""
    <table style="font-size: 12px;">
    <tr><td><b>Baugesuch Nr:</b></td><td align="right">{bgnr} ({status})</td></tr>
    <tr><td><b>Bauobjekt:</b></td><td align="right">{bauobjekt}</td></tr>
    <tr><td><b>Bewilligung:</b></td><td align="right">{bewilligung}</td></tr>
    <tr><td><b>Adresse:</b></td><td align="right">{strasse} {hausnr}</td></tr>
    <tr><td><b>Gemeinde:</b></td><td align="right">{plz} {gemeinde}</td></tr>
    <tr><td><b>Kanton:</b></td><td align="right">{kanton}</td></tr>
    <tr><td><b>Parzelle:</b></td><td align="right">{parznr}</td></tr>
    <tr><td><b>Eigentümer:</b></td><td align="right">{vorname} {name}</td></tr>
    </table>
    """

    # Marker erstellen
    folium.Marker(
        location=[lat, lon],
        tooltip=tooltip_text,
        icon=folium.Icon(color=color, icon="book"),
        size=(2, 2)
    ).add_to(map_with_layers)

    marker_js += f"""
    var marker = L.marker([{lat}, {lon}], {{
        icon: L.icon({{
            iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
            shadowSize: [41, 41]
        }})
    }}).bindTooltip(`{tooltip_text}`);

    marker.on('click', function() {{
        var props = {{
            easting: {easting},
            northing: {northing},
            lon: {lon},
            lat: {lat},
            bgnr: "{bgnr}",
            status: "{status}",
            color: "{color}",
            bauobjekt: "{bauobjekt}",
            bewilligung: "{bewilligung}",
            kanton: "{kanton}",
            gemeinde: "{gemeinde}",
            plz: "{plz}",
            strasse: "{strasse}",
            hausnr: "{hausnr}",
            parznr: "{parznr}",
            name: "{name}",
            vorname: "{vorname}"
        }};
        window.aktuell_easting = props.easting;
        window.aktuell_northing = props.northing;
        window.aktuell_lon = props.lon;
        window.aktuell_lat = props.lat;
        window.aktuell_bgnr = props.bgnr;
        window.aktuell_status = props.status;
        window.aktuell_color = props.color;
        window.aktuell_bauobjekt = props.bauobjekt;
        window.aktuell_bewilligung = props.bewilligung;
        window.aktuell_kanton = props.kanton;
        window.aktuell_gemeinde = props.gemeinde;
        window.aktuell_plz = props.plz;
        window.aktuell_strasse = props.strasse;
        window.aktuell_hausnr = props.hausnr;
        window.aktuell_parznr = props.parznr;
        window.aktuell_name = props.name;
        window.aktuell_vorname = props.vorname;

        infoPanel.update(props);
        console.log("Aktuelle Marker-Daten gespeichert:", window.aktuell_bgnr);
    }});

    marker.addTo(map);
    markers.push(marker);
    """

# Style und Skript ins HTML einfügen
map_with_layers.get_root().html.add_child(Element("""
<style>
    .info-panel {
        background: white;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(0,0,0,0.2);
        font-family: Arial, sans-serif;
        font-size: 12px;
        max-width: 300px;
    }
</style>
<script>
""" + marker_js + """
</script>
"""))

# Layer-Control und Karte zurückgeben
folium.LayerControl().add_to(map_with_layers)
map_with_layers.save("data/map.html")
map_with_layers
