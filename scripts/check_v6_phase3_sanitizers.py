#!/usr/bin/env python3
"""Build and run the v6 native style probes with ASan and UBSan."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="noxforge-v6-phase3-sanitizers-") as temporary:
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
                "-DCMAKE_BUILD_TYPE=RelWithDebInfo",
                "-DNOXFORGE_ENABLE_SANITIZERS=ON",
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
                "noxforge_style_probe",
                "noxforge_motion_probe",
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        environment = {
            **os.environ,
            "ASAN_OPTIONS": "detect_leaks=0:halt_on_error=1",
            "UBSAN_OPTIONS": "halt_on_error=1:print_stacktrace=1",
        }
        subprocess.run(
            [
                "ctest",
                "--test-dir",
                str(build),
                "--output-on-failure",
                "-R",
                "style-plugin-discovery|motion-controller-lifecycle",
            ],
            cwd=ROOT,
            env=environment,
            check=True,
        )
    print("Native Qt style ASan and UBSan probes passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
