# 🎧 Music Library BPM Orchestrator

Small CLI tool to **download, analyze, tag and organize MP3 music files by BPM**.  
It integrates with Archive.org and provides a manual BPM tap interface using pygame.

---

## ✨ Features

- 🔎 Search and download music from Archive.org
- 🎵 Manual BPM tapping interface (keyboard or buttons)
- 🏷️ Write BPM metadata into MP3 files (ID3 tag)
- 🗂️ Automatically rename and organize files into BPM ranges
- 📚 Process local folders of MP3 files
- ⚡ CLI built with Click

---

## 🚀 Installation

Install from [pypi.org](https://pypi.org/project/music-tapper/) or [pypi.org](https://pypi.org/project/music-tapper/) in your environment.

To test that it was installed properly run:

```bash
music-tapper
```


## 🚀 Installation (local dev)

This project uses **Poetry**.

```bash
poetry install
```

Run commands inside the virtual environment:

```bash
poetry run music-tapper --help
```

🎛️ CLI Usage
1. Download music from Archive.org

Supports filters:

- --text
- --artist
- --genres
- --subjects
- --year-from
- --year-to

```bash
poetry run music-tapper download \
    --text "swing jazz" \
    --artist "count basie" \
    --year-from 1930 \
    --year-to 1945
```

2. Process local folder

```bash
poetry run music-tapper from-folder ./my_mp3s
```

This will:
- Open BPM tap UI
- Save BPM to MP3 metadata
- Rename file to (BPM) Artist - Title.mp3
- Move it into /library/<bpm-range>/

🎹 BPM Tap Controls

Inside the UI:
| Key / Button | Action        |
| ------------ | ------------- |
| `SPACE`      | Tap BPM       |
| `ENTER`      | Save BPM      |
| `ESC`        | Exit          |
| `[> ]`       | Play          |
| `[\|\|]`     | Stop          |
| `[R]`        | Restart track |
| `[>>]`       | Skip track    |


📁 Output Structure

```
library/
├── 100-140/
├── 140-180/
├── 180-200/
└── 200-260/
```

Each file is renamed automatically using metadata.

🧠 Dependencies

- pygame – playback & UI
- mutagen – ID3 tagging
- requests – Archive.org API
- click – CLI

⚠️ Notes

- Designed for educational and personal use
- Be respectful with Archive.org bandwidth (the tool already throttles requests)
- Metadata quality depends on source files

🛠️ Future Ideas

- 🌐 Web UI (Flask + React)
- 🔎 BPM database browser
- 🤖 Automatic BPM detection
- 🧾 Export to CSV / JSON