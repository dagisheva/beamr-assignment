# Automated UI Test — heictojpg.com

## Overview

Selenium WebDriver test for the HEIC to JPG conversion feature on [heictojpg.com](https://heictojpg.com/).
Follows the Page Object Model (POM) design pattern.

## What is tested

`test_compression_reduces_file_size` — end-to-end happy path:

1. Navigate to heictojpg.com
2. Upload a HEIC file via drag-and-drop onto the drop zone
3. Wait for conversion to complete
4. Assert the page reports a positive reduction percentage
5. Assert output size shown on the page is smaller than input size
6. Click Download, wait for the zip archive to arrive
7. Extract the zip and assert the file inside has a `.jpg` extension
8. Assert the compressed file size on disk is smaller than the original HEIC

## Project structure

```
test/
├── conftest.py                  # Chrome WebDriver fixture (supports headless mode)
├── pytest.ini                   # pytest configuration
├── requirements.txt             # Python dependencies
├── pages/
│   ├── base_page.py             # Base class with common Selenium helpers
│   └── heictojpg_page.py        # Page Object for heictojpg.com
├── tests/
│   └── test_heic_compression.py # Test suite
└── test_data/
    └── IMG_5415.HEIC            # Input file (uncompressed HEIC photo)
```

## Prerequisites

- Python 3.12+
- Google Chrome installed
- `chromedriver` is managed automatically via `webdriver-manager`

## Setup

From the repo root, run the shared setup script (works on Windows, macOS, Linux):

```bash
python setup.py
```

This creates `test/venv` and installs all dependencies. To set up manually:

```bash
python -m venv venv

# macOS / Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

## Running the tests

```bash
pytest
```

Headless mode (for CI):

```bash
HEADLESS=1 pytest
```

## Notes

- The test file `test_data/IMG_5415.HEIC` must be an uncompressed photo.
  If the file is missing, the test is skipped with a clear message.
- The downloaded file arrives as a zip (`jpegmini_optimized.zip`);
  the test extracts it automatically and verifies the `.jpg` inside.
- No account or login is required — heictojpg.com works without registration.

## Design decisions

**Drag-and-drop via JavaScript**

Selenium's `ActionChains` cannot drag files from the OS filesystem into the
browser — it only supports dragging between DOM elements. To simulate a real
drop, the file is read in Python, base64-encoded, and passed to a JavaScript
snippet that reconstructs a `File` object and dispatches `dragenter`,
`dragover`, and `drop` events on the drop zone. This exercises the same event
handlers as a genuine user drag-and-drop.
