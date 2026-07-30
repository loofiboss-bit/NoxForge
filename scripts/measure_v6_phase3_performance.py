#!/usr/bin/env python3
"""Compare v6 native Qt medians with the immutable reviewed v5 baseline."""

from __future__ import annotations

import argparse
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
OUTPUT = ROOT / "docs/evidence/v6/qt-motion/performance.json"
BASELINE_COMMIT = "6a113e71980d106c38a2bbdece6df171c0ae9ed3"
RUNS = 11
MAX_RATIO = 1.10


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> None:
    subprocess.run(command, cwd=cwd, env=env, check=True, stdout=subprocess.DEVNULL)


def configure(source: Path, build: Path) -> None:
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
    run(
        [
            "cmake",
            "--build",
            str(build),
            "--target",
            "noxforge_style",
            "noxforge_widget_gallery",
        ],
        cwd=source,
    )


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
    with tempfile.TemporaryDirectory(prefix="noxforge-v6-phase3-performance-") as temporary:
        temp = Path(temporary)
        baseline_source = temp / "baseline"
        baseline_source.mkdir()
        with tarfile.open(fileobj=BytesIO(archive), mode="r:") as source:
            source.extractall(baseline_source, filter="data")
        baseline_build = temp / "baseline-build"
        current_build = temp / "current-build"
        configure(baseline_source, baseline_build)
        configure(ROOT, current_build)

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
                [str(current_build / "noxforge_widget_gallery"), "--page=controls"],
                [str(current_build / "noxforge_widget_gallery"), "--page=controls"],
                baseline_source=ROOT,
                current_source=ROOT,
                baseline_env=baseline_env,
                current_env=current_env,
            ),
        }

    failed = [name for name, value in metrics.items() if value["result"] != "passed"]
    if failed:
        ratios = {name: metrics[name]["ratio"] for name in failed}
        raise RuntimeError(f"v6 Phase 3 performance regression exceeds ten percent: {ratios}")
    qt_version = subprocess.run(
        ["qmake6", "-query", "QT_VERSION"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return {
        "schemaVersion": 1,
        "phase": 3,
        "result": "passed",
        "baselineCommit": BASELINE_COMMIT,
        "method": (
            "Eleven warmed, interleaved offscreen process medians on one host. Gallery startup "
            "uses each source version's gallery executable; control rendering uses "
            "one fixed v6 gallery harness with the baseline and current style plugins."
        ),
        "maximumRatio": MAX_RATIO,
        "idleTimerExpected": False,
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "qt": qt_version,
        },
        "metrics": metrics,
    }


def validate(report: dict[str, object]) -> None:
    if (
        report.get("baselineCommit") != BASELINE_COMMIT
        or report.get("phase") != 3
        or report.get("result") != "passed"
        or report.get("idleTimerExpected") is not False
    ):
        raise RuntimeError("v6 Phase 3 performance evidence has an invalid identity")
    metrics = report.get("metrics")
    if not isinstance(metrics, dict) or set(metrics) != {
        "galleryStartup",
        "controlRendering",
    }:
        raise RuntimeError("v6 Phase 3 performance evidence is incomplete")
    for name, value in metrics.items():
        if value.get("result") != "passed" or value.get("ratio", 99) > MAX_RATIO:
            raise RuntimeError(f"v6 Phase 3 performance metric failed: {name}")
        if (
            len(value.get("baselineSamplesMs", [])) != RUNS
            or len(value.get("currentSamplesMs", [])) != RUNS
        ):
            raise RuntimeError(f"v6 Phase 3 performance samples are incomplete: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    if arguments.check:
        validate(json.loads(OUTPUT.read_text(encoding="utf-8")))
        print("v6 Phase 3 performance evidence passed")
        return 0
    report = measure()
    validate(report)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
