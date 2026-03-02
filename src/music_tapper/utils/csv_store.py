# csv_store.py
import csv
import os

CSV_PATH = os.path.join("data", "library.csv")

def load_processed_set():
    if not os.path.exists(CSV_PATH):
        return set()
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return set( row["id"] for row in csv.DictReader(f))

def append_entry(artist, title, bpm, duration, filename, id):
    exists = os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["Artist", "Title", "BPM", "Duration", "Filename", "id"])
        writer.writerow([artist, title, bpm, duration, filename, id])