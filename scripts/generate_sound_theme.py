#!/usr/bin/env python3
"""Synthesize Tactile Forge Audio v2 — original, restrained NoxForge sound theme."""

from __future__ import annotations

import argparse
import hashlib
import json
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

# 24 distinct Tactile Forge Audio v2 acoustic recipes:
# (duration_s, ((freq_hz, gain), ...), decay_rate, harmonic_profile, click_amount)
SPECS: dict[str, tuple[float, tuple[tuple[float, float], ...], float, str, float]] = {
    "tick": (0.065, ((980.0, 0.16), (1470.0, 0.04)), 34.0, "anvil", 0.18),
    "volume": (0.075, ((740.0, 0.15), (1108.7, 0.06)), 28.0, "marimba", 0.12),
    "button": (0.082, ((830.6, 0.15), (1244.5, 0.05)), 26.0, "anvil", 0.22),
    "modifier": (0.070, ((622.25, 0.14), (932.33, 0.04)), 30.0, "anvil", 0.16),
    "bell": (0.180, ((1046.5, 0.12), (1567.98, 0.07)), 14.0, "chime", 0.08),
    "completion-rotation": (0.090, ((1174.66, 0.12), (1760.0, 0.05)), 24.0, "marimba", 0.10),
    "success": (0.28, ((523.25, 0.11), (783.99, 0.10), (1046.5, 0.07)), 10.5, "chime", 0.06),
    "outcome-success": (0.31, ((587.33, 0.11), (880.0, 0.10), (1174.66, 0.07)), 9.5, "chime", 0.05),
    "warning": (0.34, ((440.0, 0.11), (329.63, 0.13)), 9.5, "warm", 0.05),
    "completion-partial": (0.26, ((493.88, 0.10), (392.0, 0.11)), 11.0, "warm", 0.06),
    "battery-warn": (0.38, ((392.0, 0.12), (293.66, 0.13)), 8.5, "warm", 0.04),
    "error": (0.32, ((196.0, 0.14), (155.56, 0.13)), 10.0, "muted", 0.08),
    "outcome-failure": (0.35, ((220.0, 0.13), (146.83, 0.13)), 9.0, "muted", 0.07),
    "login": (0.54, ((261.63, 0.09), (392.0, 0.08), (523.25, 0.08), (659.25, 0.07)), 7.0, "chime", 0.04),
    "service-login": (0.46, ((293.66, 0.09), (440.0, 0.08), (659.25, 0.07)), 8.0, "chime", 0.04),
    "logout": (0.44, ((523.25, 0.09), (329.63, 0.08), (220.0, 0.07)), 8.0, "warm", 0.03),
    "service-logout": (0.40, ((440.0, 0.09), (293.66, 0.08), (196.0, 0.06)), 8.5, "warm", 0.03),
    "device-added": (0.24, ((349.23, 0.09), (523.25, 0.08), (698.46, 0.07)), 12.0, "marimba", 0.09),
    "power-plug": (0.25, ((392.0, 0.10), (587.33, 0.09), (783.99, 0.07)), 12.0, "anvil", 0.12),
    "device-removed": (0.24, ((698.46, 0.08), (523.25, 0.08), (349.23, 0.07)), 12.0, "marimba", 0.08),
    "power-unplug": (0.25, ((587.33, 0.09), (392.0, 0.08), (261.63, 0.06)), 12.5, "warm", 0.07),
    "trash": (0.21, ((415.30, 0.10), (277.18, 0.09), (185.0, 0.07)), 15.0, "anvil", 0.16),
    "message": (0.20, ((740.0, 0.09), (987.77, 0.06)), 13.0, "chime", 0.07),
    "email": (0.23, ((659.25, 0.09), (987.77, 0.07), (1318.51, 0.05)), 12.0, "chime", 0.06),
    "question": (0.22, ((587.33, 0.09), (783.99, 0.07)), 12.5, "marimba", 0.07),
    "alarm": (0.70, ((440.0, 0.11), (880.0, 0.08), (440.0, 0.09)), 7.5, "chime", 0.05),
    "incoming-call": (0.64, ((523.25, 0.10), (659.25, 0.09), (523.25, 0.09), (783.99, 0.08)), 8.0, "chime", 0.06),
}

EVENTS = {
    "audio-volume-change": "volume",
    "button-pressed": "button",
    "button-pressed-modifier": "modifier",
    "bell-window-system": "bell",
    "completion-success": "success",
    "outcome-success": "outcome-success",
    "completion-partial": "completion-partial",
    "completion-rotation": "completion-rotation",
    "completion-fail": "error",
    "outcome-failure": "outcome-failure",
    "desktop-login": "login",
    "service-login": "service-login",
    "desktop-logout": "logout",
    "service-logout": "service-logout",
    "device-added": "device-added",
    "power-plug": "power-plug",
    "device-removed": "device-removed",
    "power-unplug": "power-unplug",
    "dialog-information": "message",
    "dialog-question": "question",
    "message-new-email": "email",
    "message-new-instant": "message",
    "dialog-warning": "warning",
    "dialog-warning-auth": "warning",
    "battery-caution": "battery-warn",
    "battery-low": "battery-warn",
    "dialog-error": "error",
    "dialog-error-serious": "outcome-failure",
    "alarm-clock-elapsed": "alarm",
    "phone-incoming-call": "incoming-call",
    "trash-empty": "trash",
    "theme-demo": "login",
}

HARMONIC_RATIOS: dict[str, tuple[tuple[float, float], ...]] = {
    "anvil": ((1.0, 1.0), (2.01, 0.24), (3.12, 0.11), (4.28, 0.05)),
    "marimba": ((1.0, 1.0), (2.0, 0.18), (3.98, 0.07)),
    "chime": ((1.0, 1.0), (2.0, 0.28), (3.0, 0.12), (4.5, 0.04)),
    "warm": ((1.0, 1.0), (1.5, 0.16), (2.0, 0.12)),
    "muted": ((1.0, 1.0), (1.414, 0.18), (2.0, 0.08)),
}


def synthesize(
    name: str,
    duration: float,
    tones: tuple[tuple[float, float], ...],
    decay_rate: float,
    profile: str,
    click_amount: float,
) -> bytes:
    rng = random.Random(name)
    sample_count = round(duration * RATE)
    segment_length = sample_count / len(tones)
    partials = HARMONIC_RATIOS[profile]
    raw: list[float] = []
    lp_prev = 0.0
    lp_alpha = 0.42 if profile == "muted" else 0.68

    for index in range(sample_count):
        segment = min(len(tones) - 1, int(index / segment_length))
        frequency, gain = tones[segment]
        local = (index - segment * segment_length) / RATE
        attack = min(1.0, local / 0.005)
        tail_fade = min(1.0, (sample_count - 1 - index) / (0.012 * RATE))
        envelope = attack * tail_fade * math.exp(-local * decay_rate)

        sig = 0.0
        for ratio, amp in partials:
            partial_decay = math.exp(-local * (decay_rate * (0.4 + 0.35 * ratio)))
            sig += math.sin(2.0 * math.pi * frequency * ratio * local) * amp * partial_decay

        transient = (rng.random() * 2.0 - 1.0) * click_amount * math.exp(-local * 140.0)
        sample_val = sig * gain * envelope + transient * gain
        lp_prev = lp_prev + lp_alpha * (sample_val - lp_prev)
        raw.append(max(-0.85, min(0.85, lp_prev)))

    frames = bytearray()
    for val in raw:
        frames.extend(struct.pack("<h", round(val * 32767)))
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
    # Remove stale legacy WAVs no longer in SPECS
    for old_wav in source_dir.glob("*.wav"):
        if old_wav.stem not in SPECS:
            old_wav.unlink()
    encoded: dict[str, Path] = {}
    measurements: dict[str, dict[str, float]] = {}
    for name, (duration, tones, decay_rate, profile, click_amount) in SPECS.items():
        wav_path = source_dir / f"{name}.wav"
        oga_path = stereo_dir / f"_{name}.oga"
        target = SOUND_CONTRACT["alarmTargetRmsDbfs"] if name in {"alarm", "incoming-call"} else SOUND_CONTRACT["targetRmsDbfs"]
        frames = normalize(synthesize(name, duration, tones, decay_rate, profile, click_amount), target)
        write_wav(wav_path, frames)
        encode(wav_path, oga_path)
        normalize_ogg(oga_path, name)
        encoded[name] = oga_path
        measurements[name] = metrics(frames)
    for event, source in EVENTS.items():
        shutil.copyfile(encoded[source], stereo_dir / f"{event}.oga")
    for path in encoded.values():
        path.unlink()
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    (theme / "index.theme").write_text(
        f"# @noxforge-version: {version}\n[Sound Theme]\nName=NoxForge\nComment=Original Tactile Forge Audio v2 for KDE Plasma\nDirectories=stereo\nExample=theme-demo\n\n[stereo]\nOutputProfile=stereo\n",
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
                        "profile": profile,
                        **measurements[name],
                    }
                    for name, (duration, tones, _decay, profile, _click) in SPECS.items()
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
        print(f"Generated {len(EVENTS)} Tactile Forge Audio v2 events across {len(SPECS)} sources")
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
    print(f"Verified {len(EVENTS)} Tactile Forge Audio v2 events using {policy} ({encoder})")


if __name__ == "__main__":
    main()
