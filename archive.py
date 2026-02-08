# archive.py
import os
import requests
from tqdm import tqdm




def search_items(
        search_query, 
        rows_per_page,
        base_search_url,
        headers,
        page
    ):
    params = {
        "q": search_query,
        "fl[]": "identifier",
        "rows": rows_per_page,
        "page": page,
        "output": "json",
    }
    r = requests.get(base_search_url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()["response"]

def get_mp3_files(identifier, metadata_url, headers):
    r = requests.get(f"{metadata_url}/{identifier}", headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()

    mp3s = []
    for f in data.get("files", []):
        name = f.get("name", "")
        if name.lower().endswith(".mp3"):
            mp3s.append(name)
    return mp3s

def download_mp3(identifier, filename, download_base, head, dest_dir):
    url = f"{download_base}/{identifier}/{filename}"
    local_path = os.path.join(dest_dir, filename)

    if os.path.exists(local_path):
        return local_path # already downloaded

    os.makedirs(dest_dir, exist_ok=True)
    with requests.get(url, stream=True, headers=head, timeout=60) as r:
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