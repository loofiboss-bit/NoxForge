#!/usr/bin/env python3
"""Render deterministic wallpaper, SDDM, and preview variants from the editable source."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKENS = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))
SOURCES = {
    "16:9": ROOT / "wallpapers/NoxForge/contents/source/NoxForge.svg",
    "ultrawide": ROOT / "wallpapers/NoxForge/contents/source/NoxForge-Ultrawide.svg",
}
OUTPUTS = (
    ("16:9", 1920, 1080),
    ("16:9", 2560, 1440),
    ("16:9", 3840, 2160),
    ("ultrawide", 3440, 1440),
)


def render(
    magick: str,
    source: Path,
    destination: Path,
    width: int,
    height: int,
    *,
    dim: bool = False,
) -> None:
    command = [
        magick,
        "-background", "none",
        str(source),
        "-resize", f"{width}x{height}!",
    ]
    if dim:
        command += ["-fill", TOKENS["colors"]["background"], "-colorize", "58"]
    command += [
        "-strip",
        "-define", "png:exclude-chunks=date,time",
        f"PNG24:{destination}",
    ]
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when rendered files drift")
    args = parser.parse_args()
    magick = shutil.which("magick")
    if not magick:
        print("ImageMagick 'magick' is required to render the wallpaper", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="noxforge-wallpaper-") as temporary:
        temp = Path(temporary)
        rendered: list[tuple[Path, Path]] = []
        for composition, width, height in OUTPUTS:
            generated = temp / f"{width}x{height}.png"
            render(magick, SOURCES[composition], generated, width, height)
            rendered.append((generated, ROOT / f"wallpapers/NoxForge/contents/images/{width}x{height}.png"))
        sddm_background = temp / "sddm-background.png"
        render(magick, SOURCES["16:9"], sddm_background, 2560, 1440, dim=True)
        rendered.append((sddm_background, ROOT / "sddm/NoxForge/background.png"))
        look_preview = temp / "look-preview.png"
        render(magick, SOURCES["16:9"], look_preview, 960, 540)
        rendered.append((look_preview, ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/previews/fullscreenpreview.png"))

        drift = [target for generated, target in rendered if not target.is_file() or target.read_bytes() != generated.read_bytes()]
        if args.check:
            if drift:
                print("Wallpaper renderer drift: " + ", ".join(str(path.relative_to(ROOT)) for path in drift), file=sys.stderr)
                return 1
            print(f"Verified {len(rendered)} deterministic wallpaper artifacts")
            return 0
        for generated, target in rendered:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(generated, target)
        print(f"Rendered {len(rendered)} wallpaper, SDDM, and preview artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
