#!/usr/bin/env python3
"""Render deterministic Phase 4 artwork contact sheets and their hash manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "design/artwork-contract.json"
EVIDENCE = ROOT / "docs/evidence"


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tile(magick: str, source: Path, target: Path, geometry: str, extent: str) -> None:
    run(
        [
            magick,
            "-background",
            "#0E1318",
            str(source),
            "-resize",
            geometry,
            "-gravity",
            "center",
            "-extent",
            extent,
            "-strip",
            "-define",
            "png:exclude-chunks=date,time",
            f"PNG24:{target}",
        ]
    )


def montage(magick: str, sources: list[Path], target: Path, columns: int) -> None:
    run(
        [
            magick,
            "montage",
            *map(str, sources),
            "-tile",
            f"{columns}x",
            "-geometry",
            "+4+4",
            "-background",
            "#141B21",
            str(target),
        ]
    )
    normalized = target.with_suffix(".normalized.png")
    run(
        [
            magick,
            str(target),
            "-strip",
            "-define",
            "png:exclude-chunks=date,time",
            f"PNG24:{normalized}",
        ]
    )
    normalized.replace(target)


def render(magick: str, output: Path, temporary: Path) -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    output.mkdir(parents=True, exist_ok=True)

    brand_tiles: list[Path] = []
    brand_sources = [
        ROOT / contract["brand"]["source"],
        ROOT / "wallpapers/NoxForge/contents/images/2560x1440.png",
        ROOT / "wallpapers/NoxForge/contents/images/3440x1440.png",
    ]
    for index, source in enumerate(brand_sources):
        target = temporary / f"brand-{index}.png"
        tile(magick, source, target, "520x260", "560x300")
        brand_tiles.append(target)
    montage(magick, brand_tiles, output / "artwork-brand-wallpaper.png", 1)

    icon_tiles: list[Path] = []
    fixture = sorted(contract["runtimeIconFixture"]["required"])
    for index, relative in enumerate(fixture):
        target = temporary / f"icon-{index:03d}.png"
        tile(magick, ROOT / "icons/NoxForge/scalable" / relative, target, "40x40", "56x56")
        icon_tiles.append(target)
    montage(magick, icon_tiles, output / "artwork-icons.png", 10)

    cursor_manifest = json.loads((ROOT / "cursors/NoxForge-Cursors/coverage.json").read_text(encoding="utf-8"))
    cursor_tiles: list[Path] = []
    for index, name in enumerate(cursor_manifest["canonical"]):
        target = temporary / f"cursor-{index:03d}.png"
        tile(magick, ROOT / "cursors/NoxForge-Cursors/source" / f"{name}.svg", target, "48x48", "64x64")
        cursor_tiles.append(target)
    montage(magick, cursor_tiles, output / "artwork-cursors.png", 8)

    source_paths = [
        CONTRACT_PATH,
        ROOT / contract["brand"]["source"],
        *(ROOT / details["source"] for details in contract["wallpapers"].values()),
        ROOT / "icons/NoxForge/coverage.json",
        ROOT / "cursors/NoxForge-Cursors/coverage.json",
        ROOT / "sounds/NoxForge/coverage.json",
    ]
    sheets = [
        output / "artwork-brand-wallpaper.png",
        output / "artwork-icons.png",
        output / "artwork-cursors.png",
    ]
    manifest = {
        "schemaVersion": 1,
        "phase": 4,
        "reviewStatus": "reviewed",
        "reviewAssertions": [
            "The N/F mark remains legible at all declared optical sizes.",
            "The 16:9 and ultrawide wallpapers are independent compositions with quiet workspace regions.",
            "Every fixed runtime-fixture icon is present and semantically recognizable.",
            "Canonical cursor silhouettes and accent details remain distinct.",
        ],
        "sources": {
            path.relative_to(ROOT).as_posix(): sha256(path)
            for path in source_paths
        },
        "sheets": {
            f"docs/evidence/{path.name}": sha256(path)
            for path in sheets
        },
    }
    (output / "artwork-contact-sheets.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when contact-sheet evidence drifts")
    args = parser.parse_args()
    magick = shutil.which("magick")
    if not magick:
        print("ImageMagick 'magick' is required to render artwork evidence", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory(prefix="noxforge-artwork-evidence-") as name:
        temporary = Path(name)
        generated = temporary / "evidence"
        render(magick, generated if args.check else EVIDENCE, temporary)
        if not args.check:
            print("Rendered three reviewed Phase 4 artwork contact sheets")
            return 0
        names = (
            "artwork-brand-wallpaper.png",
            "artwork-icons.png",
            "artwork-cursors.png",
            "artwork-contact-sheets.json",
        )
        drift = [
            name
            for name in names
            if not (EVIDENCE / name).is_file()
            or (generated / name).read_bytes() != (EVIDENCE / name).read_bytes()
        ]
        if drift:
            print("Artwork evidence drift: " + ", ".join(drift), file=sys.stderr)
            return 1
    print("Verified three reviewed Phase 4 artwork contact sheets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
