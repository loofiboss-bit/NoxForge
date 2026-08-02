#!/usr/bin/env python3
"""Validate the NoxForge v7 icon overlay and write deterministic evidence."""

from __future__ import annotations

import configparser
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "icons/NoxForge"
CONTRACT_PATH = ROOT / "design/v7-icon-contract.json"
EVIDENCE_PATH = ROOT / "docs/evidence/v7/icons/phase2.json"
LOGOUT_PATH = (
    ROOT
    / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/logout/Logout.qml"
)
CHECK = "--check" in sys.argv[1:]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fallback_source(name: str, themes: list[str]) -> tuple[str, str]:
    for theme_name in themes:
        root = Path("/usr/share/icons") / theme_name
        if not root.is_dir():
            raise RuntimeError(f"missing Fedora icon fallback directory: {root}")
        matches = sorted(
            path for path in root.rglob(f"{name}.*")
            if path.suffix.lower() in {".svg", ".svgz", ".png", ".xpm"}
        )
        if matches:
            return theme_name, matches[0].relative_to(root).as_posix()
    raise RuntimeError(f"unresolved fallback probe: {name}")


def build_evidence() -> dict[str, object]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(THEME / "index.theme", encoding="utf-8")
    inheritance = parser["Icon Theme"]["Inherits"].split(",")
    expected = contract["overlayPolicy"]["inherits"]
    if inheritance != expected:
        raise RuntimeError(f"icon inheritance drift: {inheritance!r} != {expected!r}")

    logout = LOGOUT_PATH.read_text(encoding="utf-8")
    required: list[dict[str, object]] = []
    hashes: set[str] = set()
    for entry in contract["required"]:
        name = entry["name"]
        relative = f"{entry['context']}/{name}.svg"
        path = THEME / "scalable" / relative
        if not path.is_file():
            raise RuntimeError(f"missing required NoxForge icon: {relative}")
        root = ET.parse(path).getroot()
        if root.get("viewBox") != "0 0 24 24":
            raise RuntimeError(f"invalid design grid for {relative}")
        drawable = [
            element for element in root.iter()
            if element.tag.rsplit("}", 1)[-1] in {"path", "circle", "rect", "polygon"}
        ]
        if not drawable:
            raise RuntimeError(f"blank required icon: {relative}")
        digest = sha256(path)
        if digest in hashes:
            raise RuntimeError(f"required icon is not semantically distinct: {relative}")
        hashes.add(digest)
        if name.startswith("system-") and f'iconName: "{name}"' not in logout:
            raise RuntimeError(f"Logout.qml does not request {name}")
        required.append(
            {
                "name": name,
                "relativePath": relative,
                "resolution": "NoxForge overlay",
                "sha256": digest,
                "provenance": entry["provenance"],
            }
        )

    fallbacks: list[dict[str, object]] = []
    for entry in contract["fallbackProbes"]:
        name = entry["name"]
        if (THEME / "scalable" / entry["context"] / f"{name}.svg").exists():
            raise RuntimeError(f"fallback probe unexpectedly exists in NoxForge: {name}")
        theme_name, relative = fallback_source(name, inheritance)
        fallbacks.append(
            {
                "name": name,
                "resolution": "intentional fallback",
                "resolvedTheme": theme_name,
                "resolvedRelativePath": relative,
                "provenance": entry["provenance"],
            }
        )

    sizes = contract["renderMatrix"]["logicalSizes"]
    modes = contract["renderMatrix"]["modes"]
    return {
        "schemaVersion": 1,
        "version": contract["version"],
        "phase": 2,
        "result": "passed",
        "target": contract["target"],
        "theme": contract["theme"],
        "inheritance": inheritance,
        "installedFallbackDirectories": {
            name: (Path("/usr/share/icons") / name).is_dir() for name in inheritance
        },
        "requiredCore": required,
        "fallbackProbes": fallbacks,
        "semanticHashesDistinct": True,
        "renderMatrix": contract["renderMatrix"],
        "qtProbe": {
            "ctestName": "icon-theme-resolution",
            "implementation": "tests/qt/icon_resolution_probe.cpp",
            "requiredRenderCases": (len(required) + len(fallbacks)) * len(sizes) * len(modes),
            "status": "required-by-phase-gate",
        },
        "liveApplicationEvidence": {
            "status": "pending",
            "reason": "Requires an explicitly activated disposable or real Plasma session.",
        },
        "sourceHashes": {
            "contract": sha256(CONTRACT_PATH),
            "indexTheme": sha256(THEME / "index.theme"),
            "logoutQml": sha256(LOGOUT_PATH),
        },
    }


def main() -> int:
    try:
        payload = json.dumps(build_evidence(), indent=2) + "\n"
    except (KeyError, OSError, RuntimeError, ValueError, ET.ParseError) as error:
        print(f"NoxForge v7 icon check failed: {error}", file=sys.stderr)
        return 1
    if CHECK:
        if not EVIDENCE_PATH.is_file() or EVIDENCE_PATH.read_text(encoding="utf-8") != payload:
            print("NoxForge v7 icon evidence drifted", file=sys.stderr)
            return 1
        print("NoxForge v7 icon overlay check passed")
        return 0
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(payload, encoding="utf-8", newline="\n")
    print("Wrote NoxForge v7 icon overlay evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
