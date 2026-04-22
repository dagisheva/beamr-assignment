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
    path = shutil.which("x264")
    if path:
        ok(f"x264 found at {path}")
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
    if sys.platform == "darwin":
        mac_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(mac_path):
            ok(f"Chrome found at {mac_path}")
            return
    if sys.platform == "win32":
        for p in [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]:
            if os.path.exists(p):
                ok(f"Chrome found at {p}")
                return
    candidates = [
        "google-chrome", "google-chrome-stable",
        "chromium-browser", "chromium",
        "/snap/bin/chromium",           # Ubuntu Snap
        "/var/lib/flatpak/exports/bin/org.chromium.Chromium",  # Flatpak
    ]
    for candidate in candidates:
        path = shutil.which(candidate) or (candidate if os.path.exists(candidate) else None)
        if path:
            ok(f"Chrome found: {path}")
            return
    warn("Google Chrome not found — test/ will not work until it is installed.")
    print("    Download from https://www.google.com/chrome/")


def pip_run(pip, args, context):
    try:
        subprocess.run([pip] + args, check=True)
    except subprocess.CalledProcessError:
        fail(f"pip failed while {context}. See output above.")


def setup_venv(directory, deps=None, requirements=None):
    venv_dir = os.path.join(ROOT, directory, "venv")
    pip = os.path.join(venv_dir, "Scripts" if sys.platform == "win32" else "bin", "pip")

    fresh = False
    if os.path.isdir(venv_dir):
        if not os.path.exists(pip):
            fail(
                f"{directory}/venv exists but pip is missing (broken environment). "
                f"Delete {directory}/venv and re-run."
            )
        print(f"    {directory}/venv already exists, skipping creation.")
    else:
        try:
            venv.create(venv_dir, with_pip=True)
        except Exception as e:
            fail(
                f"Failed to create {directory}/venv: {e}\n"
                "    On Debian/Ubuntu, make sure python3-venv is installed:\n"
                "      sudo apt install python3-venv"
            )
        if not os.path.exists(pip):
            fail(
                f"venv created but pip is missing in {directory}/venv.\n"
                "    On Debian/Ubuntu, install the missing package:\n"
                "      sudo apt install python3-venv"
            )
        ok(f"{directory}/venv created")
        fresh = True

    if fresh:
        pip_run(pip, ["install", "--upgrade", "pip"], "upgrading pip")

    if deps:
        pip_run(pip, ["install"] + deps, f"installing {', '.join(deps)}")
        ok(f"installed: {', '.join(deps)}")

    if requirements:
        req_path = os.path.join(ROOT, directory, requirements)
        if not os.path.exists(req_path):
            fail(f"{directory}/{requirements} not found.")
        pip_run(pip, ["install", "-r", req_path], f"installing from {requirements}")
        ok(f"installed from {directory}/{requirements}")

    return os.path.join(venv_dir, "Scripts" if sys.platform == "win32" else "bin", "python")


def smoke_test(python, imports, directory):
    step(f"Smoke-testing {directory}/ imports")
    for module in imports:
        try:
            subprocess.run([python, "-c", f"import {module}"], check=True, capture_output=True)
            ok(f"import {module}")
        except subprocess.CalledProcessError:
            fail(f"'import {module}' failed in {directory}/venv — try deleting {directory}/venv and re-running.")


def print_next_steps():
    if sys.platform == "win32":
        script_py = r"script\venv\Scripts\python"
        test_py   = r"test\venv\Scripts\python"
    else:
        script_py = "script/venv/bin/python"
        test_py   = "test/venv/bin/python"

    print("\nSetup complete.\n")
    print("  Run the QP analysis script:")
    print(f"    cd script && {script_py} run_analysis.py\n")
    print("  Run the Selenium test:")
    print(f"    cd test && {test_py} -m pytest\n")


if __name__ == "__main__":
    check_python()
    check_x264()
    check_chrome()

    step("Setting up script/ environment")
    script_python = setup_venv("script", deps=["openpyxl"])

    step("Setting up test/ environment")
    test_python = setup_venv("test", requirements="requirements.txt")

    smoke_test(script_python, ["openpyxl"], "script")
    smoke_test(test_python, ["selenium", "pytest"], "test")

    print_next_steps()
