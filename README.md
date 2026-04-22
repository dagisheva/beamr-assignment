# beamr-assignment

Two standalone projects:

- **[script/](script/)** — x264 QP sweep: encodes a YUV file across QP 1–51 and produces an Excel report with file size and FPS charts
- **[test/](test/)** — Selenium end-to-end test for the HEIC→JPG conversion on [heictojpg.com](https://heictojpg.com/)

## Prerequisites

- Python 3.9+
- [x264](https://www.videolan.org/developers/x264.html) on PATH (for `script/`)
- [Google Chrome](https://www.google.com/chrome/) (for `test/`)

## Setup

Run once from the repo root — sets up both projects:

```bash
python setup.py
```

This creates `script/venv` and `test/venv` with all required dependencies.

## Running

```bash
# QP analysis script
cd script
venv/bin/python run_analysis.py        # macOS / Linux
venv\Scripts\python run_analysis.py    # Windows

# Selenium test
cd test
venv/bin/python -m pytest              # macOS / Linux
venv\Scripts\python -m pytest          # Windows
```

See [script/README.md](script/README.md) and [test/README.md](test/README.md) for details.
