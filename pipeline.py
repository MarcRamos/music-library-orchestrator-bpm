import time
import os
import argparse
import glob

from archive import search_items, get_mp3_files, download_mp3
from audio_utils import normalize_mp3, save_bpm_to_mp3
from bpm_ui import measure_bpm_ui
from csv_store import load_processed_set, append_entry
from bpm_organizer import bpm_folder


processed = load_processed_set()
print(processed)
page = 1
total_items = None

DEST_DIR = os.path.join("download", "raw")
os.makedirs(DEST_DIR, exist_ok=True)

# Add or remove query fields as you wish
# It's more useful to do the query in the archive.org page and then
# update these values accordingly.

SEARCH_QUERY = (
    'subject:"1930s" AND subject:(Jazz OR Swing OR "Big Band") '
    'AND mediatype:audio '
    'AND collection:audio_music '
    'AND year:[1927 TO 1945] '
    'AND creator:"johnny hodges orchestra'
)

ROWS_PER_PAGE = 100
BASE_SEARCH_URL = "https://archive.org/advancedsearch.php"
METADATA_URL = "https://archive.org/metadata"
DOWNLOAD_BASE = "https://archive.org/download"

HEADERS = {"User-Agent": "archive-downloader (educational use)"}

# ================= HELPERS =================


def process_archive_files():
    while True:
        response = search_items(
            SEARCH_QUERY, 
            ROWS_PER_PAGE,
            BASE_SEARCH_URL,
            HEADERS,
            page
        )

        if total_items is None:
            total_items = response["numFound"]
            print(f"📀 Items found: {total_items}")

        items = response["docs"]
        if not items:
            break

        print(f"➡️ Page {page}, items: {len(items)}")

        for item in items:
            identifier = item["identifier"]
            mp3s = get_mp3_files(identifier, METADATA_URL, HEADERS)
            for mp3 in mp3s:

                mp3_path = download_mp3(
                    identifier, mp3, DOWNLOAD_BASE, HEADERS, DEST_DIR
                )
                time.sleep(0.5)  # be nice to archive.org
                bpm = measure_bpm_ui(mp3_path)
                if bpm is None:
                    print("⏭️ Skipped by the user")
                    continue
                
                save_bpm_to_mp3(mp3_path, bpm)
                object_mp3 = normalize_mp3(
                    mp3_path, os.path.join("library", bpm_folder(bpm))
                )
                object_mp3.update({"id": identifier})
                append_entry(**object_mp3)
                print("🎶 Successfully processed\n")


def process_local_folder(folder_path):
    """Processes all MP3s in a folder using the BPM UI"""
    mp3_files = glob.glob(os.path.join(folder_path, "*.mp3"))
    for mp3_path in mp3_files:
        print(f"🎵 Processing {os.path.basename(mp3_path)}")
        bpm = measure_bpm_ui(mp3_path)
        if bpm is None:
            print("⏭️ Skipped by the user")
            continue
        save_bpm_to_mp3(mp3_path, bpm)
        object_mp3 = normalize_mp3(mp3_path, os.path.join("library", bpm_folder(bpm)))
        object_mp3.update({"id": None})
        append_entry(**object_mp3)
        print("✅ Successfully processed\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Full pipeline: download songs from Archive.org, " \
        "measure BPM, and organize into folders"
    )
    parser.add_argument(
        "--folder", type=str, default=None,
        help="Process all MP3s in the specified folder using the BPM UI"
    )

    args = parser.parse_args()

    if args.folder:
        if not os.path.isdir(args.folder):
            print(f"❌ Folder {args.folder} does not exist")
        else:
            process_local_folder(args.folder)
    else:
        print("🚀 Starting Archive.org download and BPM pipeline…")
        process_archive_files()