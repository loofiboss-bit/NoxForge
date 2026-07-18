#!/usr/bin/env python3
"""Render the editable NoxForge wallpaper source at the release resolution."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "wallpapers/NoxForge/contents/source/NoxForge.svg"
OUTPUT = ROOT / "wallpapers/NoxForge/contents/images/2560x1440.png"


def main() -> int:
    magick = shutil.which("magick")
    if not magick:
        print("ImageMagick 'magick' is required to render the wallpaper", file=sys.stderr)
        return 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [magick, "-background", "none", str(SOURCE), "-resize", "2560x1440!", "-strip", f"PNG24:{OUTPUT}"],
        check=True,
    )
    print(f"Rendered {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
