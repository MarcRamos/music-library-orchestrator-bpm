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
    """
    Download, analyze, and organize MP3 files from archive.org based on a query.

    This function iterates over search results from the Internet Archive,
    downloads each MP3 file, allows the user to measure its BPM via an
    interactive UI, updates metadata, renames the file, and stores the
    results in a CSV database and a BPM-based folder structure.

    Parameters
    ----------
    query : str
        Search query string in archive.org advanced search syntax.

    Notes
    -----
    - The function keeps track of already processed items using a CSV store.
    - Each downloaded MP3 is temporarily saved under ``download/raw``.
    - BPM is measured interactively using :func:`measure_bpm_ui`.
    - Files are renamed and moved into a BPM-based folder using
      :func:`normalize_mp3_name_meta` and :func:`bpm_folder`.
    - Metadata (artist, title, BPM, etc.) is appended to a CSV via
      :func:`append_entry`.

    User Interaction
    ----------------
    During processing, the BPM UI allows the user to:
    - Tap BPM using the space bar
    - Save BPM with ENTER
    - Skip a track
    - Cancel the entire pipeline

    Side Effects
    ------------
    - Downloads files from archive.org
    - Writes MP3 files to disk
    - Modifies MP3 metadata (BPM tag)
    - Moves/renames files into a library folder
    - Appends entries to a CSV database

    Raises
    ------
    RuntimeError
        If download or metadata processing fails unexpectedly.

    Examples
    --------
    >>> query = 'subject:"1930s" AND subject:(Jazz OR Swing)'
    >>> process_archive_files(query)
    """
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
    """
    Process local MP3 files to measure BPM and organize them into a library.

    This function scans a folder for MP3 files that do not already contain a
    BPM prefix in their filename (i.e., files not starting with "(<number>)"),
    then opens an interactive UI to measure BPM, updates metadata, renames
    the file, and moves it into a BPM-based output folder.

    Parameters
    ----------
    folder_path : str
        Path to the folder containing MP3 files to process.
    out_folder : str, optional
        Destination root folder where processed files will be stored,
        organized by BPM ranges. Default is "library/".

    Notes
    -----
    - Files whose names start with ``(<digits>)`` are skipped, assuming they
      have already been processed.
    - BPM is measured interactively using :func:`measure_bpm_ui`.
    - Files are renamed and moved according to their BPM using
      :func:`normalize_mp3_name_meta` and :func:`bpm_folder`.
    - Metadata is stored in a CSV database using :func:`append_entry`.

    User Interaction
    ----------------
    During BPM measurement, the user can:
    - Tap BPM with SPACE
    - Save BPM with ENTER
    - Skip a track
    - Cancel processing entirely

    Side Effects
    ------------
    - Reads MP3 files from disk
    - Modifies MP3 metadata (BPM tag)
    - Moves/renames files into BPM-based folders
    - Appends entries to a CSV database

    Examples
    --------
    >>> process_local_folder("E:/Music/Rock and roll/1950s")
    """
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


import click


@click.group()
def main():
    """🎧 Music Library BPM Orchestrator

    Download swing/jazz tracks from archive.org, measure BPM interactively,
    and organize your local music library automatically.
    """
    pass


def _split_csv(value):
    """Convert comma-separated string into list (or return None)."""
    if value is None:
        return None
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    return value


@main.command()
@click.option(
    "--text",
    help="Free text search (e.g. song title or keywords).",
)
@click.option(
    "--artist",
    help="Artist or creator name (e.g. 'Count Basie').",
)
@click.option(
    "--genres",
    help="Comma-separated genres (e.g. 'Jazz,Swing,Big Band').",
)
@click.option(
    "--subjects",
    help="Comma-separated subjects/tags from archive.org.",
)
@click.option(
    "--year-from",
    type=int,
    help="Start year (e.g. 1930).",
)
@click.option(
    "--year-to",
    type=int,
    help="End year (e.g. 1945).",
)
def download(text, artist, genres, subjects, year_from, year_to):
    """
    Download songs from archive.org, measure BPM and store them locally.

    This command performs the full pipeline:

    Download → BPM tapping UI → tagging → renaming → classification → CSV log
    """

    query = build_search_query(
        text=text,
        artist=artist,
        genres=_split_csv(genres),
        subjects=_split_csv(subjects),
        year_from=year_from,
        year_to=year_to,
    )

    click.echo(f"🔎 Query:\n{query}\n")

    process_archive_files(query)


@main.command(name="from-folder")
@click.argument("local_folder", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--out",
    default="library/",
    show_default=True,
    help="Output folder where processed files will be stored.",
)
def from_folder(local_folder, out):
    """
    Process MP3 files from a local folder using BPM tapping UI.

    Only files without a BPM prefix like "(120)" will be processed.
    """

    click.echo(f"📁 Processing folder: {local_folder}")
    click.echo(f"📦 Output library: {out}\n")

    process_local_folder(local_folder, out_folder=out)