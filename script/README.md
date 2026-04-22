# QP Analysis Script

## Overview

This script analyzes how the Quantization Parameter (QP) of the x264 video encoder
affects file size and encoding performance (FPS).

It runs x264 with QP values from 1 to 51 on a provided uncompressed YUV video file
and generates an Excel report with a data table and charts.

## What is QP?

QP (Quantization Parameter) controls how aggressively video is compressed:
- Low QP (e.g. 1) = minimal compression, large file, best quality
- High QP (e.g. 51) = maximum compression, small file, worst quality

## Prerequisites

- Python 3.9+
- x264 encoder:
  - macOS: `brew install x264`
  - Ubuntu: `sudo apt install x264`
  - Windows: скачать исполняемый файл с [videolan.org](https://www.videolan.org/developers/x264.html) и добавить в PATH
- Python packages: `openpyxl`

## Setup

From the repo root, run the shared setup script (works on Windows, macOS, Linux):

```bash
python setup.py
```

This creates `script/venv` and installs all dependencies. To set up manually:

```bash
python -m venv venv

# macOS / Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install openpyxl
```

## Usage

Place `foreman-cif.yuv` in the script directory, then run:

```bash
python run_analysis.py
```

## Configuration

The following parameters can be adjusted at the top of `run_analysis.py`:

| Constant | Default | Description |
|---|---|---|
| `QP_RANGE` | `range(1, 52)` | QP values to test |
| `RUNS_PER_QP` | `3` | Encoding runs per QP (median FPS is taken) |
| `RESOLUTION` | `352x288` | Input video resolution |

## Output

- `encoded_files/` — encoded .264 files for each QP value
- `qp_analysis_report.xlsx` — Excel report containing:
  - Data table: QP, File Size (KB), FPS (median)
  - Chart: File Size vs QP
  - Chart: Encoding Speed (FPS) vs QP

## Key observations from the results

- **File size decreases exponentially** as QP increases, with the steepest drop
  between QP 1–15. Beyond QP ~25, further size reduction is minimal.
- **Encoding speed (FPS) generally increases** with higher QP, since less
  computational work is needed for coarser quantization.
- FPS measurements show variance due to CPU load fluctuations.
  Each QP is encoded 3 times and the median FPS is reported.
  File size is deterministic and does not require multiple runs.

## AI assistance

This script was developed with the help of Claude (Anthropic).
Conversation thread: https://claude.ai/share/e24b1550-e5c5-44ba-9b64-92874ea4333f
