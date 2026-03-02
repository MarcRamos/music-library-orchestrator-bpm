# archive.py
import os
import requests
from tqdm import tqdm


SEARCH_QUERY = (
    'subject:"1930s" AND subject:(Jazz OR Swing OR "Big Band") '
    'AND mediatype:audio '
    'AND collection:audio_music '
    'AND year:[1927 TO 1945] '
    'AND creator:(johnny hodges orchestra)'
)
ROWS_PER_PAGE = 100
BASE_SEARCH_URL = "https://archive.org/advancedsearch.php"
METADATA_URL = "https://archive.org/metadata"
DOWNLOAD_BASE = "https://archive.org/download"
HEADERS = {"User-Agent": "archive-downloader (educational use)"}

def search_items(page):
    params = {
        "q": SEARCH_QUERY,
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
        r.raise_for_status()
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
# ================= MAIN =================