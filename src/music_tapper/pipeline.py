import time
import os
import argparse
import glob
import re

import click

from music_tapper.utils.archive import search_items, get_mp3_files, download_mp3
from music_tapper.utils.audio_utils import normalize_mp3_name_meta, save_bpm_to_mp3
from music_tapper.utils.bpm_ui import measure_bpm_ui
from music_tapper.utils.csv_store import load_processed_set, append_entry
from music_tapper.utils.bpm_organizer import bpm_folder


def process_archive_files():
    processed = load_processed_set()
    print(processed)

    DEST_DIR = os.path.join("download", "raw")
    os.makedirs(DEST_DIR, exist_ok=True)

    page = 1
    total_items = None
    running = True
    while running:
        response = search_items(page)

        if total_items is None:
            total_items = response["numFound"]
            print(f"📀 Items found: {total_items}")

        items = response["docs"]
        if not items:
            break

        print(f"➡️ Page {page}, items: {len(items)}")

        for item in items:
            identifier = item["identifier"]
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
        bpm = measure_bpm_ui(mp3_path)
        if bpm is None:
            print("⏭️ Skipped by the user")
            continue
        save_bpm_to_mp3(mp3_path, bpm)
        bpm_out_folder = os.path.join(out_folder, bpm_folder(bpm))
        object_mp3 = normalize_mp3(mp3_path, bpm_out_folder)
        object_mp3.update({"id": None})
        append_entry(**object_mp3)
        print("✅ Successfully processed\n")

def main():
    parser = argparse.ArgumentParser(
        description="Full pipeline: download songs from Archive.org, " \
        "measure BPM, and organize into folders"
    )
    parser.add_argument(
        "--folder", type=str, default=None,
        help="Process all MP3s in the specified folder using the BPM UI"
    )

    parser.add_argument(
        "--out-folder", type=str, default=None,
        help="Save resulting mp3 with BPM tag and moves inside a" \
        " BPM ranged folder within output location"
    )

    args = parser.parse_args()

    if args.folder:
        if not os.path.isdir(args.folder):
            raise FileNotFoundError(f"❌ Folder {args.folder} does not exist")
        if args.out_folder is None:
            raise ValueError(f"❌ Output Folder must be defined (--out-folder arg)")
        if not os.path.isdir(args.out_folder):
             print(f"❌ Output folder {args.out_folder} does not exist")
        else:
            process_local_folder(args.folder, args.out_folder)
    else:
        print("🚀 Starting Archive.org download and BPM pipeline…")
        process_archive_files()


@click.group()
def main():
    """🎧 Music Library BPM Orchestrator"""
    pass

@main.command()
def download():
    """Download songs from Archive.org and process BPM"""
    process_archive_files()

@main.command()
@click.argument("folder", type=click.Path(exists=True))
def folder(folder):
    """Process all MP3 files in a local folder"""
    process_local_folder(folder)