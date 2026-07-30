#!/usr/bin/env python3
"""Render and verify deterministic v6 Aurorae, icon, and cursor evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "design/edge-polish-contract.json"
EVIDENCE_ROOT = ROOT / "docs/evidence/v6/edge-polish"
MANIFEST_PATH = EVIDENCE_ROOT / "manifest.json"
THEME_ID = "io.github.loofiboss.noxforge.desktop"
TOKENS = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"not a PNG: {path}")
    return struct.unpack(">II", data[16:24])


def normalize(magick: str, path: Path) -> None:
    normalized = path.with_suffix(".normalized.png")
    run(
        [
            magick,
            str(path),
            "-strip",
            "-define",
            "png:exclude-chunks=date,time",
            f"PNG24:{normalized}",
        ]
    )
    normalized.replace(path)


def tile(magick: str, source: Path, target: Path, size: int, extent: int) -> None:
    run(
        [
            magick,
            "-background",
            TOKENS["colors"]["surface"],
            str(source),
            "-resize",
            f"{size}x{size}",
            "-gravity",
            "center",
            "-extent",
            f"{extent}x{extent}",
            "-strip",
            "-define",
            "png:exclude-chunks=date,time",
            f"PNG24:{target}",
        ]
    )


def fit_tile(
    magick: str,
    source: Path,
    target: Path,
    geometry: str,
    extent: str,
) -> None:
    run(
        [
            magick,
            "-background",
            TOKENS["colors"]["surface"],
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


def montage(
    magick: str,
    sources: list[Path],
    target: Path,
    columns: int,
) -> None:
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
            TOKENS["colors"]["background"],
            str(target),
        ]
    )
    normalize(magick, target)


def render_aurorae(
    magick: str,
    output: Path,
    temporary: Path,
    contract: dict[str, object],
) -> tuple[Path, list[Path]]:
    theme = ROOT / f"aurorae/{THEME_ID}"
    sources = [theme / "decoration.svg"] + [
        theme / f"{name}.svg"
        for name in contract["aurorae"]["buttons"]
    ]
    tiles = []
    for index, source in enumerate(sources):
        target = temporary / f"aurorae-{index}.png"
        if source.name == "decoration.svg":
            fit_tile(magick, source, target, "640x320", "1040x324")
        else:
            fit_tile(magick, source, target, "1024x96", "1040x112")
        tiles.append(target)
    target = output / "aurorae-states.png"
    montage(magick, tiles, target, 1)
    return target, sources


def priority_icons(contract: dict[str, object]) -> list[str]:
    groups = contract["icons"]["priority"]
    priority = [
        relative
        for group in ("panel", "systemSettings", "dolphin", "session")
        for relative in groups[group]
    ]
    if not 40 <= len(priority) <= 60 or len(priority) != len(set(priority)):
        raise RuntimeError("Phase 6 icon priority must contain 40–60 unique icons")
    return priority


def render_icons(
    magick: str,
    output: Path,
    temporary: Path,
    contract: dict[str, object],
) -> tuple[Path, list[Path], list[str]]:
    theme = ROOT / "icons/NoxForge"
    priority = priority_icons(contract)
    sizes = contract["icons"]["reviewSizes"]
    source_paths: list[Path] = []
    strips = []
    for icon_index, relative in enumerate(priority):
        icon_tiles = []
        for size in sizes:
            optical = theme / f"{size}x{size}" / relative
            source = optical if size in (16, 22) and optical.is_file() else theme / "scalable" / relative
            if not source.is_file():
                raise RuntimeError(f"missing priority icon source: {relative}")
            source_paths.append(source)
            target = temporary / f"icon-{icon_index:02d}-{size}.png"
            tile(magick, source, target, size, 52)
            icon_tiles.append(target)
        strip = temporary / f"icon-strip-{icon_index:02d}.png"
        montage(magick, icon_tiles, strip, len(sizes))
        strips.append(strip)
    target = output / "icon-priority.png"
    montage(magick, strips, target, 7)
    return target, sorted(set(source_paths)), priority


def render_cursors(
    magick: str,
    output: Path,
    temporary: Path,
    contract: dict[str, object],
) -> tuple[Path, list[Path], list[str]]:
    theme = ROOT / "cursors/NoxForge-Cursors"
    coverage = json.loads((theme / "coverage.json").read_text(encoding="utf-8"))
    canonical = coverage["canonical"]
    sizes = contract["cursors"]["physicalSizes"]
    sources = [theme / "source" / f"{name}.svg" for name in canonical]
    strips = []
    for cursor_index, source in enumerate(sources):
        cursor_tiles = []
        for size in sizes:
            target = temporary / f"cursor-{cursor_index:02d}-{size}.png"
            tile(magick, source, target, size, 64)
            cursor_tiles.append(target)
        strip = temporary / f"cursor-strip-{cursor_index:02d}.png"
        montage(magick, cursor_tiles, strip, len(sizes))
        strips.append(strip)
    target = output / "cursor-optical.png"
    montage(magick, strips, target, 8)
    return target, sources, canonical


def render(magick: str, output: Path, temporary: Path) -> dict[str, object]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    output.mkdir(parents=True, exist_ok=True)
    aurorae, aurorae_sources = render_aurorae(magick, output, temporary, contract)
    icons, icon_sources, priority = render_icons(magick, output, temporary, contract)
    cursors, cursor_sources, canonical_cursors = render_cursors(
        magick, output, temporary, contract
    )
    outputs = [aurorae, icons, cursors]

    icon_coverage_path = ROOT / "icons/NoxForge/coverage.json"
    icon_coverage = json.loads(icon_coverage_path.read_text(encoding="utf-8"))
    frozen = contract["icons"]["coverageFrozen"]
    if (
        icon_coverage["iconCount"] != frozen["scalable"]
        or icon_coverage["opticalCount"] != frozen["optical"]
        or len(icon_coverage["runtimeFixture"]) != frozen["runtimeFixture"]
    ):
        raise RuntimeError("Phase 6 icon coverage changed without a proven runtime miss")
    if priority != [
        relative
        for group in ("panel", "systemSettings", "dolphin", "session")
        for relative in icon_coverage["phase6Priority"][group]
    ]:
        raise RuntimeError("Phase 6 priority ranking drifted from icon coverage")

    cursor_coverage_path = ROOT / "cursors/NoxForge-Cursors/coverage.json"
    cursor_coverage = json.loads(cursor_coverage_path.read_text(encoding="utf-8"))
    if (
        cursor_coverage["sizes"] != contract["cursors"]["physicalSizes"]
        or cursor_coverage["animations"]["wait"] != contract["cursors"]["animation"]
        or cursor_coverage["animations"]["progress"] != contract["cursors"]["animation"]
    ):
        raise RuntimeError("Phase 6 cursor size or animation contract drift")

    sound_root = ROOT / "sounds/NoxForge"
    if tree_sha256(sound_root) != contract["sound"]["treeSha256"]:
        raise RuntimeError("Phase 6 sound theme changed without a semantic mismatch")

    source_paths = [
        CONTRACT_PATH,
        ROOT / "design/tokens.json",
        ROOT / "scripts/generate_visual_assets.py",
        ROOT / "scripts/generate_cursors.py",
        ROOT / "scripts/render_v6_edge_evidence.py",
        ROOT / f"aurorae/{THEME_ID}/{THEME_ID}rc",
        icon_coverage_path,
        cursor_coverage_path,
        ROOT / "sounds/NoxForge/coverage.json",
        *(path for path in sound_root.rglob("*") if path.is_file()),
        *aurorae_sources,
        *icon_sources,
        *cursor_sources,
    ]
    return {
        "schemaVersion": 1,
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "phase": 6,
        "kind": contract["evidence"]["kind"],
        "reviewStatus": "reviewed-offscreen",
        "liveDecoration": contract["evidence"]["liveDecoration"],
        "liveDecorationRemainsPhase7": contract["evidence"][
            "liveDecorationRemainsPhase7"
        ],
        "aurorae": {
            "buttons": contract["aurorae"]["buttons"],
            "buttonStates": contract["aurorae"]["states"],
            "windowStates": contract["aurorae"]["windowStates"],
        },
        "icons": {
            "priorityCount": len(priority),
            "priority": contract["icons"]["priority"],
            "reviewSizes": contract["icons"]["reviewSizes"],
            "coverageFrozen": frozen,
        },
        "cursors": {
            "canonicalCount": len(canonical_cursors),
            "physicalSizes": contract["cursors"]["physicalSizes"],
            "hotspotsFrozen": contract["cursors"]["hotspotsFrozen"],
            "animation": contract["cursors"]["animation"],
        },
        "sound": contract["sound"],
        "outputs": {
            (EVIDENCE_ROOT / path.name).relative_to(ROOT).as_posix(): {
                "sha256": sha256(path),
                "width": png_dimensions(path)[0],
                "height": png_dimensions(path)[1],
            }
            for path in outputs
        },
        "sourceHashes": {
            path.relative_to(ROOT).as_posix(): sha256(path)
            for path in sorted(set(source_paths))
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    magick = shutil.which("magick")
    if not magick:
        print("ImageMagick 'magick' is required", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory(prefix="noxforge-v6-edge-") as temporary_name:
        temporary = Path(temporary_name)
        generated = temporary / "evidence"
        manifest = render(magick, generated, temporary)
        encoded = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        if arguments.check:
            drift = []
            if not MANIFEST_PATH.is_file() or MANIFEST_PATH.read_text(encoding="utf-8") != encoded:
                drift.append(MANIFEST_PATH.relative_to(ROOT).as_posix())
            for relative in manifest["outputs"]:
                current = ROOT / relative
                candidate = generated / current.name
                if not current.is_file() or current.read_bytes() != candidate.read_bytes():
                    drift.append(relative)
            if drift:
                print("v6 edge-polish evidence drift: " + ", ".join(drift), file=sys.stderr)
                return 1
            print("Verified deterministic v6 edge-polish evidence")
            return 0

        EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
        for relative in manifest["outputs"]:
            target = ROOT / relative
            shutil.copyfile(generated / target.name, target)
        MANIFEST_PATH.write_text(encoded, encoding="utf-8", newline="\n")
        print("Rendered deterministic v6 edge-polish evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
