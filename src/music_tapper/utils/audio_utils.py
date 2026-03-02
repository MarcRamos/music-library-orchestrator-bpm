from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TBPM
import os

def save_bpm_to_mp3(mp3_path, bpm):
    """
    Write BPM metadata to an MP3 file using ID3 tags.

    Parameters
    ----------
    mp3_path : str
        Path to the MP3 file where the BPM tag will be written.
    bpm : int or str
        Beats per minute value to store in the TBPM ID3 frame.

    Returns
    -------
    None

    Notes
    -----
    This function uses the mutagen library to modify ID3 tags in-place.
    If the file does not already contain ID3 tags, they will be created.
    """
    audio = MP3(mp3_path, ID3=ID3)
    audio.tags.add(TBPM(text=str(bpm)))
    audio.save()

def sanitize(text):
    """
    Sanitize a string for safe filesystem usage and normalize capitalization.

    Parameters
    ----------
    text : str
        Input string to sanitize.

    Returns
    -------
    str
        Cleaned string with forbidden filesystem characters removed and each
        word capitalized.

    Notes
    -----
    The following characters are removed: ``<>:"/\\|?*``.
    The resulting string is normalized using title-style capitalization.
    """
    text = "".join(c for c in text if c not in r'<>:"/\|?*')
    return " ".join(w.capitalize() for w in text.split())

def normalize_mp3_name_meta(path, dest_dir):
    """
    Rename and move an MP3 file based on its metadata and return its metadata.

    The output filename format is:
        ``(BPM) Artist - Title.mp3``

    Parameters
    ----------
    path : str
        Path to the source MP3 file.
    dest_dir : str
        Destination directory where the renamed file will be moved.

    Returns
    -------
    dict
        Dictionary containing normalized metadata with keys:

        - ``filename`` : str
            New filename.
        - ``duration`` : float
            Audio duration in seconds.
        - ``artist`` : str
            Sanitized artist name.
        - ``title`` : str
            Sanitized title.
        - ``bpm`` : str
            BPM value extracted from metadata.

    Notes
    -----
    - Artist and title are sanitized to ensure filesystem-safe filenames.
    - The destination directory is created if it does not exist.
    - The original file is moved (renamed), not copied.
    """
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