#!/usr/bin/env python3
"""Compare v5 rendering medians with the locked Phase 0 source baseline."""

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
OUTPUT = ROOT / "docs/evidence/v5/performance.json"
BASELINE_COMMIT = "e3faefd481026cffafb9b48e11aa79987781fa78"
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
            "noxforge_style_probe",
            "noxforge_widget_gallery",
            "noxforge_sddm_renderer",
        ],
        cwd=source,
    )


def samples(command: list[str], *, cwd: Path, env: dict[str, str]) -> list[float]:
    for _ in range(2):
        run(command, cwd=cwd, env=env)
    measured = []
    for _ in range(RUNS):
        started = time.perf_counter_ns()
        run(command, cwd=cwd, env=env)
        measured.append(round((time.perf_counter_ns() - started) / 1_000_000, 3))
    return measured


def metric(
    baseline_command: list[str],
    current_command: list[str],
    *,
    baseline_source: Path,
    current_source: Path,
    baseline_env: dict[str, str],
    current_env: dict[str, str],
) -> dict[str, object]:
    baseline = samples(baseline_command, cwd=baseline_source, env=baseline_env)
    current = samples(current_command, cwd=current_source, env=current_env)
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
    with tempfile.TemporaryDirectory(prefix="noxforge-phase6-performance-") as temporary:
        temp = Path(temporary)
        baseline_source = temp / "baseline"
        baseline_source.mkdir()
        with tarfile.open(fileobj=BytesIO(archive), mode="r:") as source:
            source.extractall(baseline_source, filter="data")
        baseline_build = temp / "baseline-build"
        current_build = temp / "current-build"
        configure(baseline_source, baseline_build)
        configure(ROOT, current_build)

        base_env = {
            **os.environ,
            "QT_QPA_PLATFORM": "offscreen",
            "QT_PLUGIN_PATH": str(baseline_build / "plugins"),
        }
        current_env = {
            **os.environ,
            "QT_QPA_PLATFORM": "offscreen",
            "QT_PLUGIN_PATH": str(current_build / "plugins"),
        }
        output = temp / "capture.png"
        metrics = {
            "galleryStartup": metric(
                [str(baseline_build / "noxforge_widget_gallery"), "--page=controls"],
                [str(current_build / "noxforge_widget_gallery"), "--page=controls"],
                baseline_source=baseline_source,
                current_source=ROOT,
                baseline_env=base_env,
                current_env=current_env,
            ),
            "controlRendering": metric(
                [str(current_build / "noxforge_widget_gallery"), "--page=controls", str(output)],
                [str(current_build / "noxforge_widget_gallery"), "--page=controls", str(output)],
                baseline_source=baseline_source,
                current_source=ROOT,
                baseline_env=base_env,
                current_env=current_env,
            ),
            "qmlFirstFrame": metric(
                [
                    str(current_build / "noxforge_sddm_renderer"),
                    str(baseline_source / "sddm/NoxForge/Main.qml"),
                    str(baseline_source / "sddm/NoxForge/background.png"),
                    str(output),
                    "--first-frame",
                ],
                [
                    str(current_build / "noxforge_sddm_renderer"),
                    str(ROOT / "sddm/NoxForge/Main.qml"),
                    str(ROOT / "sddm/NoxForge/background.png"),
                    str(output),
                    "--first-frame",
                ],
                baseline_source=baseline_source,
                current_source=ROOT,
                baseline_env=current_env,
                current_env=current_env,
            ),
        }
    failed = [name for name, value in metrics.items() if value["result"] != "passed"]
    if failed:
        ratios = {name: metrics[name]["ratio"] for name in failed}
        raise RuntimeError(
            f"Phase 6 performance regression exceeds ten percent: {ratios}"
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
        "phase": 6,
        "result": "passed",
        "baselineCommit": BASELINE_COMMIT,
        "method": "Eleven warmed offscreen process medians on one host. Gallery startup uses each source version's gallery executable; control rendering uses one fixed current gallery harness with the Phase 0 and current style plugins; the QML probe exits on the first frameSwapped signal.",
        "maximumRatio": MAX_RATIO,
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "qt": qt_version,
        },
        "metrics": metrics,
    }


def validate(report: dict[str, object]) -> None:
    if report.get("baselineCommit") != BASELINE_COMMIT or report.get("result") != "passed":
        raise RuntimeError("Phase 6 performance evidence has an invalid baseline or result")
    metrics = report.get("metrics")
    if not isinstance(metrics, dict) or set(metrics) != {
        "galleryStartup",
        "controlRendering",
        "qmlFirstFrame",
    }:
        raise RuntimeError("Phase 6 performance evidence has incomplete metrics")
    for name, value in metrics.items():
        if value.get("result") != "passed" or value.get("ratio", 99) > MAX_RATIO:
            raise RuntimeError(f"Phase 6 performance metric failed: {name}")
        if len(value.get("baselineSamplesMs", [])) != RUNS or len(
            value.get("currentSamplesMs", [])
        ) != RUNS:
            raise RuntimeError(f"Phase 6 performance samples are incomplete: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    if arguments.check:
        validate(json.loads(OUTPUT.read_text(encoding="utf-8")))
        print("Phase 6 performance evidence passed")
        return 0
    report = measure()
    validate(report)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
