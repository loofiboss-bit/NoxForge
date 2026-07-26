#!/usr/bin/env python3
"""Render and verify the authentic Phase 5 QML composition matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "design/session-surface-contract.json"
EVIDENCE_ROOT = ROOT / "docs/evidence/v5/session"
MANIFEST_PATH = ROOT / "docs/evidence/v5/session-surfaces.json"
BACKGROUND = ROOT / "sddm/NoxForge/background.png"


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"not a PNG: {path}")
    return struct.unpack(">II", data[16:24])


def render(renderer: Path, destination: Path) -> dict[str, object]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    captures: list[dict[str, object]] = []
    for surface, relative in contract["surfaces"].items():
        for composition in contract["compositions"]:
            width = composition["width"]
            height = composition["height"]
            scenario = composition["scenario"]
            filename = f"{surface}-{width}x{height}-{scenario}.png"
            output = destination / filename
            subprocess.run(
                [
                    str(renderer),
                    surface,
                    str(ROOT / relative),
                    str(BACKGROUND),
                    str(output),
                    str(width),
                    str(height),
                    scenario,
                    str(ROOT),
                ],
                cwd=ROOT,
                env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
                check=True,
            )
            if png_dimensions(output) != (width, height):
                raise RuntimeError(f"wrong render dimensions: {filename}")
            captures.append(
                {
                    "file": f"session/{filename}",
                    "surface": surface,
                    "width": width,
                    "height": height,
                    "scenario": scenario,
                    "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                }
            )
    return {
        "schemaVersion": 1,
        "contract": str(CONTRACT_PATH.relative_to(ROOT)),
        "renderer": "tools/session_renderer.cpp",
        "authenticQml": True,
        "themeContext": "isolated NoxForge Plasma and icon context",
        "liveSession": False,
        "reviewStatus": "reviewed",
        "captures": captures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--renderer", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    renderer = arguments.renderer.resolve()
    if not renderer.is_file():
        raise SystemExit(f"session renderer not found: {renderer}")

    with tempfile.TemporaryDirectory(prefix="noxforge-session-evidence-") as temporary:
        rendered = Path(temporary)
        manifest = render(renderer, rendered)
        encoded = json.dumps(manifest, indent=2) + "\n"
        if arguments.check:
            if not MANIFEST_PATH.is_file() or MANIFEST_PATH.read_text(encoding="utf-8") != encoded:
                raise SystemExit("session evidence manifest drift")
            for capture in manifest["captures"]:
                current = ROOT / "docs/evidence/v5" / capture["file"]
                candidate = rendered / Path(capture["file"]).name
                if not current.is_file() or current.read_bytes() != candidate.read_bytes():
                    raise SystemExit(f"session render drift: {current.relative_to(ROOT)}")
            print("Verified 16 authentic Phase 5 QML composition renders")
            return 0

        EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
        for capture in manifest["captures"]:
            source = rendered / Path(capture["file"]).name
            shutil.copyfile(source, ROOT / "docs/evidence/v5" / capture["file"])
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST_PATH.write_text(encoded, encoding="utf-8")
    print("Rendered 16 authentic Phase 5 QML compositions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
