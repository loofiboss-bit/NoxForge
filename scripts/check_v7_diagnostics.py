#!/usr/bin/env python3
"""Validate v7 diagnostics, sound reproducibility, and gate reporting."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "design/v7-diagnostics-contract.json"
DOCTOR_PATH = ROOT / "tools/noxforge-doctor"
SOUND_PATH = ROOT / "scripts/generate_sound_theme.py"
RELEASE_PATH = ROOT / "scripts/release-check.py"
RUNNER_PATH = ROOT / "scripts/run_python_tests.py"
MAN_PATH = ROOT / "docs/man/noxforge-doctor.1"
ARTWORK_PATH = ROOT / "docs/ARTWORK.md"
EVIDENCE_PATH = ROOT / "docs/evidence/v7/diagnostics/phase7.json"
CHECK = "--check" in sys.argv[1:]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(text: str, fragments: tuple[str, ...], subject: str) -> None:
    missing = [fragment for fragment in fragments if fragment not in text]
    if missing:
        raise RuntimeError(f"{subject} contract drift: {', '.join(missing)}")


def build_evidence() -> dict[str, object]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    doctor = DOCTOR_PATH.read_text(encoding="utf-8")
    sound = SOUND_PATH.read_text(encoding="utf-8")
    release = RELEASE_PATH.read_text(encoding="utf-8")
    runner = RUNNER_PATH.read_text(encoding="utf-8")
    manual = MAN_PATH.read_text(encoding="utf-8")
    artwork = ARTWORK_PATH.read_text(encoding="utf-8")

    require(
        doctor,
        (
            '"qtStyle"',
            '"soundTheme"',
            '"criticalIcons"',
            '"provenance"',
            "detect_wallpaper",
            "parse_kscreen_doctor",
            '"KScreen/KWin runtime"',
        ),
        "doctor",
    )
    if contract["doctor"]["forbiddenScaleSource"] in doctor:
        raise RuntimeError("doctor still treats QT_SCALE_FACTOR as output evidence")
    require(manual, ("component provenance", "KScreen/KWin", "critical resolution"), "doctor manual")
    require(
        sound,
        (
            f'PINNED_FFMPEG_VERSION = "{contract["soundReproducibility"]["pinnedFfmpegVersion"]}"',
            "canonical PCM/source metrics",
            "pinned FFmpeg byte equality",
        ),
        "sound reproducibility",
    )
    require(artwork, ("Cross-toolchain reproducibility", "must never be used to overwrite"), "artwork documentation")
    require(
        release,
        (
            "environment preflight failed",
            "repository gate failed after environment preflight",
            "scripts/run_python_tests.py",
            "Derived Python gate counts",
        ),
        "release gate",
    )
    require(runner, ("result.testsRun", "len(result.skipped)", "result.wasSuccessful()"), "Python runner")

    return {
        "schemaVersion": 1,
        "version": contract["version"],
        "phase": 7,
        "result": "passed",
        "doctor": contract["doctor"],
        "soundReproducibility": contract["soundReproducibility"],
        "releaseGate": contract["releaseGate"],
        "liveQualification": contract["liveQualification"],
        "sourceHashes": {
            "contract": sha256(CONTRACT_PATH),
            "doctor": sha256(DOCTOR_PATH),
            "soundGenerator": sha256(SOUND_PATH),
            "releaseCheck": sha256(RELEASE_PATH),
            "testRunner": sha256(RUNNER_PATH),
            "doctorManual": sha256(MAN_PATH),
            "artworkDocumentation": sha256(ARTWORK_PATH),
        },
    }


def main() -> int:
    try:
        payload = json.dumps(build_evidence(), indent=2) + "\n"
    except (KeyError, OSError, RuntimeError, ValueError) as error:
        print(f"NoxForge v7 diagnostics check failed: {error}", file=sys.stderr)
        return 1
    if CHECK:
        if not EVIDENCE_PATH.is_file() or EVIDENCE_PATH.read_text(encoding="utf-8") != payload:
            print("NoxForge v7 diagnostics evidence drifted", file=sys.stderr)
            return 1
        print("NoxForge v7 diagnostics check passed")
        return 0
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(payload, encoding="utf-8", newline="\n")
    print("Wrote NoxForge v7 diagnostics evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
