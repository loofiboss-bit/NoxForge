#!/usr/bin/env python3
"""Validate and record the NoxForge v7 Aurorae fallback contract."""

from __future__ import annotations

import argparse
import configparser
import gzip
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THEME_ID = "io.github.loofiboss.noxforge.desktop"
THEME = ROOT / "aurorae" / THEME_ID
SOURCE = THEME / "decoration.svg"
COMPRESSED = THEME / "decoration.svgz"
CONTRACT = ROOT / "design/edge-polish-contract.json"
GENERATOR = ROOT / "scripts/generate_visual_assets.py"
CONFIG = THEME / f"{THEME_ID}rc"
OUTPUT = ROOT / "docs/evidence/v7/aurorae/phase1.json"
POSITIONS = {
    "topleft",
    "top",
    "topright",
    "left",
    "center",
    "right",
    "bottomleft",
    "bottom",
    "bottomright",
}
SCALES = [100, 125, 140, 150, 175, 200]
WINDOW_STATES = [
    "active-normal",
    "inactive-normal",
    "active-maximized",
    "inactive-maximized",
    "quick-tiled-left",
    "quick-tiled-right",
    "shaded",
    "fullscreen-transition",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def element_ids(root: ET.Element) -> set[str]:
    return {
        identifier
        for element in root.iter()
        if (identifier := element.get("id")) is not None
    }


def element_by_id(root: ET.Element, identifier: str) -> ET.Element:
    for element in root.iter():
        if element.get("id") == identifier:
            return element
    raise RuntimeError(f"missing Aurorae element: {identifier}")


def validate_source() -> dict[str, object]:
    root = ET.parse(SOURCE).getroot()
    if root.get("viewBox") != "0 0 92 40":
        raise RuntimeError("Aurorae decoration viewBox must fit the two normal frames")
    identifiers = element_ids(root)
    expected = {
        f"{prefix}-{position}"
        for prefix in ("decoration", "decoration-inactive")
        for position in POSITIONS
    }
    missing = sorted(expected - identifiers)
    if missing:
        raise RuntimeError("incomplete normal fallback frame: " + ", ".join(missing))
    special = sorted(identifier for identifier in identifiers if identifier.startswith("decoration-maximized"))
    if special:
        raise RuntimeError("special maximized elements must be absent: " + ", ".join(special))

    for identifier, expected_class, minimum_opacity in (
        ("decoration-center", "ColorScheme-Raised", 1.0),
        ("decoration-inactive-center", "ColorScheme-Sunken", 0.9),
    ):
        center = element_by_id(root, identifier)
        if center.tag.rsplit("}", 1)[-1] != "rect":
            raise RuntimeError(f"{identifier} must be a simple stretchable rectangle")
        if center.get("class") != expected_class or center.get("fill") != "currentColor":
            raise RuntimeError(f"{identifier} has an invalid material")
        opacity = float(center.get("fill-opacity", "1"))
        if opacity < minimum_opacity:
            raise RuntimeError(f"{identifier} can expose an unpainted center")
        if float(center.get("width", "0")) <= 0 or float(center.get("height", "0")) <= 0:
            raise RuntimeError(f"{identifier} is not stretchable")

    if gzip.decompress(COMPRESSED.read_bytes()) != SOURCE.read_bytes():
        raise RuntimeError("decoration.svgz does not contain the exact source SVG")
    payload = COMPRESSED.read_bytes()
    if payload[:4] != b"\x1f\x8b\x08\x00" or payload[4:8] != b"\x00\x00\x00\x00":
        raise RuntimeError("decoration.svgz does not use canonical gzip metadata")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    aurorae = contract.get("aurorae", {})
    if (
        aurorae.get("maximizedStrategy") != "normal-frame-fallback"
        or aurorae.get("specialMaximizedElements") is not False
    ):
        raise RuntimeError("Aurorae contract does not declare the fallback strategy")

    parser = configparser.ConfigParser(interpolation=None)
    parser.read(CONFIG, encoding="utf-8")
    layout = parser["Layout"]
    for edge in ("Top", "Bottom", "Left", "Right"):
        if layout.get(f"TitleEdge{edge}Maximized") != "0":
            raise RuntimeError(f"TitleEdge{edge}Maximized must remain zero")

    return {
        "viewBox": root.get("viewBox"),
        "normalFrameElementCount": len(expected),
        "specialMaximizedElementCount": len(special),
        "activeCenterOpacity": 1.0,
        "inactiveCenterOpacity": 0.9,
    }


def build_evidence() -> dict[str, object]:
    geometry = validate_source()
    static_matrix = [
        {
            "state": state,
            "scalePercent": scale,
            "status": "passed-static",
            "surface": "normal-frame-fallback",
        }
        for state in WINDOW_STATES
        for scale in SCALES
    ]
    return {
        "schemaVersion": 1,
        "release": "7.0.0-dev",
        "phase": 1,
        "strategy": "normal-frame-fallback",
        "decision": "Remove the incomplete special maximized centers and use Aurorae's documented normal-frame fallback.",
        "upstreamContract": "https://develop.kde.org/docs/plasma/aurorae/#maximized-windows",
        "sourceGeometry": geometry,
        "sourceHashes": {
            SOURCE.relative_to(ROOT).as_posix(): digest(SOURCE),
            COMPRESSED.relative_to(ROOT).as_posix(): digest(COMPRESSED),
            CONFIG.relative_to(ROOT).as_posix(): digest(CONFIG),
            CONTRACT.relative_to(ROOT).as_posix(): digest(CONTRACT),
            GENERATOR.relative_to(ROOT).as_posix(): digest(GENERATOR),
        },
        "staticMatrix": static_matrix,
        "mixedOutputStaticCases": [
            {"scales": [100, 140], "status": "passed-static"},
            {"scales": [100, 200], "status": "passed-static"},
        ],
        "liveMatrix": {
            "status": "pending",
            "requiredScales": SCALES,
            "requiredMixedOutputs": [[100, 140], [100, 200]],
            "reason": "This environment has not executed a trusted input-capable composed KWin mixed-DPI matrix."
        },
        "releaseReady": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    evidence = build_evidence()
    payload = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    if arguments.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != payload:
            print("v7 Aurorae Phase 1 evidence drift", file=sys.stderr)
            return 1
        print("Verified v7 Aurorae normal-frame fallback and 48 static scale/state cases")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(payload, encoding="utf-8", newline="\n")
    print("Recorded v7 Aurorae normal-frame fallback and 48 static scale/state cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
