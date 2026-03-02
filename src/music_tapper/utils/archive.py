# archive.py
import os
from typing import List, Optional, Union
import requests
from tqdm import tqdm
from datetime import datetime


ROWS_PER_PAGE = 100
BASE_SEARCH_URL = "https://archive.org/advancedsearch.php"
METADATA_URL = "https://archive.org/metadata"
DOWNLOAD_BASE = "https://archive.org/download"
HEADERS = {"User-Agent": "archive-downloader (educational use)"}


def build_search_query(
    text:Optional[str]="",
    subjects:Optional[Union[List[str],str]]=None,
    genres:Optional[Union[List[str],str]]=None,
    year_from:Optional[str]=None,
    year_to:Optional[str]=None,
    artist:Optional[str]=None,
    extra_subjects:Optional[str]=None,
):
    parts = [text] if text else []

    if subjects:
        if "," in subjects:
            subject_tag = [
                f'subject:"{sub.strip()}"' for sub in subjects.split(",")
            ]
        else:
            subject_tag = [f'subject:"{subjects}"']
        parts = subject_tag

    if genres:
        genres_str = " OR ".join(
            [f'"{g}"' if " " in g else g for g in genres]
        )
        parts.append(f"subject:({genres_str})")

    if extra_subjects:
        extra = " OR ".join(
            [f'"{s}"' if " " in s else s for s in extra_subjects]
        )
        parts.append(f"subject:({extra})")

    # siempre audio musical
    parts.append("mediatype:audio")
    parts.append("collection:audio_music")

    if year_from and year_to:
        if not year_from.isdigit():
            raise ValueError("Year from must be a number.")
        if not year_to.isdigit():
            raise ValueError("Year to must be a number.")
        if int(year_from) < 1921:
            raise ValueError("Year from value must higher than 1920.")
        if int(year_to) > datetime.now().year:
            raise ValueError("Year to value must lower than current year.")
        parts.append(f"year:[{year_from} TO {year_to}]")

    if artist:
        parts.append(f'creator:("{artist.lower()}")')

    # unir todo
    print(f"Joining {parts}")
    return " AND ".join(parts)


def search_items(page, query):
    params = {
        "q": query,
        "fl[]": "identifier",
        "rows": ROWS_PER_PAGE,
        "page": page,
        "output": "json",
    }
    r = requests.get(BASE_SEARCH_URL, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()["response"]

def get_mp3_files(identifier):
    r = requests.get(f"{METADATA_URL}/{identifier}", headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()

    mp3s = []
    for f in data.get("files", []):
        name = f.get("name", "")
        if name.lower().endswith(".mp3"):
            mp3s.append(name)
    return mp3s

def download_mp3(identifier, filename, dest_dir):
    url = f"{DOWNLOAD_BASE}/{identifier}/{filename}"
    local_path = os.path.join(dest_dir, filename)

    if os.path.exists(local_path):
        return local_path # already downloaded

    os.makedirs(dest_dir, exist_ok=True)
    with requests.get(url, stream=True, headers=HEADERS, timeout=60) as r:
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            print(f"Error downloading file: {filename}. Do you want to continue (Y/n):{input("Y")}")
        total = int(r.headers.get("content-length", 0))

        with open(local_path, "wb") as f, tqdm(
            total=total,
            unit="B",
            unit_scale=True,
            desc=filename,
            leave=False,
        ) as bar:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))
    return local_path
