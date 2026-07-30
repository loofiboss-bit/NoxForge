#!/usr/bin/env python3
"""Render and verify the authentic offscreen v6 session-surface matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "design/session-surface-contract.json"
EVIDENCE_ROOT = ROOT / "docs/evidence/v6/session"
MANIFEST_PATH = EVIDENCE_ROOT / "manifest.json"
BACKGROUND = ROOT / "sddm/NoxForge/background.png"
SCENARIO_SIZE = (1920, 1080)
CHOREOGRAPHY_SIZE = (2560, 1440)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"not a PNG: {path}")
    return struct.unpack(">II", data[16:24])


def render_one(
    renderer: Path,
    destination: Path,
    surface: str,
    source: Path,
    width: int,
    height: int,
    scenario: str,
    filename: str,
    kind: str,
) -> dict[str, object]:
    output = destination / filename
    subprocess.run(
        [
            str(renderer),
            surface,
            str(source),
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
    return {
        "file": filename,
        "kind": kind,
        "surface": surface,
        "width": width,
        "height": height,
        "scenario": scenario,
        "sha256": sha256(output),
    }


def render(renderer: Path, destination: Path) -> dict[str, object]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    captures: list[dict[str, object]] = []
    surfaces = {
        name: ROOT / relative
        for name, relative in contract["surfaces"].items()
    }

    for surface, source in surfaces.items():
        for size in contract["v6ResolutionMatrix"]:
            width, height = size["width"], size["height"]
            captures.append(
                render_one(
                    renderer,
                    destination,
                    surface,
                    source,
                    width,
                    height,
                    "standard-end",
                    f"{surface}-resolution-{width}x{height}.png",
                    "resolution",
                )
            )

    for surface, scenarios in contract["v6ScenarioMatrix"].items():
        source = surfaces[surface]
        for scenario in scenarios:
            captures.append(
                render_one(
                    renderer,
                    destination,
                    surface,
                    source,
                    *SCENARIO_SIZE,
                    f"{scenario}-end",
                    f"{surface}-scenario-{scenario}.png",
                    "scenario",
                )
            )

    for surface, source in surfaces.items():
        for frame in contract["choreographyFrames"]:
            frame_name = frame["name"]
            captures.append(
                render_one(
                    renderer,
                    destination,
                    surface,
                    source,
                    *CHOREOGRAPHY_SIZE,
                    f"standard-{frame_name}",
                    f"{surface}-choreography-{frame_name}.png",
                    "choreography",
                )
            )

    policy_directories = (
        ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/splash",
        ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/logout",
        ROOT / "kwin/tabbox/io.github.loofiboss.noxforge.desktop/contents/ui",
    )
    source_paths = [
        CONTRACT_PATH,
        ROOT / "design/tokens.json",
        ROOT / "design/motion-contract.json",
        ROOT / "scripts/generate_design_system.py",
        ROOT / "scripts/render_v6_session_evidence.py",
        ROOT / "scripts/measure_v6_phase5_performance.py",
        ROOT / "tools/session_renderer.cpp",
        *surfaces.values(),
        ROOT / "sddm/NoxForge/Tokens.qml",
        *[
            directory / name
            for directory in policy_directories
            for name in ("Tokens.qml", "MotionPolicy.qml")
        ],
    ]
    return {
        "schemaVersion": 1,
        "release": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "contract": CONTRACT_PATH.relative_to(ROOT).as_posix(),
        "renderer": "tools/session_renderer.cpp",
        "kind": contract["v6EvidencePolicy"]["kind"],
        "authenticQml": True,
        "themeContext": "isolated NoxForge Plasma and icon context",
        "liveSession": contract["v6EvidencePolicy"]["qualifiesLiveSession"],
        "reviewStatus": "reviewed-offscreen",
        "sourceHashes": {
            path.relative_to(ROOT).as_posix(): sha256(path)
            for path in source_paths
        },
        "captureCount": len(captures),
        "captures": captures,
    }


def build_renderer(build: Path) -> Path:
    subprocess.run(
        [
            "cmake",
            "-S",
            str(ROOT),
            "-B",
            str(build),
            "-G",
            "Ninja",
            "-DCMAKE_BUILD_TYPE=Release",
        ],
        cwd=ROOT,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(
        ["cmake", "--build", str(build), "--target", "noxforge_session_renderer"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    return build / "noxforge_session_renderer"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when v6 session evidence drifts")
    arguments = parser.parse_args()

    with (
        tempfile.TemporaryDirectory(prefix="noxforge-v6-session-build-") as build_dir,
        tempfile.TemporaryDirectory(prefix="noxforge-v6-session-render-") as render_dir,
    ):
        rendered = Path(render_dir)
        manifest = render(build_renderer(Path(build_dir)), rendered)
        encoded = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        if arguments.check:
            drift = []
            if not MANIFEST_PATH.is_file() or MANIFEST_PATH.read_text(encoding="utf-8") != encoded:
                drift.append(MANIFEST_PATH.relative_to(ROOT).as_posix())
            for capture in manifest["captures"]:
                current = EVIDENCE_ROOT / capture["file"]
                candidate = rendered / capture["file"]
                if not current.is_file() or current.read_bytes() != candidate.read_bytes():
                    drift.append(current.relative_to(ROOT).as_posix())
            if drift:
                print("v6 session evidence drift: " + ", ".join(drift), file=sys.stderr)
                return 1
            print(f"Verified {manifest['captureCount']} authentic offscreen v6 session renders")
            return 0

        EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
        for capture in manifest["captures"]:
            shutil.copyfile(rendered / capture["file"], EVIDENCE_ROOT / capture["file"])
        MANIFEST_PATH.write_text(encoded, encoding="utf-8", newline="\n")
        print(f"Rendered {manifest['captureCount']} authentic offscreen v6 session compositions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
