import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from geocoding import get_lv95_coordinates
from archive import archive_all_csvs
from write_geopackage import combine_with_existing

# 1. CSV laden
df = pd.read_csv("Data/*.csv", sep=";")

# 2. Adresse für Geocoding zusammensetzen (Strasse + HausNr + Gemeinde)
def make_searchtext(row):
    strasse = str(row["Strasse"]).strip() if not pd.isna(row["Strasse"]) else ""
    hausnr = str(row["HausNr"]).strip() if not pd.isna(row["HausNr"]) else ""
    gemeinde = str(row["Gemeinde"]).strip() if not pd.isna(row["Gemeinde"]) else ""
    return f"{strasse} {hausnr} {gemeinde}".strip()

df["Suchtext"] = df.apply(make_searchtext, axis=1)

# 3. Koordinaten holen
def get_coords(searchtext):
    try:
        return get_lv95_coordinates(searchtext)
    except Exception:
        return (None, None)

coords = df["Suchtext"].apply(get_coords)
df["Ost"] = coords.apply(lambda val: val[0] if val else None)
df["Nord"] = coords.apply(lambda val: val[1] if val else None)

# 4. Nur gültige Koordinaten
df_valid = df.dropna(subset=["Ost", "Nord"]).copy()
df_valid["Ost"] = df_valid["Ost"].astype(float)
df_valid["Nord"] = df_valid["Nord"].astype(float)

# 5. GeoDataFrame bauen
gdf = gpd.GeoDataFrame(
    df_valid,
    geometry=[Point(e, n) for e, n in zip(df_valid["Ost"], df_valid["Nord"])],
    crs="EPSG:2056"
)

# 6. GeoPackage schreiben/an bestehendes anhängen
combine_with_existing(gdf)  # ID-Spalte optional ergänzen

print("GeoPackage erfolgreich erstellt! Anzahl Objekte:", len(gdf))

# 7. Importdatei archivieren
archive_all_csvs()