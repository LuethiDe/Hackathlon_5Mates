import shutil
import os
import datetime
import glob

def archive_all_csvs(source_pattern="Data/*.csv", archive_dir="Data/archiv/"):
    """
    Verschiebt alle CSV-Dateien aus Data/ ins Archiv, jeder bekommt einen Zeitstempel.
    """
    os.makedirs(archive_dir, exist_ok=True)
    files = glob.glob(source_pattern)
    if not files:
        print(f"Keine Dateien gefunden für Pattern: {source_pattern}")
        return
    for file in files:
        basename = os.path.basename(file)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        ziel = os.path.join(archive_dir, f"{os.path.splitext(basename)[0]}_{timestamp}.csv")
        shutil.move(file, ziel)
        print(f"{file} wurde nach {ziel} verschoben.")