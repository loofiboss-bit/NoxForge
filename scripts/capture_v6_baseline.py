#!/usr/bin/env python3
"""Capture and verify the immutable v5 visual baseline used by NoxForge v6."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "docs/evidence/v6/baseline"
MANIFEST_PATH = EVIDENCE_ROOT / "manifest.json"
REVIEWED_BASELINE = "6a113e71980d106c38a2bbdece6df171c0ae9ed3"
QT_PAGES = ("controls", "data", "menu", "states", "stress")
SCALES = (("100", "1.0"), ("140", "1.4"))
SESSION_SURFACES = {
    "sddm": "sddm/NoxForge/Main.qml",
    "splash": "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/splash/Splash.qml",
    "logout": "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/logout/Logout.qml",
    "tabbox": "kwin/tabbox/io.github.loofiboss.noxforge.desktop/contents/ui/Switcher.qml",
}
PLASMA_ASSETS = {
    "panel": "widgets/panel-background.svg",
    "tasks": "widgets/tasks.svg",
    "popup": "widgets/background.svg",
    "tooltip": "widgets/tooltip.svg",
    "notification": "dialogs/background.svg",
}


def run(
    command: list[str],
    *,
    env: dict[str, str] | None = None,
    capture: bool = False,
) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=capture,
        text=capture,
    )
    return result.stdout.strip() if capture else ""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"not a PNG: {path}")
    return struct.unpack(">II", data[16:24])


def version_line(command: list[str]) -> str:
    try:
        return run(command, capture=True).splitlines()[0]
    except (FileNotFoundError, subprocess.CalledProcessError, IndexError):
        return "unavailable"


def toolchain() -> dict[str, str]:
    fedora = Path("/etc/fedora-release")
    return {
        "operatingSystem": fedora.read_text(encoding="utf-8").strip()
        if fedora.is_file()
        else "unavailable",
        "python": version_line(["python3", "--version"]),
        "gcc": version_line(["g++", "--version"]),
        "cmake": version_line(["cmake", "--version"]),
        "ninja": version_line(["ninja", "--version"]),
        "qt": version_line(["qmake6", "-query", "QT_VERSION"]),
        "frameworks": version_line(
            ["rpm", "-q", "kf6-kcoreaddons", "--qf", "%{VERSION}"]
        ),
        "rpm": version_line(["rpm", "--version"]),
        "rpmlint": version_line(["rpmlint", "--version"]),
        "plasma": version_line(["plasmashell", "--version"]),
        "kwin": version_line(["kwin_wayland", "--version"]),
    }


def load_artwork_renderer():
    path = ROOT / "scripts/render_artwork_evidence.py"
    spec = importlib.util.spec_from_file_location("noxforge_artwork_evidence", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load scripts/render_artwork_evidence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_png(magick: str, source: Path, target: Path) -> None:
    run(
        [
            magick,
            str(source),
            "-strip",
            "-define",
            "png:exclude-chunks=date,time",
            f"PNG24:{target}",
        ]
    )


def render_baseline(destination: Path) -> list[dict[str, object]]:
    magick = shutil.which("magick")
    if not magick:
        raise RuntimeError("ImageMagick 'magick' is required")

    build = ROOT / "build/v6-phase0"
    run(["cmake", "-S", str(ROOT), "-B", str(build), "-G", "Ninja"])
    run(
        [
            "cmake",
            "--build",
            str(build),
            "--target",
            "noxforge_widget_gallery",
            "noxforge_session_renderer",
            "noxforge_style",
        ]
    )
    gallery = build / "noxforge_widget_gallery"
    session_renderer = build / "noxforge_session_renderer"
    plugin_path = build / "plugins"
    captures: list[dict[str, object]] = []

    for page in QT_PAGES:
        for label, scale in SCALES:
            output = destination / f"qt-{page}-{label}pct.png"
            env = {
                **os.environ,
                "QT_QPA_PLATFORM": "offscreen",
                "QT_PLUGIN_PATH": str(plugin_path),
                "QT_SCALE_FACTOR": scale,
            }
            run([str(gallery), f"--page={page}", str(output)], env=env)
            captures.append(capture_entry(output, "qt", page, label))

    plasma_theme = ROOT / "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop"
    for label, scale in SCALES:
        tiles: list[Path] = []
        for index, (surface, relative) in enumerate(PLASMA_ASSETS.items()):
            tile = destination / f".plasma-{label}-{index}-{surface}.png"
            percent = str(round(float(scale) * 100))
            run(
                [
                    magick,
                    "-background",
                    "none",
                    str(plasma_theme / relative),
                    "-resize",
                    f"{percent}%",
                    "-strip",
                    f"PNG32:{tile}",
                ]
            )
            tiles.append(tile)
        raw = destination / f".plasma-shell-{label}pct.png"
        output = destination / f"plasma-shell-{label}pct.png"
        run(
            [
                magick,
                "montage",
                *map(str, tiles),
                "-tile",
                "5x1",
                "-geometry",
                "320x240+8+8",
                "-background",
                "#0E1318",
                str(raw),
            ]
        )
        normalize_png(magick, raw, output)
        captures.append(capture_entry(output, "plasma", "shell", label))
        for path in (*tiles, raw):
            path.unlink()

    background = ROOT / "sddm/NoxForge/background.png"
    for surface, relative in SESSION_SURFACES.items():
        output = destination / f"session-{surface}-2560x1440.png"
        run(
            [
                str(session_renderer),
                surface,
                str(ROOT / relative),
                str(background),
                str(output),
                "2560",
                "1440",
                "standard",
                str(ROOT),
            ],
            env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
        )
        captures.append(capture_entry(output, "session", surface, "100"))

    artwork = load_artwork_renderer()
    artwork_output = destination / ".artwork"
    artwork_temp = destination / ".artwork-temp"
    artwork_temp.mkdir()
    artwork.render(magick, artwork_output, artwork_temp)
    artwork_names = {
        "artwork-brand-wallpaper.png": "brand-wallpaper.png",
        "artwork-icons.png": "icons.png",
        "artwork-cursors.png": "cursors.png",
    }
    for source_name, target_name in artwork_names.items():
        target = destination / target_name
        shutil.copyfile(artwork_output / source_name, target)
        captures.append(capture_entry(target, "artwork", target.stem, "100"))
    shutil.rmtree(artwork_output)
    shutil.rmtree(artwork_temp)
    return sorted(captures, key=lambda entry: str(entry["file"]))


def capture_entry(path: Path, layer: str, surface: str, scale: str) -> dict[str, object]:
    width, height = png_dimensions(path)
    return {
        "file": path.name,
        "layer": layer,
        "surface": surface,
        "scalePercent": int(scale),
        "width": width,
        "height": height,
        "sha256": sha256(path),
        "status": "reviewed-v5-baseline",
        "v6Result": "pending",
    }


def v5_evidence_hashes() -> list[dict[str, str]]:
    root = ROOT / "docs/evidence/v5"
    return [
        {
            "file": path.relative_to(ROOT).as_posix(),
            "sha256": sha256(path),
        }
        for path in sorted(root.rglob("*"))
        if path.is_file()
    ]


def write_manifest(captures: list[dict[str, object]]) -> None:
    manifest = {
        "schemaVersion": 1,
        "release": "6.0.0-dev",
        "capturedOn": "2026-07-30",
        "reviewedBaseline": {
            "branch": "main",
            "commit": REVIEWED_BASELINE,
            "stableRelease": "v5.0.0",
            "stableCommit": "c979515e6bb99f0201e630be269bb7ecc097c35c",
            "trackedWorktreeChanges": False,
        },
        "toolchain": toolchain(),
        "evidencePolicy": {
            "authenticOffscreenOutput": True,
            "interactiveOrLiveEvidence": False,
            "v5ResultsPromotedToV6": False,
            "initialV6Result": "pending",
        },
        "v5Evidence": v5_evidence_hashes(),
        "captures": captures,
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def verify() -> None:
    if not MANIFEST_PATH.is_file():
        raise RuntimeError("v6 baseline manifest is missing")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest["reviewedBaseline"]["commit"] != REVIEWED_BASELINE:
        raise RuntimeError("v6 baseline commit drift")
    policy = manifest["evidencePolicy"]
    if policy["interactiveOrLiveEvidence"] or policy["v5ResultsPromotedToV6"]:
        raise RuntimeError("v5 offscreen evidence was promoted to v6 live evidence")
    if manifest["v5Evidence"] != v5_evidence_hashes():
        raise RuntimeError("v5 evidence hash drift")
    expected = 10 + 2 + 4 + 3
    captures = manifest["captures"]
    if len(captures) != expected:
        raise RuntimeError(f"expected {expected} v6 baseline captures")
    for capture in captures:
        path = EVIDENCE_ROOT / capture["file"]
        if not path.is_file() or sha256(path) != capture["sha256"]:
            raise RuntimeError(f"v6 baseline capture drift: {capture['file']}")
        if list(png_dimensions(path)) != [capture["width"], capture["height"]]:
            raise RuntimeError(f"v6 baseline dimensions drift: {capture['file']}")
        if capture["v6Result"] != "pending":
            raise RuntimeError(f"v6 baseline result was prematurely promoted: {capture['file']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    arguments = parser.parse_args()

    if arguments.check:
        verify()
        print("Verified 19 immutable v5 baseline captures for NoxForge v6")
        return 0

    head = run(["git", "rev-parse", "HEAD"], capture=True)
    if head != REVIEWED_BASELINE:
        raise RuntimeError(
            f"refusing to capture v6 baseline from {head}; expected {REVIEWED_BASELINE}"
        )
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="noxforge-v6-baseline-") as temporary:
        generated = Path(temporary)
        captures = render_baseline(generated)
        for capture in captures:
            shutil.copyfile(generated / str(capture["file"]), EVIDENCE_ROOT / str(capture["file"]))
    write_manifest(captures)
    verify()
    print("Captured 19 immutable v5 baseline references for NoxForge v6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
