from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TBPM
import os

def save_bpm_to_mp3(mp3_path, bpm):
    audio = MP3(mp3_path, ID3=ID3)
    audio.tags.add(TBPM(text=str(bpm)))
    audio.save()

def sanitize(text):
    text = "".join(c for c in text if c not in r'<>:"/\|?*')
    return " ".join(w.capitalize() for w in text.split())

def normalize_mp3(path, dest_dir):
    audio = MP3(path)
    artist = audio.get("TPE1", [""])[0]
    title = audio.get("TIT2", [""])[0]
    bpm = audio.get("TBPM", [""])[0]
    duration = round(audio.info.length, 2)

    artist = sanitize(str(artist))
    title = sanitize(str(title))

    new_name = f"({bpm}) {artist} - {title}.mp3"
    
    os.makedirs(dest_dir, exist_ok=True)
    new_path = os.path.join(dest_dir, new_name)

    audio.save()
    os.rename(path, new_path)
    return {
        "filename": os.path.basename(new_path), 
        "duration": duration,
        "artist": artist,
        "title": title,
        "bpm": bpm
    }