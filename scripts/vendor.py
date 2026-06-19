"""Vendor meme templates from a local memegen clone into the package.

Source: https://github.com/jacebrowning/memegen (MIT). Run:

    git clone --depth 1 https://github.com/jacebrowning/memegen /tmp/memegen
    uv run python scripts/vendor.py /tmp/memegen

Copies each template's config.yml and one static base image (png > jpg > gif),
dropping alternate style images we don't use.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

DEST = Path(__file__).parent.parent / "src" / "quickmeme" / "templates"


def _base_image(directory: Path) -> Path | None:
    for ext in ("png", "jpg", "jpeg", "gif"):
        candidate = directory / f"default.{ext}"
        if candidate.exists():
            return candidate
    return None


def main(source_root: str) -> int:
    source = Path(source_root) / "templates"
    if not source.is_dir():
        print(f"No templates/ under {source_root}", file=sys.stderr)
        return 1

    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)

    count = 0
    for directory in sorted(source.iterdir()):
        if not directory.is_dir() or directory.name.startswith("_"):
            continue
        config = directory / "config.yml"
        image = _base_image(directory)
        if not config.exists() or image is None:
            continue
        out = DEST / directory.name
        out.mkdir()
        shutil.copy2(config, out / "config.yml")
        shutil.copy2(image, out / image.name)
        count += 1

    print(f"Vendored {count} templates into {DEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/memegen-inspect"))
