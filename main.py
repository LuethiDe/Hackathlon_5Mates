def process_csv():
    import pandas as pd
    import glob
    import geopandas as gpd
    from shapely.geometry import Point
    from geocoding import get_lv95_coordinates
    from archive import archive_all_csvs
    from write_geopackage import combine_with_existing

    # 1. Alle CSVs im Data-Ordner verarbeiten
    csv_files = glob.glob("Data/*.csv")
    if not csv_files:
        raise FileNotFoundError("Keine CSV-Dateien im Data-Ordner gefunden!")

    df_list = []
    for filepath in csv_files:
        df = pd.read_csv(filepath, sep=";")
        df_list.append(df)

    # Alle CSVs zusammenfassen
    df = pd.concat(df_list, ignore_index=True)

    # 2. Adresse für Geocoding zusammensetzen
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
    combine_with_existing(gdf)  # Wenn du eine ID-Spalte hast: combine_with_existing(gdf, unique_id_col="ID")

    print("GeoPackage erfolgreich erstellt! Anzahl Objekte:", len(gdf))

    # 7. Importdatei archivieren
    archive_all_csvs()
    return gdf