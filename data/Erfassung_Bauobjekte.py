import csv
import os
import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry

CSV_DATEI = "Datensatz_Bauobjekte.csv"

status_werte = ["bewilligt", "Auflage", "Gesuch", "abgelehnt", "gelöscht"]
kantone = [
    "AG", "AI", "AR", "BE", "BL", "BS", "FR", "GE", "GL", "GR", "JU", "LU",
    "NE", "NW", "OW", "SG", "SH", "SO", "SZ", "TG", "TI", "UR", "VD", "VS", "ZG", "ZH"
]

felder_ohne_id = [
    "BGNr", "Status", "Bauobjekt", "Bewilligung", "Kanton", "Gemeinde",
    "PLZ", "Strasse", "HausNr", "ParzNr", "Name", "Vorname"
]

pflichtfelder = [f for f in felder_ohne_id if f not in ["Bewilligung", "HausNr"]]

def naechste_id():
    if not os.path.exists(CSV_DATEI):
        return 1

    ids = []
    with open(CSV_DATEI, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            id_raw = row.get("ID", "").strip()
            if id_raw.isdigit():
                ids.append(int(id_raw))
    return max(ids) + 1 if ids else 1


def speichern(neu=True):
    daten = {feld: entries[feld].get() for feld in felder_ohne_id}
    if any(daten[feld].strip() == "" for feld in pflichtfelder):
        messagebox.showwarning("Pflichtfelder", "Bitte alle Pflichtfelder ausfüllen.")
        return

    if neu:
        daten["ID"] = str(naechste_id())
        modus = "a"
    else:
        daten["ID"] = gefundene_id[0]
        modus = "w"

    try:
        if not os.path.exists(CSV_DATEI) or modus == "a":
            with open(CSV_DATEI, modus, newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["ID"] + felder_ohne_id, delimiter=";")
                if modus == "a" and os.path.getsize(CSV_DATEI) == 0:
                    writer.writeheader()
                writer.writerow(daten)
        else:
            with open(CSV_DATEI, newline='', encoding='utf-8') as f:
                rows = list(csv.DictReader(f, delimiter=";"))

            for row in rows:
                if row["BGNr"] == daten["BGNr"]:
                    for feld in felder_ohne_id:
                        row[feld] = daten[feld]
                    row["ID"] = daten["ID"]

            with open(CSV_DATEI, "w", newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["ID"] + felder_ohne_id, delimiter=";")
                writer.writeheader()
                writer.writerows(rows)

        messagebox.showinfo("Erfolg", f"Baugesuch gespeichert (BGNr {daten['BGNr']})")
        for entry in entries.values():
            if isinstance(entry, (tk.Entry, DateEntry)):
                entry.delete(0, tk.END)
            elif isinstance(entry, ttk.Combobox):
                entry.set("")

        if neu:
            root.destroy()

    except Exception as e:
        messagebox.showerror("Fehler", f"{e}")


def suche_bgnr():
    bgnr = suchfeld.get().strip()
    if not bgnr:
        return
    try:
        with open(CSV_DATEI, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                if row["BGNr"] == bgnr:
                    for feld in felder_ohne_id:
                        widget = entries[feld]
                        wert = row[feld]
                        if feld in ["Status", "Kanton"]:
                            widget.set(wert)
                        else:
                            widget.delete(0, tk.END)
                            widget.insert(0, wert)
                    global gefundene_id
                    gefundene_id = (row["ID"], bgnr)
                    messagebox.showinfo("Gefunden", f"Eintrag mit BGNr {bgnr} geladen.")
                    return
        messagebox.showwarning("Nicht gefunden", f"Kein Eintrag mit BGNr {bgnr} gefunden.")
    except Exception as e:
        messagebox.showerror("Fehler", f"{e}")


# GUI Aufbau
root = tk.Tk()
root.geometry("450x600")
root.title("Baugesuch erfassen / anzeigen")

entries = {}
for i, feld in enumerate(felder_ohne_id):
    tk.Label(root, text=feld + ":").grid(row=i + 1, column=0, sticky="w", padx=5, pady=2)

    if feld == "Status":
        combobox = ttk.Combobox(root, values=status_werte, state="readonly", width=37)
        combobox.grid(row=i + 1, column=1, sticky="w", padx=5, pady=2)
        entries[feld] = combobox
    elif feld == "Kanton":
        combobox = ttk.Combobox(root, values=kantone, state="readonly", width=37)
        combobox.grid(row=i + 1, column=1, sticky="w", padx=5, pady=2)
        entries[feld] = combobox
    elif feld == "Bewilligung":
        date_entry = DateEntry(root, date_pattern="yyyy-mm-dd", width=37)
        date_entry.grid(row=i + 1, column=1, sticky="w", padx=5, pady=2)
        entries[feld] = date_entry
    else:
        entry = tk.Entry(root, width=40)
        entry.grid(row=i + 1, column=1, sticky="w", padx=5, pady=2)
        entries[feld] = entry

# Suchfeld für BGNr
start_row = len(felder_ohne_id) + 1

tk.Label(root, text="BGNr suchen:").grid(row=start_row, column=0, sticky=tk.W, padx=5, pady=10)
suchfeld = tk.Entry(root, width=30)
suchfeld.grid(row=start_row, column=1, padx=5, pady=5, sticky=tk.W)

# Buttons
tk.Button(root, text="Eintrag laden", command=suche_bgnr).grid(row=start_row + 1, column=1, sticky=tk.W, padx=5)
tk.Button(root, text="Neues Baugesuch speichern", command=lambda: speichern(neu=True)).grid(row=start_row + 2, column=0, pady=10)

root.mainloop()
