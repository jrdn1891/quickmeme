from __future__ import annotations

import subprocess
from pathlib import Path


def copy_to_clipboard(png_path: Path) -> None:
    script = (
        f'set the clipboard to (read (POSIX file "{png_path}") as «class PNGf»)'
    )
    subprocess.run(["osascript", "-e", script], check=True)


def open_in_preview(png_path: Path) -> None:
    subprocess.run(["open", str(png_path)], check=True)
