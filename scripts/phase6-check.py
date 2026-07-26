#!/usr/bin/env python3
"""Run the complete NoxForge v5 Phase 6 automated gate."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], *, env: dict[str, str] | None = None) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def main() -> int:
    run([sys.executable, "scripts/release-check.py"])
    run([sys.executable, "scripts/check_phase6_accessibility.py", "--check"])
    run([sys.executable, "scripts/measure_phase6_performance.py", "--check"])
    run([sys.executable, "-m", "unittest", "tests.test_v5_phase6", "-v"])

    with tempfile.TemporaryDirectory(prefix="noxforge-phase6-sanitizers-") as temporary:
        build = Path(temporary) / "build"
        flags = "-fsanitize=address,undefined -fno-omit-frame-pointer"
        run(
            [
                "cmake",
                "-S",
                str(ROOT),
                "-B",
                str(build),
                "-G",
                "Ninja",
                "-DCMAKE_BUILD_TYPE=Debug",
                f"-DCMAKE_CXX_FLAGS={flags}",
                f"-DCMAKE_EXE_LINKER_FLAGS={flags}",
                f"-DCMAKE_SHARED_LINKER_FLAGS={flags}",
            ]
        )
        run(["cmake", "--build", str(build)])
        env = {
            **os.environ,
            "ASAN_OPTIONS": "detect_leaks=0:halt_on_error=1",
            "UBSAN_OPTIONS": "halt_on_error=1:print_stacktrace=1",
        }
        run(["ctest", "--test-dir", str(build), "--output-on-failure"], env=env)

    print("NoxForge Phase 6 automated gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
