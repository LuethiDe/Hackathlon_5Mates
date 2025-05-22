import geopandas as gpd
import pandas as pd
import os

GPKG_PATH = "Data/bauobjekte.gpkg"
LAYER_NAME = "bauobjekte"

def combine_with_existing(new_gdf, gpkg_path=GPKG_PATH, layer_name=LAYER_NAME, unique_id_col=None):
    """
    Hängt neuen GeoDataFrame an bestehenden Layer im GeoPackage an.
    Vermeidet Dubletten, wenn 'unique_id_col' eindeutig ist.
    """
    if os.path.exists(gpkg_path):
        print("Bestehendes GeoPackage gefunden – importiere und hänge an.")
        old_gdf = gpd.read_file(gpkg_path, layer=layer_name)
        combined = pd.concat([old_gdf, new_gdf], ignore_index=True)
        if unique_id_col and unique_id_col in combined.columns:
            combined = combined.drop_duplicates(subset=[unique_id_col])
        else:
            combined = combined.drop_duplicates()
        combined = gpd.GeoDataFrame(combined, geometry="geometry", crs=new_gdf.crs)
    else:
        print("Kein GeoPackage vorhanden – neu erstellen.")
        combined = new_gdf

    combined.to_file(gpkg_path, layer=layer_name, driver="GPKG")
    print(f"{len(combined)} Objekte jetzt im GeoPackage '{gpkg_path}'.")