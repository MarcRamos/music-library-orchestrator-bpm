import time
import os
import argparse
import glob
import re

import click

from music_tapper.utils.archive import build_search_query, search_items, get_mp3_files, download_mp3
from music_tapper.utils.audio_utils import normalize_mp3_name_meta, save_bpm_to_mp3
from music_tapper.utils.bpm_ui import measure_bpm_ui
from music_tapper.utils.csv_store import load_processed_set, append_entry
from music_tapper.utils.bpm_organizer import bpm_folder


def process_archive_files(query):
    processed = load_processed_set()
    DEST_DIR = os.path.join("download", "raw")
    os.makedirs(DEST_DIR, exist_ok=True)

    page = 1
    total_items = None
    running = True
    while running:
        response = search_items(page, query)

        if total_items is None:
            total_items = response["numFound"]
            print(f"📀 Items found: {total_items}")

        items = response["docs"]
        if not items:
            break

        print(f"➡️ Page {page}, items: {len(items)}")

        for item in items:
            identifier = item["identifier"]
            if identifier in processed:
                print(f"Object already processed: {identifier}, skipping.")
            file_names = get_mp3_files(identifier)
            for file_name in file_names:
                print(f"MP3 file: {file_name}")
                mp3_path = download_mp3(identifier, file_name, DEST_DIR)
                time.sleep(0.5)  # be nice to archive.org
                bpm, running = measure_bpm_ui(mp3_path)
                if bpm is None:
                    if not running:
                        print("🚫 Cancelled by the user")
                        break
                    print("⏭️ Skipped by the user")
                    continue
                
                save_bpm_to_mp3(mp3_path, bpm)
                object_mp3 = normalize_mp3_name_meta(
                    mp3_path, os.path.join("library", bpm_folder(bpm))
                )
                object_mp3.update({"id": identifier})
                append_entry(**object_mp3)
                print("🎶 Successfully processed\n")
            if not running:
                break


def process_local_folder(folder_path, out_folder="library/"):
    """Processes all MP3s without BPM tag in a folder using the BPM UI"""
    mp3_files = [
        p for p in glob.glob(os.path.join(folder_path, "*.mp3"))
        if not re.match(r'^\(\d+\)', os.path.basename(p))
    ]
    for mp3_path in mp3_files:
        print(f"🎵 Processing {os.path.basename(mp3_path)}")
        bpm, running = measure_bpm_ui(mp3_path)
        if bpm is None:
            if not running:
                print("🚫 Cancelled by the user")
                break
            print("⏭️ Skipped by the user")
            continue
        save_bpm_to_mp3(mp3_path, bpm)
        bpm_out_folder = os.path.join(out_folder, bpm_folder(bpm))
        object_mp3 = normalize_mp3_name_meta(mp3_path, bpm_out_folder)
        object_mp3.update({"id": None})
        append_entry(**object_mp3)
        print("✅ Successfully processed\n")


@click.group()
def main():
    """🎧 Music Library BPM Orchestrator"""
    pass

@main.command()
@click.option("--text", default=None)
@click.option("--artist", default=None)
@click.option("--genres", default=None)
@click.option("--subjects", default=None)
@click.option("--year-from", type=int, default=None)
@click.option("--year-to", type=int, default=None)
def download(text, artist, genres, subjects, year_from, year_to):

    query = build_search_query(
        text=text,
        subjects=subjects.split(",") if subjects and "," in subjects else subjects,
        genres=genres.split(",") if genres and "," in genres else genres,
        year_from=year_from,
        year_to=year_to,
        artist=artist
    )

    print("🔎 Query:", query)
    process_archive_files(query)

@main.command()
@click.argument("local_folder", type=click.Path(exists=True))
def from_folder(local_folder):
    """Process all MP3 files in a local folder"""
    process_local_folder(local_folder)