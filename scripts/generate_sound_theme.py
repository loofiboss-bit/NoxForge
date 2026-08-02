#!/usr/bin/env python3
"""Synthesize the original, restrained NoxForge system sound theme."""

from __future__ import annotations

import argparse
import json
import hashlib
import math
import random
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "sounds/NoxForge"
ARTWORK = json.loads((ROOT / "design/artwork-contract.json").read_text(encoding="utf-8"))
SOUND_CONTRACT = ARTWORK["sounds"]
RATE = SOUND_CONTRACT["sampleRate"]
PINNED_FFMPEG_VERSION = "8.1.2"

SPECS = {
    "tick": (0.08, ((880.0, 0.16), (1320.0, 0.05))),
    "success": (0.28, ((523.25, 0.11), (783.99, 0.10), (1046.5, 0.06))),
    "warning": (0.34, ((440.0, 0.10), (329.63, 0.13))),
    "error": (0.32, ((196.0, 0.14), (155.56, 0.12))),
    "login": (0.52, ((261.63, 0.08), (392.0, 0.08), (659.25, 0.07))),
    "logout": (0.44, ((523.25, 0.08), (329.63, 0.08), (220.0, 0.06))),
    "device-added": (0.24, ((349.23, 0.09), (698.46, 0.07))),
    "device-removed": (0.24, ((698.46, 0.08), (349.23, 0.07))),
    "message": (0.20, ((740.0, 0.08), (987.77, 0.05))),
    "alarm": (0.70, ((440.0, 0.11), (880.0, 0.08), (440.0, 0.09))),
}

EVENTS = {
    "audio-volume-change": "tick",
    "button-pressed": "tick",
    "button-pressed-modifier": "tick",
    "bell-window-system": "tick",
    "completion-success": "success",
    "outcome-success": "success",
    "completion-partial": "warning",
    "completion-rotation": "tick",
    "completion-fail": "error",
    "outcome-failure": "error",
    "desktop-login": "login",
    "service-login": "login",
    "desktop-logout": "logout",
    "service-logout": "logout",
    "device-added": "device-added",
    "power-plug": "device-added",
    "device-removed": "device-removed",
    "power-unplug": "device-removed",
    "dialog-information": "message",
    "dialog-question": "message",
    "message-new-email": "message",
    "message-new-instant": "message",
    "dialog-warning": "warning",
    "dialog-warning-auth": "warning",
    "battery-caution": "warning",
    "battery-low": "warning",
    "dialog-error": "error",
    "dialog-error-serious": "error",
    "alarm-clock-elapsed": "alarm",
    "phone-incoming-call": "alarm",
    "trash-empty": "device-removed",
    "theme-demo": "login",
}


def synthesize(name: str, duration: float, tones: tuple[tuple[float, float], ...]) -> bytes:
    rng = random.Random(name)
    sample_count = round(duration * RATE)
    frames = bytearray()
    segment_length = sample_count / len(tones)
    for index in range(sample_count):
        segment = min(len(tones) - 1, int(index / segment_length))
        frequency, gain = tones[segment]
        local = (index - segment * segment_length) / RATE
        attack = min(1.0, local / 0.008)
        envelope = attack * math.exp(-local * 11.0)
        fundamental = math.sin(2 * math.pi * frequency * local)
        overtone = math.sin(2 * math.pi * frequency * 2.01 * local) * 0.22
        texture = (rng.random() * 2 - 1) * 0.015 * math.exp(-local * 24)
        value = max(-0.8, min(0.8, (fundamental + overtone) * gain * envelope + texture))
        frames.extend(struct.pack("<h", round(value * 32767)))
    return bytes(frames)


def normalize(frames: bytes, target_dbfs: float) -> bytes:
    samples = struct.unpack(f"<{len(frames) // 2}h", frames)
    rms = math.sqrt(sum(sample * sample for sample in samples) / len(samples))
    peak = max(abs(sample) for sample in samples)
    target = 32767 * 10 ** (target_dbfs / 20)
    ceiling = 32767 * 10 ** (SOUND_CONTRACT["peakCeilingDbfs"] / 20)
    gain = min(target / rms, ceiling / peak)
    normalized = (max(-32768, min(32767, round(sample * gain))) for sample in samples)
    return struct.pack(f"<{len(samples)}h", *normalized)


def metrics(frames: bytes) -> dict[str, float]:
    samples = struct.unpack(f"<{len(frames) // 2}h", frames)
    rms = math.sqrt(sum(sample * sample for sample in samples) / len(samples)) / 32767
    peak = max(abs(sample) for sample in samples) / 32767
    return {
        "rmsDbfs": round(20 * math.log10(rms), 3),
        "peakDbfs": round(20 * math.log10(peak), 3),
    }


def write_wav(path: Path, frames: bytes) -> None:
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(RATE)
        output.writeframes(frames)


def encode(source: Path, target: Path) -> None:
    subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-fflags", "+bitexact",
            "-i", str(source), "-map_metadata", "-1", "-ac", "2", "-c:a", "libvorbis",
            "-q:a", "4", "-flags:a", "+bitexact", str(target),
        ],
        check=True,
    )


def ffmpeg_version() -> str | None:
    try:
        first_line = subprocess.run(
            ["ffmpeg", "-version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
    except (IndexError, OSError, subprocess.CalledProcessError):
        return None
    match = re.match(r"ffmpeg version\s+([^\s]+)", first_line)
    return match.group(1) if match else None


def ogg_crc(data: bytes) -> int:
    checksum = 0
    for byte in data:
        checksum ^= byte << 24
        for _ in range(8):
            checksum = ((checksum << 1) ^ 0x04C11DB7) & 0xFFFFFFFF if checksum & 0x80000000 else (checksum << 1) & 0xFFFFFFFF
    return checksum


def normalize_ogg(path: Path, stream_name: str) -> None:
    """Replace random Ogg serials and recompute page CRCs deterministically."""
    content = bytearray(path.read_bytes())
    serial = hashlib.sha256(stream_name.encode("utf-8")).digest()[:4]
    offset = 0
    while offset < len(content):
        if content[offset : offset + 4] != b"OggS":
            raise RuntimeError(f"invalid Ogg page in {path}")
        segment_count = content[offset + 26]
        header_length = 27 + segment_count
        body_length = sum(content[offset + 27 : offset + header_length])
        page_length = header_length + body_length
        content[offset + 14 : offset + 18] = serial
        content[offset + 22 : offset + 26] = b"\0\0\0\0"
        checksum = ogg_crc(bytes(content[offset : offset + page_length]))
        content[offset + 22 : offset + 26] = struct.pack("<I", checksum)
        offset += page_length
    path.write_bytes(content)


def generate(theme: Path) -> None:
    source_dir = theme / "source"
    stereo_dir = theme / "stereo"
    source_dir.mkdir(parents=True, exist_ok=True)
    stereo_dir.mkdir(parents=True, exist_ok=True)
    encoded: dict[str, Path] = {}
    measurements: dict[str, dict[str, float]] = {}
    for name, (duration, tones) in SPECS.items():
        wav_path = source_dir / f"{name}.wav"
        oga_path = stereo_dir / f"_{name}.oga"
        target = SOUND_CONTRACT["alarmTargetRmsDbfs"] if name == "alarm" else SOUND_CONTRACT["targetRmsDbfs"]
        frames = normalize(synthesize(name, duration, tones), target)
        write_wav(wav_path, frames)
        encode(wav_path, oga_path)
        normalize_ogg(oga_path, name)
        encoded[name] = oga_path
        measurements[name] = metrics(frames)
    for event, source in EVENTS.items():
        shutil.copyfile(encoded[source], stereo_dir / f"{event}.oga")
    for path in encoded.values():
        path.unlink()
    (theme / "index.theme").write_text(
        "[Sound Theme]\nName=NoxForge\nComment=Original restrained forge tones for KDE Plasma\nDirectories=stereo\nExample=theme-demo\n\n[stereo]\nOutputProfile=stereo\n",
        encoding="utf-8",
        newline="\n",
    )
    (theme / "coverage.json").write_text(
        json.dumps(
            {
                "schemaVersion": 2,
                "sampleRate": RATE,
                "events": EVENTS,
                "normalization": {
                    "targetRmsDbfs": SOUND_CONTRACT["targetRmsDbfs"],
                    "alarmTargetRmsDbfs": SOUND_CONTRACT["alarmTargetRmsDbfs"],
                    "peakCeilingDbfs": SOUND_CONTRACT["peakCeilingDbfs"],
                    "toleranceDb": SOUND_CONTRACT["toleranceDb"],
                },
                "sources": {
                    name: {
                        "durationMs": round(duration * 1000),
                        "frequenciesHz": [frequency for frequency, _gain in tones],
                        **measurements[name],
                    }
                    for name, (duration, tones) in SPECS.items()
                },
            },
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when generated sound files drift")
    args = parser.parse_args()
    encoder = ffmpeg_version() if shutil.which("ffmpeg") else None
    if encoder is None:
        print("environment preflight failed: ffmpeg is required for sound validation", file=sys.stderr)
        raise SystemExit(1)
    if not args.check:
        generate(THEME)
        print(f"Generated {len(EVENTS)} normalized original NoxForge sound events")
        return
    with tempfile.TemporaryDirectory(prefix="noxforge-sounds-") as temporary:
        generated = Path(temporary) / "NoxForge"
        generate(generated)
        expected = sorted(path.relative_to(generated) for path in generated.rglob("*") if path.is_file())
        pinned = encoder == PINNED_FFMPEG_VERSION
        drift = [
            relative
            for relative in expected
            if pinned or relative.parts[0] != "stereo"
            if not (THEME / relative).is_file()
            or (generated / relative).read_bytes() != (THEME / relative).read_bytes()
        ]
        if drift:
            policy = "pinned encoder bytes" if pinned else "canonical PCM/source metrics"
            print(f"Sound generator drift under {policy}: " + ", ".join(map(str, drift)), file=sys.stderr)
            raise SystemExit(1)
        invalid_ogg = [
            relative
            for relative in expected
            if relative.parts[0] == "stereo"
            and (
                not (THEME / relative).is_file()
                or (THEME / relative).read_bytes()[:4] != b"OggS"
            )
        ]
        if invalid_ogg:
            print("Invalid committed Ogg events: " + ", ".join(map(str, invalid_ogg)), file=sys.stderr)
            raise SystemExit(1)
    policy = "pinned FFmpeg byte equality" if encoder == PINNED_FFMPEG_VERSION else "canonical PCM/source metrics"
    print(f"Verified {len(EVENTS)} normalized original NoxForge sound events using {policy} ({encoder})")


if __name__ == "__main__":
    main()
