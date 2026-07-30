#!/usr/bin/env python3
"""Render authentic offscreen v6 Global Theme and SDDM previews."""

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
THEME_ID = "io.github.loofiboss.noxforge.desktop"
OUTPUTS = {
    "globalTheme": ROOT / f"look-and-feel/{THEME_ID}/contents/previews/preview.png",
    "sddm": ROOT / "sddm/NoxForge/preview.png",
}
SOURCE_PATHS = (
    ROOT / "tools/sddm_renderer.cpp",
    ROOT / "sddm/NoxForge/Main.qml",
    ROOT / "sddm/NoxForge/background.png",
    ROOT / "sddm/NoxForge/NoxForgeLockup.svg",
    ROOT / "wallpapers/NoxForge/contents/images/2560x1440.png",
)
MANIFEST = ROOT / "docs/evidence/v6/brand/preview-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(destination: Path) -> dict[str, object]:
    magick = shutil.which("magick")
    if not magick:
        raise RuntimeError("ImageMagick 'magick' is required")
    with tempfile.TemporaryDirectory(prefix="noxforge-v6-preview-build-") as temporary:
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
                "noxforge_sddm_renderer",
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        destination.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                magick,
                str(ROOT / "wallpapers/NoxForge/contents/images/2560x1440.png"),
                "-resize",
                "480x380^",
                "-gravity",
                "center",
                "-extent",
                "480x380",
                "-strip",
                "-define",
                "png:exclude-chunks=date,time",
                f"PNG24:{destination / 'global-theme-preview.png'}",
            ],
            cwd=ROOT,
            check=True,
        )
        subprocess.run(
            [
                str(build / "noxforge_sddm_renderer"),
                str(ROOT / "sddm/NoxForge/Main.qml"),
                str(ROOT / "sddm/NoxForge/background.png"),
                str(destination / "sddm-preview.png"),
            ],
            cwd=ROOT,
            env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
            check=True,
        )

    rendered = {
        "globalTheme": destination / "global-theme-preview.png",
        "sddm": destination / "sddm-preview.png",
    }
    return {
        "schemaVersion": 1,
        "release": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "phase": 2,
        "kind": "authentic-offscreen-preview",
        "liveEvidence": False,
        "sources": {
            path.relative_to(ROOT).as_posix(): sha256(path)
            for path in SOURCE_PATHS
        },
        "outputs": {
            name: {
                "path": OUTPUTS[name].relative_to(ROOT).as_posix(),
                "sha256": sha256(path),
            }
            for name, path in rendered.items()
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when previews drift")
    arguments = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="noxforge-v6-preview-output-") as temporary:
        generated = Path(temporary)
        manifest = render(generated)
        manifest_text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        rendered = {
            "globalTheme": generated / "global-theme-preview.png",
            "sddm": generated / "sddm-preview.png",
        }
        if arguments.check:
            drift = [
                OUTPUTS[name].relative_to(ROOT).as_posix()
                for name, source in rendered.items()
                if not OUTPUTS[name].is_file()
                or OUTPUTS[name].read_bytes() != source.read_bytes()
            ]
            if (
                not MANIFEST.is_file()
                or MANIFEST.read_text(encoding="utf-8") != manifest_text
            ):
                drift.append(MANIFEST.relative_to(ROOT).as_posix())
            if drift:
                print("v6 preview drift: " + ", ".join(drift), file=sys.stderr)
                return 1
            print("Verified authentic offscreen v6 previews")
            return 0

        for name, source in rendered.items():
            OUTPUTS[name].parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, OUTPUTS[name])
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(manifest_text, encoding="utf-8", newline="\n")
        print("Rendered authentic offscreen v6 Global Theme and SDDM previews")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
