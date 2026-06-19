from __future__ import annotations

import os
import platform
import shutil
import subprocess
import time
from pathlib import Path

OUT_DIR = Path.home() / ".quickmeme" / "out"


def output_path(template_id: str) -> Path:
    return OUT_DIR / f"{template_id}-{time.strftime('%Y%m%d-%H%M%S')}.png"


def copy_to_clipboard(png_path: Path) -> bool:
    """Copy a PNG onto the system clipboard. Returns False if no tool is available."""
    system = platform.system()
    if system == "Darwin":
        script = f'set the clipboard to (read (POSIX file "{png_path}") as «class PNGf»)'
        subprocess.run(["osascript", "-e", script], check=True)
        return True
    if system == "Windows":
        ps = (
            "Add-Type -AssemblyName System.Windows.Forms,System.Drawing;"
            f"[System.Windows.Forms.Clipboard]::SetImage("
            f"[System.Drawing.Image]::FromFile('{png_path}'))"
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
        return True
    if shutil.which("wl-copy"):
        with open(png_path, "rb") as f:
            subprocess.run(["wl-copy", "--type", "image/png"], stdin=f, check=True)
        return True
    if shutil.which("xclip"):
        subprocess.run(
            ["xclip", "-selection", "clipboard", "-t", "image/png", "-i", str(png_path)],
            check=True,
        )
        return True
    return False


def open_file(png_path: Path) -> bool:
    """Open a file in the OS default viewer. Returns False if not possible."""
    system = platform.system()
    if system == "Darwin":
        subprocess.run(["open", str(png_path)], check=True)
        return True
    if system == "Windows":
        os.startfile(str(png_path))  # type: ignore[attr-defined]
        return True
    if shutil.which("xdg-open"):
        subprocess.run(["xdg-open", str(png_path)], check=True)
        return True
    return False
