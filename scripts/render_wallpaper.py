#!/usr/bin/env python3
"""Render deterministic PNG24 wallpaper, KDE Dynamic images_dark, SDDM, and preview variants."""

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
VARIANT_SOURCES = {
    "NoxForge": {
        "16:9": ROOT / "wallpapers/NoxForge/contents/source/NoxForge.svg",
        "ultrawide": ROOT / "wallpapers/NoxForge/contents/source/NoxForge-Ultrawide.svg",
    },
    "NoxForge-Quiet": {
        "16:9": ROOT / "wallpapers/NoxForge-Quiet/contents/source/NoxForge.svg",
        "ultrawide": ROOT / "wallpapers/NoxForge-Quiet/contents/source/NoxForge-Ultrawide.svg",
    },
    "NoxForge-Ultrawide": {
        "16:9": ROOT / "wallpapers/NoxForge-Ultrawide/contents/source/NoxForge.svg",
        "ultrawide": ROOT / "wallpapers/NoxForge-Ultrawide/contents/source/NoxForge-Ultrawide.svg",
    },
    "NoxForge-Obsidian": {
        "16:9": ROOT / "wallpapers/NoxForge-Obsidian/contents/source/NoxForge.svg",
        "ultrawide": ROOT / "wallpapers/NoxForge-Obsidian/contents/source/NoxForge-Ultrawide.svg",
    },
    "NoxForge-Obsidian-Ultrawide": {
        "16:9": ROOT / "wallpapers/NoxForge-Obsidian-Ultrawide/contents/source/NoxForge.svg",
        "ultrawide": ROOT / "wallpapers/NoxForge-Obsidian-Ultrawide/contents/source/NoxForge-Ultrawide.svg",
    },
}
OUTPUTS = (
    ("16:9", 1920, 1080),
    ("16:9", 2560, 1440),
    ("16:9", 2560, 1600),
    ("16:9", 3840, 2160),
    ("16:9", 3840, 2400),
    ("ultrawide", 3440, 1440),
    ("ultrawide", 5120, 1440),
)
WALLPAPER_VARIANTS = (
    ("NoxForge", False),
    ("NoxForge-Quiet", True),
    ("NoxForge-Ultrawide", False),
    ("NoxForge-Obsidian", False),
    ("NoxForge-Obsidian-Ultrawide", False),
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
    """Render true 24-bit PNG24 without PNG8 256-color quantization banding."""
    command = [
        magick,
        "-background", "none",
        str(source),
        "-resize", f"{width}x{height}^",
        "-gravity", "center",
        "-extent", f"{width}x{height}",
    ]
    if dim:
        command += ["-fill", TOKENS["colors"]["background"], "-colorize", "58"]
    command += [
        "-depth", "8",
        "-strip",
        "-define", "png:exclude-chunks=date,time",
        "-define", "png:compression-level=9",
        "-define", "png:compression-filter=5",
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
            for variant, dim in WALLPAPER_VARIANTS:
                generated = temp / f"{variant}-{width}x{height}.png"
                render(
                    magick,
                    VARIANT_SOURCES[variant][composition],
                    generated,
                    width,
                    height,
                    dim=dim,
                )
                rendered.append((generated, ROOT / f"wallpapers/{variant}/contents/images/{width}x{height}.png"))
                if variant == "NoxForge-Obsidian":
                    # Populate Plasma 6 Dynamic Wallpaper images_dark/ inside primary NoxForge package
                    rendered.append((generated, ROOT / f"wallpapers/NoxForge/contents/images_dark/{width}x{height}.png"))
        sddm_background = temp / "sddm-background.png"
        render(magick, SOURCES["16:9"], sddm_background, 2560, 1440, dim=True)
        rendered.append((sddm_background, ROOT / "sddm/NoxForge/background.png"))
        sddm_obsidian = temp / "sddm-obsidian-background.png"
        render(magick, VARIANT_SOURCES["NoxForge-Obsidian"]["16:9"], sddm_obsidian, 2560, 1440, dim=True)
        rendered.append((sddm_obsidian, ROOT / "sddm/NoxForgeObsidian/background.png"))
        look_preview = temp / "look-preview.png"
        render(magick, SOURCES["16:9"], look_preview, 960, 540)
        rendered.append((look_preview, ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/previews/fullscreenpreview.png"))
        look_obsidian_preview = temp / "look-obsidian-preview.png"
        render(magick, VARIANT_SOURCES["NoxForge-Obsidian"]["16:9"], look_obsidian_preview, 960, 540)
        rendered.append((look_obsidian_preview, ROOT / "look-and-feel/io.github.loofiboss.noxforge.obsidian.desktop/contents/previews/fullscreenpreview.png"))

        drift = [target for generated, target in rendered if not target.is_file() or target.read_bytes() != generated.read_bytes()]
        if args.check:
            if drift:
                print("Wallpaper renderer drift: " + ", ".join(str(path.relative_to(ROOT)) for path in drift[:12]), file=sys.stderr)
                return 1
            print(f"Verified {len(rendered)} deterministic PNG24 wallpaper artifacts")
            return 0
        for generated, target in rendered:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(generated, target)
        print(f"Rendered {len(rendered)} PNG24 wallpaper, images_dark, SDDM, and preview artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
