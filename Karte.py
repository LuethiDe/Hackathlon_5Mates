def exp_geojson():
    import folium
    import geopandas as gpd
    from pyproj import Transformer
    import json
    import pandas as pd
    from branca.element import Element

    gdf = gpd.read_file("data/bauobjekte.gpkg")
    print(gdf.columns)
    gdf.to_file("data/bauobjekte.geojson", driver="GeoJSON")

    map_with_layers = folium.Map(location=[46.8,8.3], zoom_start=8, control_scale=True,tiles=None)

    tile_url="https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/3857/{z}/{x}/{y}.jpeg"
    st_layer = folium.TileLayer(name="Swisstopo", tiles=tile_url, attr="swisstopo")
    st_layer.add_to(map_with_layers)

    wms_layer_av = folium.raster_layers.WmsTileLayer(
        url="https://wms.geo.admin.ch/",
        name="Amtliche Vermessung",
        layers="ch.swisstopo-vd.amtliche-vermessung",
        fmt="image/png",
        transparent=True,
        overlay=True,
        version="1.3.0",
        attr="swisstopo",
        control=True,
        **{
            "minZoom": 16 
        }
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

    geojson_path = "data/swissBOUNDARIES3D_1_3_TLM_GEMEINDEGEBIET.geojson"

    folium.GeoJson(
        geojson_path,
        name="Gemeindegebiete",
        show=False,
        tooltip=folium.GeoJsonTooltip(fields=["Gemeindename"], aliases=["Gemeinde:"]),
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': 'black',
            'weight': 2
        }
    ).add_to(map_with_layers)

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

    tooltip_rows = []
    x = 0

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

            tooltip_rows.append({
                "BGNr": bgnr,
                "Status": status,
                "Bauobjekt": bauobjekt,
                "Bewilligung": bewilligung,
                "Adresse": f"{strasse} {hausnr}",
                "Gemeinde": gemeinde,
                "PLZ": plz,
                "Kanton": kanton,
                "Parzelle": parznr,
                "Eigentümer Vorname": vorname,
                "Eigentümer Name": name,
                "Koordinaten": f"{lat}, {lon}"
            })
            
            # Tooltip-Inhalt erstellen
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

    df = pd.DataFrame(tooltip_rows)
    df.to_csv("baugesuche_tooltips.csv", index=False)

    print("Skript läuft bis zum Speichern.")
    try:
        folium.LayerControl().add_to(map_with_layers)
        map_with_layers.save("map.html")
        print("Map erfolgreich als map.html gespeichert!")
    except Exception as e:
        print("Fehler beim Speichern:", e)