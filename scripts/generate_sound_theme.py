#!/usr/bin/env python3
"""Synthesize the original, restrained NoxForge system sound theme."""

from __future__ import annotations

import json
import hashlib
import math
import random
import shutil
import struct
import subprocess
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "sounds/NoxForge"
RATE = 48_000

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


def main() -> None:
    source_dir = THEME / "source"
    stereo_dir = THEME / "stereo"
    source_dir.mkdir(parents=True, exist_ok=True)
    stereo_dir.mkdir(parents=True, exist_ok=True)
    encoded: dict[str, Path] = {}
    for name, (duration, tones) in SPECS.items():
        wav_path = source_dir / f"{name}.wav"
        oga_path = stereo_dir / f"_{name}.oga"
        write_wav(wav_path, synthesize(name, duration, tones))
        encode(wav_path, oga_path)
        normalize_ogg(oga_path, name)
        encoded[name] = oga_path
    for event, source in EVENTS.items():
        shutil.copyfile(encoded[source], stereo_dir / f"{event}.oga")
    for path in encoded.values():
        path.unlink()
    (THEME / "index.theme").write_text(
        "[Sound Theme]\nName=NoxForge\nComment=Original restrained forge tones for KDE Plasma\nDirectories=stereo\nExample=theme-demo\n\n[stereo]\nOutputProfile=stereo\n",
        encoding="utf-8",
        newline="\n",
    )
    (THEME / "coverage.json").write_text(
        json.dumps({"schemaVersion": 1, "sampleRate": RATE, "events": EVENTS}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Generated {len(EVENTS)} original NoxForge sound events")


if __name__ == "__main__":
    main()
