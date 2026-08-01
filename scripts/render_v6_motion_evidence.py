#!/usr/bin/env python3
"""Render deterministic 0/50/100 percent native Qt motion evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/v6/qt-motion"
MANIFEST = EVIDENCE / "manifest.json"
STATES = {
    "state-000.png": 0.0,
    "state-050.png": 0.5,
    "state-100.png": 1.0,
}
SOURCES = (
    ROOT / "CMakeLists.txt",
    ROOT / "design/motion-contract.json",
    ROOT / "src/style/noxforgepalette.h",
    ROOT / "src/style/noxforgemotion.h",
    ROOT / "src/style/noxforgemotion.cpp",
    ROOT / "src/style/noxforgestyle.h",
    ROOT / "src/style/noxforgestyle.cpp",
    ROOT / "tools/motion_state_renderer.cpp",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(destination: Path) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="noxforge-v6-motion-build-") as temporary:
        build = Path(temporary)
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
            [
                "cmake",
                "--build",
                str(build),
                "--target",
                "noxforge_style",
                "noxforge_motion_state_renderer",
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        destination.mkdir(parents=True, exist_ok=True)
        runtime = build / "runtime"
        home = runtime / "home"
        config = runtime / "config"
        cache = runtime / "cache"
        for path in (home, config, cache):
            path.mkdir(parents=True)
        environment = {
            "PATH": os.environ.get("PATH", "/usr/bin"),
            "HOME": str(home),
            "XDG_CONFIG_HOME": str(config),
            "XDG_CACHE_HOME": str(cache),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "QT_QPA_PLATFORM": "offscreen",
            "QT_PLUGIN_PATH": str(build / "plugins"),
        }
        for filename, progress in STATES.items():
            subprocess.run(
                [
                    str(build / "noxforge_motion_state_renderer"),
                    str(destination / filename),
                    str(progress),
                ],
                cwd=ROOT,
                env=environment,
                check=True,
            )

    return {
        "schemaVersion": 1,
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "phase": 3,
        "kind": "authentic-offscreen-native-qt-motion",
        "liveEvidence": False,
        "deterministicProgress": [0, 50, 100],
        "sources": {
            path.relative_to(ROOT).as_posix(): sha256(path)
            for path in SOURCES
        },
        "renders": [
            {
                "progressPercent": round(progress * 100),
                "path": f"docs/evidence/v6/qt-motion/{filename}",
                "sha256": sha256(destination / filename),
                "width": 960,
                "height": 540,
            }
            for filename, progress in STATES.items()
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when motion evidence drifts")
    arguments = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="noxforge-v6-motion-output-") as temporary:
        generated = Path(temporary)
        manifest = render(generated)
        manifest_text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        if arguments.check:
            drift = [
                f"docs/evidence/v6/qt-motion/{filename}"
                for filename in STATES
                if not (EVIDENCE / filename).is_file()
                or (EVIDENCE / filename).read_bytes() != (generated / filename).read_bytes()
            ]
            if not MANIFEST.is_file() or MANIFEST.read_text(encoding="utf-8") != manifest_text:
                drift.append("docs/evidence/v6/qt-motion/manifest.json")
            if drift:
                print("v6 motion evidence drift: " + ", ".join(drift), file=sys.stderr)
                return 1
            print("Verified deterministic 0/50/100 percent native Qt motion evidence")
            return 0

        EVIDENCE.mkdir(parents=True, exist_ok=True)
        for filename in STATES:
            shutil.copyfile(generated / filename, EVIDENCE / filename)
        MANIFEST.write_text(manifest_text, encoding="utf-8", newline="\n")
        print("Rendered deterministic 0/50/100 percent native Qt motion evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
