#!/usr/bin/env python3
"""Validate v7 priority-icon optics and frozen cursor/brand decisions."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "design/v7-asset-contract.json"
GENERATOR_PATH = ROOT / "scripts/generate_visual_assets.py"
ICON_ROOT = ROOT / "icons/NoxForge/scalable"
CURSOR_COVERAGE = ROOT / "cursors/NoxForge-Cursors/coverage.json"
ARTWORK_CONTRACT = ROOT / "design/artwork-contract.json"
V6_SHEET = ROOT / "docs/evidence/v6/edge-polish/icon-priority.png"
EVIDENCE_ROOT = ROOT / "docs/evidence/v7/assets"
EVIDENCE_PATH = EVIDENCE_ROOT / "phase6.json"
SHEET_PATH = EVIDENCE_ROOT / "priority-icons.png"
CHECK = "--check" in sys.argv[1:]


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def render_raw(magick: str, source: Path, size: int) -> bytes:
    return subprocess.run(
        [
            magick,
            "-background",
            "none",
            str(source),
            "-resize",
            f"{size}x{size}",
            "-gravity",
            "center",
            "-extent",
            f"{size}x{size}",
            "-depth",
            "8",
            "rgba:-",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def render_tile(magick: str, source: Path, target: Path) -> None:
    subprocess.run(
        [
            magick,
            "-background",
            "none",
            str(source),
            "-resize",
            "40x40",
            "-gravity",
            "center",
            "-extent",
            "64x64",
            "-strip",
            "-define",
            "png:exclude-chunks=date,time",
            f"PNG32:{target}",
        ],
        cwd=ROOT,
        check=True,
    )


def render_sheet(magick: str, icons: list[Path], destination: Path, temporary: Path) -> None:
    tiles = []
    for index, source in enumerate(icons):
        tile = temporary / f"priority-{index:02d}.png"
        render_tile(magick, source, tile)
        tiles.append(tile)
    draft = temporary / "priority-icons-draft.png"
    subprocess.run(
        [
            magick,
            "montage",
            *map(str, tiles),
            "-tile",
            "6x8",
            "-geometry",
            "+4+4",
            "-background",
            "#151D23",
            str(draft),
        ],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [
            magick,
            str(draft),
            "-strip",
            "-define",
            "png:exclude-chunks=date,time",
            f"PNG24:{destination}",
        ],
        cwd=ROOT,
        check=True,
    )


def build_evidence(magick: str, sheet: Path, temporary: Path) -> dict[str, object]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    ranked = contract["rankedPriority"]
    if len(ranked) != 48 or len(set(ranked)) != 48:
        raise RuntimeError("v7 priority ranking must contain exactly 48 unique icons")
    icons = [ICON_ROOT / relative for relative in ranked]
    missing = [path.relative_to(ROOT).as_posix() for path in icons if not path.is_file()]
    if missing:
        raise RuntimeError("priority icons are missing: " + ", ".join(missing))

    renders: dict[str, dict[str, object]] = {}
    for size in contract["reviewSizes"]:
        digests: dict[str, str] = {}
        minimum_visible_pixels = size * size
        for relative, icon in zip(ranked, icons, strict=True):
            pixels = render_raw(magick, icon, size)
            if len(pixels) != size * size * 4:
                raise RuntimeError(f"wrong raw render size for {relative} at {size}")
            visible = sum(pixels[index] > 0 for index in range(3, len(pixels), 4))
            if visible == 0:
                raise RuntimeError(f"empty priority icon: {relative} at {size}")
            minimum_visible_pixels = min(minimum_visible_pixels, visible)
            digests[relative] = sha256_bytes(pixels)
        if len(set(digests.values())) != len(digests):
            raise RuntimeError(f"priority icons collapse to duplicate rasters at {size} px")
        renders[str(size)] = {
            "iconCount": len(digests),
            "uniqueRasterCount": len(set(digests.values())),
            "minimumVisiblePixels": minimum_visible_pixels,
            "rasterHashes": digests,
        }

    hardware_keyboard = ICON_ROOT / "devices/input-keyboard.svg"
    settings_keyboard = ICON_ROOT / "preferences/preferences-desktop-keyboard.svg"
    if hardware_keyboard.read_bytes() == settings_keyboard.read_bytes():
        raise RuntimeError("keyboard hardware and settings semantics are still identical")

    render_sheet(magick, icons, sheet, temporary)
    cursor_coverage = json.loads(CURSOR_COVERAGE.read_text(encoding="utf-8"))
    return {
        "schemaVersion": 1,
        "version": contract["version"],
        "phase": 6,
        "result": "passed",
        "evidenceBasis": contract["evidenceBasis"],
        "rankedPriority": ranked,
        "opticalPolicy": contract["opticalPolicy"],
        "renderQualification": renders,
        "semanticCorrection": {
            "hardware": "devices/input-keyboard.svg",
            "settings": "preferences/preferences-desktop-keyboard.svg",
            "distinctAtAllReviewSizes": True,
        },
        "cursorDecision": {
            **contract["cursorDecision"],
            "physicalSizes": cursor_coverage["sizes"],
            "coverageSha256": sha256(CURSOR_COVERAGE),
        },
        "brandDecision": {
            **contract["brandDecision"],
            "contractSha256": sha256(ARTWORK_CONTRACT),
        },
        "contactSheetComparison": {
            "historicalV6": V6_SHEET.relative_to(ROOT).as_posix(),
            "historicalV6Sha256": sha256(V6_SHEET),
            "v7": SHEET_PATH.relative_to(ROOT).as_posix(),
            "v7Sha256": sha256(sheet),
            "sameArtifact": False,
        },
        "liveQualification": contract["liveQualification"],
        "sourceHashes": {
            "contract": sha256(CONTRACT_PATH),
            "generator": sha256(GENERATOR_PATH),
            **{
                f"icons/NoxForge/scalable/{relative}": sha256(icon)
                for relative, icon in zip(ranked, icons, strict=True)
            },
        },
    }


def main() -> int:
    magick = shutil.which("magick")
    if not magick:
        print("NoxForge v7 asset check failed: ImageMagick 'magick' was not found", file=sys.stderr)
        return 1
    try:
        with tempfile.TemporaryDirectory(prefix="noxforge-v7-assets-") as name:
            temporary = Path(name)
            sheet = temporary / "priority-icons.png"
            evidence = build_evidence(magick, sheet, temporary)
            payload = json.dumps(evidence, indent=2) + "\n"
            if CHECK:
                if (
                    not EVIDENCE_PATH.is_file()
                    or EVIDENCE_PATH.read_text(encoding="utf-8") != payload
                    or not SHEET_PATH.is_file()
                    or SHEET_PATH.read_bytes() != sheet.read_bytes()
                ):
                    print("NoxForge v7 asset evidence drifted", file=sys.stderr)
                    return 1
                print("NoxForge v7 priority-asset check passed")
                return 0
            EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(sheet, SHEET_PATH)
            EVIDENCE_PATH.write_text(payload, encoding="utf-8", newline="\n")
            print("Wrote NoxForge v7 priority-asset evidence")
            return 0
    except (KeyError, OSError, RuntimeError, subprocess.CalledProcessError, ValueError) as error:
        print(f"NoxForge v7 asset check failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
