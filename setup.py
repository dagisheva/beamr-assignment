#!/usr/bin/env python3
"""
Setup script for the beamr-assignment project.
Sets up virtual environments for both script/ and test/.
Works on Windows, macOS, and Linux.

Usage:
    python setup.py
"""

import sys
import os
import shutil
import subprocess
import venv

MIN_PYTHON = (3, 9)
ROOT = os.path.dirname(os.path.abspath(__file__))


def step(msg):
    print(f"\n==> {msg}")

def ok(msg):
    print(f"    OK: {msg}")

def warn(msg):
    print(f"    WARN: {msg}")

def fail(msg):
    print(f"    ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def check_python():
    step("Checking Python version")
    v = sys.version_info
    if (v.major, v.minor) < MIN_PYTHON:
        fail(f"Python {v.major}.{v.minor} found, but {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required.")
    ok(f"Python {v.major}.{v.minor}.{v.micro}")


def check_x264():
    step("Checking x264 (required for script/)")
    if shutil.which("x264"):
        ok(f"x264 found at {shutil.which('x264')}")
        return
    warn("x264 not found on PATH — script/run_analysis.py will not work until it is installed.")
    print("    Install options:")
    print("      macOS:   brew install x264")
    print("      Ubuntu:  sudo apt install x264")
    print("      Windows: choco install x264")
    print("               or download x264.exe from https://www.videolan.org/developers/x264.html")
    print("               and add it to PATH")


def check_chrome():
    step("Checking Google Chrome (required for test/)")
    candidates = ["google-chrome", "google-chrome-stable", "chromium-browser", "chromium"]
    if sys.platform == "darwin":
        mac_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(mac_path):
            ok(f"Chrome found at {mac_path}")
            return
    if sys.platform == "win32":
        win_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        for p in win_paths:
            if os.path.exists(p):
                ok(f"Chrome found at {p}")
                return
    for candidate in candidates:
        if shutil.which(candidate):
            ok(f"Chrome found: {shutil.which(candidate)}")
            return
    warn("Google Chrome not found — test/ will not work until it is installed.")
    print("    Download from https://www.google.com/chrome/")


def setup_venv(directory, deps=None, requirements=None):
    venv_dir = os.path.join(ROOT, directory, "venv")
    pip = os.path.join(venv_dir, "Scripts" if sys.platform == "win32" else "bin", "pip")

    if os.path.isdir(venv_dir):
        print(f"    {directory}/venv already exists, skipping creation.")
    else:
        venv.create(venv_dir, with_pip=True)
        ok(f"{directory}/venv created")

    subprocess.run([pip, "install", "--quiet", "--upgrade", "pip"], check=True)

    if deps:
        subprocess.run([pip, "install", "--quiet"] + deps, check=True)
        ok(f"installed: {', '.join(deps)}")

    if requirements:
        req_path = os.path.join(ROOT, directory, requirements)
        subprocess.run([pip, "install", "--quiet", "-r", req_path], check=True)
        ok(f"installed from {directory}/{requirements}")


def print_next_steps():
    if sys.platform == "win32":
        activate_script = r"venv\Scripts\activate"
    else:
        activate_script = "source venv/bin/activate"

    print("\nSetup complete.\n")
    print("  Run the QP analysis script:")
    print(f"    cd script && {activate_script} && python run_analysis.py\n")
    print("  Run the Selenium test:")
    print(f"    cd test  && {activate_script} && python -m pytest\n")


if __name__ == "__main__":
    check_python()
    check_x264()
    check_chrome()

    step("Setting up script/ environment")
    setup_venv("script", deps=["openpyxl"])

    step("Setting up test/ environment")
    setup_venv("test", requirements="requirements.txt")

    print_next_steps()