#!/usr/bin/env python3
"""Measure the complete v6 candidate against the immutable reviewed v5 baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import statistics
import subprocess
import tarfile
import tempfile
import time
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/evidence/v6/performance.json"
BASELINE_COMMIT = "6a113e71980d106c38a2bbdece6df171c0ae9ed3"
RUNS = 11
MAX_RATIO = 1.10


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=True,
        text=True,
        capture_output=capture,
        stdout=None if capture else subprocess.DEVNULL,
    )


def configure(source: Path, build: Path, *, current: bool) -> None:
    run(
        [
            "cmake",
            "-S",
            str(source),
            "-B",
            str(build),
            "-G",
            "Ninja",
            "-DCMAKE_BUILD_TYPE=Release",
        ],
        cwd=source,
    )
    targets = ["noxforge_style", "noxforge_widget_gallery", "noxforge_sddm_renderer"]
    if current:
        targets.append("noxforge_motion_qualification_probe")
    run(["cmake", "--build", str(build), "--target", *targets], cwd=source)


def timed(command: list[str], *, cwd: Path, env: dict[str, str]) -> float:
    started = time.perf_counter_ns()
    run(command, cwd=cwd, env=env)
    return round((time.perf_counter_ns() - started) / 1_000_000, 3)


def metric(
    baseline_command: list[str],
    current_command: list[str],
    *,
    baseline_source: Path,
    current_source: Path,
    baseline_env: dict[str, str],
    current_env: dict[str, str],
) -> dict[str, object]:
    for _ in range(2):
        run(baseline_command, cwd=baseline_source, env=baseline_env)
        run(current_command, cwd=current_source, env=current_env)
    baseline = []
    current = []
    for index in range(RUNS):
        if index % 2 == 0:
            baseline.append(timed(baseline_command, cwd=baseline_source, env=baseline_env))
            current.append(timed(current_command, cwd=current_source, env=current_env))
        else:
            current.append(timed(current_command, cwd=current_source, env=current_env))
            baseline.append(timed(baseline_command, cwd=baseline_source, env=baseline_env))
    baseline_median = round(statistics.median(baseline), 3)
    current_median = round(statistics.median(current), 3)
    ratio = round(current_median / baseline_median, 4)
    return {
        "baselineSamplesMs": baseline,
        "currentSamplesMs": current,
        "baselineMedianMs": baseline_median,
        "currentMedianMs": current_median,
        "ratio": ratio,
        "limit": MAX_RATIO,
        "result": "passed" if ratio <= MAX_RATIO else "failed",
    }


def measure() -> dict[str, object]:
    archive = subprocess.run(
        ["git", "archive", "--format=tar", BASELINE_COMMIT],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    with tempfile.TemporaryDirectory(prefix="noxforge-v6-phase7-performance-") as temporary:
        temp = Path(temporary)
        baseline_source = temp / "baseline"
        baseline_source.mkdir()
        with tarfile.open(fileobj=BytesIO(archive), mode="r:") as source:
            source.extractall(baseline_source, filter="data")
        baseline_build = temp / "baseline-build"
        current_build = temp / "current-build"
        configure(baseline_source, baseline_build, current=False)
        configure(ROOT, current_build, current=True)

        baseline_env = {
            **os.environ,
            "QT_QPA_PLATFORM": "offscreen",
            "QT_PLUGIN_PATH": str(baseline_build / "plugins"),
        }
        current_env = {
            **os.environ,
            "QT_QPA_PLATFORM": "offscreen",
            "QT_PLUGIN_PATH": str(current_build / "plugins"),
        }
        quick_env = {
            **current_env,
            "QT_QUICK_BACKEND": "software",
        }
        baseline_quick_env = {
            **baseline_env,
            "QT_QUICK_BACKEND": "software",
        }
        baseline_output = temp / "baseline.png"
        current_output = temp / "current.png"
        metrics = {
            "galleryStartup": metric(
                [str(baseline_build / "noxforge_widget_gallery"), "--page=controls"],
                [str(current_build / "noxforge_widget_gallery"), "--page=controls"],
                baseline_source=baseline_source,
                current_source=ROOT,
                baseline_env=baseline_env,
                current_env=current_env,
            ),
            "controlRendering": metric(
                [
                    str(current_build / "noxforge_widget_gallery"),
                    "--page=controls",
                    str(baseline_output),
                ],
                [
                    str(current_build / "noxforge_widget_gallery"),
                    "--page=controls",
                    str(current_output),
                ],
                baseline_source=ROOT,
                current_source=ROOT,
                baseline_env=baseline_env,
                current_env=current_env,
            ),
            "qmlFirstFrame": metric(
                [
                    str(baseline_build / "noxforge_sddm_renderer"),
                    str(baseline_source / "sddm/NoxForge/Main.qml"),
                    str(baseline_source / "sddm/NoxForge/background.png"),
                    str(baseline_output),
                    "--first-frame",
                ],
                [
                    str(current_build / "noxforge_sddm_renderer"),
                    str(ROOT / "sddm/NoxForge/Main.qml"),
                    str(ROOT / "sddm/NoxForge/background.png"),
                    str(current_output),
                    "--first-frame",
                ],
                baseline_source=baseline_source,
                current_source=ROOT,
                baseline_env=baseline_quick_env,
                current_env=quick_env,
            ),
        }
        stress = json.loads(
            run(
                [str(current_build / "noxforge_motion_qualification_probe")],
                cwd=ROOT,
                env=current_env,
                capture=True,
            ).stdout
        )

    failed = [name for name, value in metrics.items() if value["result"] != "passed"]
    if failed:
        ratios = {name: metrics[name]["ratio"] for name in failed}
        raise RuntimeError(f"v6 Phase 7 performance regression exceeds ten percent: {ratios}")
    if stress.get("result") != "passed":
        raise RuntimeError(f"v6 Phase 7 motion stress failed: {stress}")

    qt_version = subprocess.run(
        ["qmake6", "-query", "QT_VERSION"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    source_paths = (
        ROOT / "CMakeLists.txt",
        ROOT / "design/motion-contract.json",
        ROOT / "scripts/measure_v6_phase7_performance.py",
        ROOT / "src/style/noxforgemotion.cpp",
        ROOT / "src/style/noxforgemotion.h",
        ROOT / "src/style/noxforgestyle.cpp",
        ROOT / "tests/qt/motion_qualification_probe.cpp",
        ROOT / "tools/widget_gallery.cpp",
        ROOT / "tools/sddm_renderer.cpp",
        ROOT / "sddm/NoxForge/Main.qml",
    )
    return {
        "schemaVersion": 1,
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "phase": 7,
        "result": "passed",
        "baselineCommit": BASELINE_COMMIT,
        "method": (
            "Eleven warmed, interleaved offscreen process medians compare the complete "
            "v6 tree with the immutable reviewed v5 baseline. A separate native probe "
            "runs 500 input and animation cycles, checks semantic end states, trims and "
            "compares glibc heap allocation, and requires the shared timer to stop."
        ),
        "maximumRatio": MAX_RATIO,
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "qt": qt_version,
        },
        "metrics": metrics,
        "motionStress": stress,
        "sources": {
            path.relative_to(ROOT).as_posix(): digest(path)
            for path in sorted(source_paths)
        },
    }


def validate(report: dict[str, object]) -> None:
    if (
        report.get("schemaVersion") != 1
        or report.get("phase") != 7
        or report.get("version") != (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        or report.get("baselineCommit") != BASELINE_COMMIT
        or report.get("result") != "passed"
        or report.get("maximumRatio") != MAX_RATIO
    ):
        raise RuntimeError("v6 Phase 7 performance evidence has an invalid identity")
    metrics = report.get("metrics")
    if not isinstance(metrics, dict) or set(metrics) != {
        "galleryStartup",
        "controlRendering",
        "qmlFirstFrame",
    }:
        raise RuntimeError("v6 Phase 7 performance metrics are incomplete")
    for name, value in metrics.items():
        if value.get("result") != "passed" or value.get("ratio", 99) > MAX_RATIO:
            raise RuntimeError(f"v6 Phase 7 performance metric failed: {name}")
        if (
            len(value.get("baselineSamplesMs", [])) != RUNS
            or len(value.get("currentSamplesMs", [])) != RUNS
        ):
            raise RuntimeError(f"v6 Phase 7 performance samples are incomplete: {name}")
    stress = report.get("motionStress")
    if (
        not isinstance(stress, dict)
        or stress.get("result") != "passed"
        or stress.get("cycles") != 500
        or stress.get("failedCases") != 0
        or stress.get("idleTimerActive") is not False
        or stress.get("trackedWidgetsAfterCleanup") != 0
        or stress.get("heapGrowthBytes", -1) < 0
        or stress.get("heapGrowthBytes", 999999999)
        > stress.get("heapGrowthLimitBytes", -1)
    ):
        raise RuntimeError("v6 Phase 7 motion stress evidence is incomplete or failed")
    sources = report.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise RuntimeError("v6 Phase 7 performance source lineage is missing")
    for relative, expected in sources.items():
        path = ROOT / relative
        if not path.is_file() or digest(path) != expected:
            raise RuntimeError(f"v6 Phase 7 performance source drift: {relative}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    if arguments.check:
        validate(json.loads(OUTPUT.read_text(encoding="utf-8")))
        print("v6 Phase 7 performance evidence passed")
        return 0
    report = measure()
    validate(report)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
