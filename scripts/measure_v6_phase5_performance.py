#!/usr/bin/env python3
"""Compare the v6 SDDM first-frame median with the reviewed v5 baseline."""

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
OUTPUT = ROOT / "docs/evidence/v6/session/performance.json"
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
        ["cmake", "--build", str(build), "--target", "noxforge_sddm_renderer"],
        cwd=source,
    )


def timed(command: list[str], *, cwd: Path, env: dict[str, str]) -> float:
    started = time.perf_counter_ns()
    run(command, cwd=cwd, env=env)
    return round((time.perf_counter_ns() - started) / 1_000_000, 3)


def measure() -> dict[str, object]:
    archive = subprocess.run(
        ["git", "archive", "--format=tar", BASELINE_COMMIT],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    with tempfile.TemporaryDirectory(prefix="noxforge-v6-phase5-performance-") as temporary:
        temp = Path(temporary)
        baseline_source = temp / "baseline"
        baseline_source.mkdir()
        with tarfile.open(fileobj=BytesIO(archive), mode="r:") as source:
            source.extractall(baseline_source, filter="data")
        baseline_build = temp / "baseline-build"
        current_build = temp / "current-build"
        configure(baseline_source, baseline_build)
        configure(ROOT, current_build)
        baseline_output = temp / "baseline.png"
        current_output = temp / "current.png"
        baseline_command = [
            str(baseline_build / "noxforge_sddm_renderer"),
            str(baseline_source / "sddm/NoxForge/Main.qml"),
            str(baseline_source / "sddm/NoxForge/background.png"),
            str(baseline_output),
            "--first-frame",
        ]
        current_command = [
            str(current_build / "noxforge_sddm_renderer"),
            str(ROOT / "sddm/NoxForge/Main.qml"),
            str(ROOT / "sddm/NoxForge/background.png"),
            str(current_output),
            "--first-frame",
        ]
        environment = {
            **os.environ,
            "QT_QPA_PLATFORM": "offscreen",
            "QT_QUICK_BACKEND": "software",
        }
        for _ in range(2):
            run(baseline_command, cwd=baseline_source, env=environment)
            run(current_command, cwd=ROOT, env=environment)
        baseline_samples = []
        current_samples = []
        for index in range(RUNS):
            if index % 2 == 0:
                baseline_samples.append(timed(baseline_command, cwd=baseline_source, env=environment))
                current_samples.append(timed(current_command, cwd=ROOT, env=environment))
            else:
                current_samples.append(timed(current_command, cwd=ROOT, env=environment))
                baseline_samples.append(timed(baseline_command, cwd=baseline_source, env=environment))

    baseline_median = round(statistics.median(baseline_samples), 3)
    current_median = round(statistics.median(current_samples), 3)
    ratio = round(current_median / baseline_median, 4)
    result = "passed" if ratio <= MAX_RATIO else "failed"
    if result != "passed":
        raise RuntimeError(
            "v6 Phase 5 first-frame regression exceeds ten percent: "
            f"{ratio} (baseline={baseline_samples}, current={current_samples})"
        )
    qt_version = subprocess.run(
        ["qmake6", "-query", "QT_VERSION"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return {
        "schemaVersion": 1,
        "phase": 5,
        "result": result,
        "baselineCommit": BASELINE_COMMIT,
        "method": "Eleven warmed, interleaved SDDM offscreen first-frame process medians on one host.",
        "maximumRatio": MAX_RATIO,
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "qt": qt_version,
        },
        "metric": {
            "baselineSamplesMs": baseline_samples,
            "currentSamplesMs": current_samples,
            "baselineMedianMs": baseline_median,
            "currentMedianMs": current_median,
            "ratio": ratio,
            "limit": MAX_RATIO,
            "result": result,
        },
    }


def validate(report: dict[str, object]) -> None:
    if (
        report.get("baselineCommit") != BASELINE_COMMIT
        or report.get("phase") != 5
        or report.get("result") != "passed"
        or report.get("maximumRatio") != MAX_RATIO
    ):
        raise RuntimeError("v6 Phase 5 performance evidence has an invalid identity")
    metric = report.get("metric")
    if (
        not isinstance(metric, dict)
        or metric.get("result") != "passed"
        or metric.get("ratio", 99) > MAX_RATIO
        or len(metric.get("baselineSamplesMs", [])) != RUNS
        or len(metric.get("currentSamplesMs", [])) != RUNS
    ):
        raise RuntimeError("v6 Phase 5 first-frame evidence is incomplete or failed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    if arguments.check:
        report = json.loads(OUTPUT.read_text(encoding="utf-8"))
        validate(report)
        print("v6 Phase 5 first-frame performance evidence passed")
        return 0
    report = measure()
    validate(report)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
