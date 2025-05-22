import folium
import shiny
import geopandas as gpd
from pyproj import Transformer
import json

gdf = gpd.read_file("data/Bauobjekte.gpkg")
print(gdf.columns)
gdf.to_file("data/bauobjekte.geojson", driver="GeoJSON")

map_with_layers = folium.Map(location=[46.8,8.3], zoom_start=8, control_scale=True,tiles=None)

tile_url="https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/3857/{z}/{x}/{y}.jpeg"
st_layer = folium.TileLayer(name="Swisstopo", tiles=tile_url, attr="swisstopo")
st_layer.add_to(map_with_layers)

wms_layer_av = folium.WmsTileLayer(
    url="https://wms.geo.admin.ch/",
    name="Amtliche Vermessung",
    layers="ch.swisstopo-vd.amtliche-vermessung", 
    fmt="image/png",
    overlay=False,
    transparent=True,
    version="1.3.0"
)
wms_layer_av.add_to(map_with_layers)

openstreetmap_layer = folium.TileLayer('OpenStreetMap')
openstreetmap_layer.add_to(map_with_layers)

geojson_path = "data/swissBOUNDARIES3D_1_3_TLM_KANTONSGEBIET.geojson"

folium.GeoJson(
    geojson_path,
    name="Kantonsgrenzen",
    tooltip=folium.GeoJsonTooltip(fields=["NAME"], aliases=["Kanton:"]),
    style_function=lambda x: {
        'fillColor': 'transparent',
        'color': 'black',
        'weight': 2
    }
).add_to(map_with_layers)

# geojson_path = "data/swissBOUNDARIES3D_1_3_TLM_GEMEINDEGEBIET.geojson"

# folium.GeoJson(
#     geojson_path,
#     name="Gemeindegebiete",
#     tooltip=folium.GeoJsonTooltip(fields=["Gemeindename"], aliases=["Gemeinde:"]),
#     style_function=lambda x: {
#         'fillColor': 'transparent',
#         'color': 'black',
#         'weight': 2
#     }
# ).add_to(map_with_layers)

geojson_path = "data/bauobjekte.geojson"

folium.GeoJson(
    geojson_path,
    name="Baugesuche",
    tooltip=folium.GeoJsonTooltip(fields=["BGNr"], aliases=["BG Nr:"]),
    style_function=lambda x: {
        'fillColor': 'transparent',
        'color': 'black',
        'weight': 100
    }
).add_to(map_with_layers)


transformer = Transformer.from_crs("EPSG:2056", "EPSG:4326", always_xy=True)

status_colors = {
    "bewilligt": "green",
    "Auflage": "orange",
    "Gesuch": "blue",
    "abgelehnt": "red"
}


with open("data/bauobjekte.geojson", encoding="utf-8") as f:
    geojson_data = json.load(f)



for feature in geojson_data["features"]:
    properties = feature["properties"]
    geometry = feature["geometry"]
    
    if geometry["type"] == "Point":
        easting, northing = geometry["coordinates"]
        lon, lat = transformer.transform(easting, northing)
        bgnr = properties.get("BGNr", "Unbekannt")
        status = properties.get("Status", "Unbekannt")
        color = status_colors.get(status, "gray")
        bauobjekt = properties.get("Bauobjekt", "Unbekannt")
        bewilligung = properties.get("Bewilligung", "Unbekannt")
        kanton = properties.get("Kanton", "Unbekannt")
        gemeinde = properties.get("Gemeinde", "Unbekannt")
        plz = properties.get("PLZ", "Unbekannt")
        strasse = properties.get("Strasse", "Unbekannt")
        hausnr = properties.get("HausNr", "Unbekannt")
        parznr = properties.get("ParzNr", "Unbekannt")
        name = properties.get("Name", "Unbekannt")
        vorname = properties.get("Vorname", "Unbekannt")
        
        # Tooltip-Inhalt erstellen
        tooltip_text = (
            f"Baugesuch Nr: {bgnr} ({status})<br>"
            f"Bauobjekt: {bauobjekt}<br>"
            f"Bewilligung: {bewilligung}<br>"
            f"Adresse: {strasse} {hausnr}<br>      {gemeinde} {plz}<br>      {kanton}<br>"
            f"Parzelle: {parznr}<br>"
            f"Eigentümer: {vorname} {name}"
        )
        
        # Marker erstellen
        folium.Marker(
            location=[lat, lon],
            tooltip=tooltip_text,
            icon=folium.Icon(color=color, icon="road")
        ).add_to(map_with_layers)

folium.LayerControl().add_to(map_with_layers)
map_with_layers.save("data/map.html")
