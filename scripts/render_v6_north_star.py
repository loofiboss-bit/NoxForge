#!/usr/bin/env python3
"""Render and verify the phase-one Kinetic Precision north-star prototypes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/evidence/v6/north-star"
BASELINE = ROOT / "docs/evidence/v6/baseline"
BASELINE_MAP = {
    "north-star-qt.png": "qt-controls-100pct.png",
    "north-star-plasma.png": "plasma-shell-100pct.png",
    "north-star-session.png": "session-sddm-2560x1440.png",
    "north-star-tabbox.png": "session-tabbox-2560x1440.png",
    "north-star-brand-wallpaper.png": "brand-wallpaper.png",
    "north-star-motion-storyboard.png": "session-splash-2560x1440.png",
}
SCORES = {
    "hierarchy": 5,
    "stateClarity": 5,
    "cohesion": 4,
    "branding": 4,
    "density": 4,
    "motion": 4,
    "accessibility": 4,
    "fallbackBehavior": 4,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        **kwargs,
    )


def dimensions(path: Path) -> tuple[int, int]:
    result = run(
        ["identify", "-format", "%w %h", str(path)],
        capture_output=True,
    )
    width, height = result.stdout.split()
    return int(width), int(height)


def difference_ratio(first: Path, second: Path) -> float:
    result = subprocess.run(
        ["compare", "-metric", "RMSE", str(first), str(second), "null:"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.strip() or "ImageMagick comparison failed")
    match = re.search(r"\((0(?:\.\d+)?|1(?:\.0+)?)\)", result.stderr)
    if not match:
        raise RuntimeError(f"unexpected ImageMagick metric: {result.stderr.strip()}")
    return float(match.group(1))


def render(destination: Path) -> dict[str, object]:
    for command in ("cmake", "ninja", "identify", "compare"):
        if shutil.which(command) is None:
            raise RuntimeError(f"required phase-one render tool was not found: {command}")
    with tempfile.TemporaryDirectory(prefix="noxforge-v6-north-star-build-") as temporary:
        build = Path(temporary)
        run(
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
            stdout=subprocess.DEVNULL,
        )
        run(
            ["cmake", "--build", str(build), "--target", "noxforge_north_star_renderer"],
            stdout=subprocess.DEVNULL,
        )
        env = os.environ.copy()
        env["QT_QPA_PLATFORM"] = "offscreen"
        subprocess.run(
            [str(build / "noxforge_north_star_renderer"), str(destination)],
            cwd=ROOT,
            env=env,
            check=True,
        )

    baseline_manifest = json.loads(
        (BASELINE / "manifest.json").read_text(encoding="utf-8")
    )
    baseline_entries = {
        entry["file"]: entry for entry in baseline_manifest["captures"]
    }
    comparisons: list[dict[str, object]] = []
    for target_name, baseline_name in BASELINE_MAP.items():
        target = destination / target_name
        baseline = BASELINE / baseline_name
        target_size = dimensions(target)
        baseline_size = dimensions(baseline)
        if target_size != baseline_size:
            raise RuntimeError(
                f"{target_name} is {target_size}, baseline {baseline_name} is {baseline_size}"
            )
        difference = difference_ratio(target, baseline)
        if difference == 0:
            raise RuntimeError(f"{target_name} does not differ from its v5 baseline")
        baseline_entry = baseline_entries[baseline_name]
        if sha256(baseline) != baseline_entry["sha256"]:
            raise RuntimeError(f"baseline hash drift: {baseline_name}")
        comparisons.append(
            {
                "file": target_name,
                "baseline": f"../baseline/{baseline_name}",
                "width": target_size[0],
                "height": target_size[1],
                "sha256": sha256(target),
                "baselineSha256": baseline_entry["sha256"],
                "rootMeanSquareDifference": round(difference, 6),
                "status": "passed",
            }
        )

    qmake = shutil.which("qmake6")
    qt_version = "unknown"
    if qmake:
        qt_version = run(
            [qmake, "-query", "QT_VERSION"],
            capture_output=True,
        ).stdout.strip()
    return {
        "schemaVersion": 1,
        "release": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "phase": 1,
        "kind": "rendered-north-star-prototype",
        "prototype": True,
        "productionRuntime": False,
        "liveEvidence": False,
        "renderer": {
            "source": "tools/north_star_renderer.cpp",
            "backend": "Qt QImage and QPainter",
            "platform": "offscreen",
            "qtVersion": qt_version,
            "systemFont": True,
        },
        "sources": {
            "tokensSha256": sha256(ROOT / "design/tokens.json"),
            "motionContractSha256": sha256(ROOT / "design/motion-contract.json"),
            "rendererSha256": sha256(ROOT / "tools/north_star_renderer.cpp"),
        },
        "comparisons": comparisons,
        "scorecard": {
            "scale": {"minimum": 1, "maximum": 5, "requiredMinimum": 4},
            "scores": SCORES,
            "status": "passed",
            "review": [
                "Neutral selected surfaces replace broad olive fills.",
                "Immediate focus rings remain distinct from filled primary actions.",
                "Tonal layers reduce nested borders and keep overlays legible.",
                "System-font roles establish hierarchy before separators.",
                "Lime is limited to primary actions, rails, and narrow energy seams.",
                "Motion evidence is a static storyboard; live motion remains unqualified.",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when renders drift")
    arguments = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="noxforge-v6-north-star-output-") as temporary:
        rendered = Path(temporary)
        manifest = render(rendered)
        manifest_text = json.dumps(manifest, indent=2, ensure_ascii=True) + "\n"
        if arguments.check:
            drift: list[str] = []
            for name in BASELINE_MAP:
                committed = OUTPUT / name
                if not committed.is_file() or committed.read_bytes() != (rendered / name).read_bytes():
                    drift.append(name)
            committed_manifest = OUTPUT / "manifest.json"
            if (
                not committed_manifest.is_file()
                or committed_manifest.read_text(encoding="utf-8") != manifest_text
            ):
                drift.append("manifest.json")
            if drift:
                print("north-star evidence drift: " + ", ".join(drift), file=sys.stderr)
                return 1
            print("Kinetic Precision north-star evidence is current")
            return 0

        OUTPUT.mkdir(parents=True, exist_ok=True)
        for name in BASELINE_MAP:
            shutil.copyfile(rendered / name, OUTPUT / name)
        (OUTPUT / "manifest.json").write_text(manifest_text, encoding="utf-8", newline="\n")
        print(f"Rendered {len(BASELINE_MAP)} Kinetic Precision north-star prototypes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
