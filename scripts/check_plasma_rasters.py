#!/usr/bin/env python3
"""Raster-smoke representative Plasma SVGs at the v2 scale matrix."""

from __future__ import annotations

import shutil
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop"
ASSETS = (
    "widgets/background.svg",
    "widgets/button.svg",
    "widgets/tasks.svg",
    "widgets/scrollbar.svg",
    "widgets/tabbar.svg",
    "widgets/dragger.svg",
    "widgets/monitor.svg",
    "weather/wind-arrows.svg",
)
SCALES = (1.0, 1.25, 1.4, 2.0)


def dimension(value: str | None) -> int:
    if value is None:
        raise ValueError("missing SVG dimension")
    return round(float(value.removesuffix("px")))


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"invalid raster output: {path}")
    return struct.unpack(">II", data[16:24])


def main() -> int:
    magick = shutil.which("magick")
    if not magick:
        raise SystemExit("ImageMagick 'magick' is required for Plasma raster checks")
    with tempfile.TemporaryDirectory(prefix="noxforge-plasma-raster-") as temporary:
        target = Path(temporary)
        outputs: list[Path] = []
        for relative in ASSETS:
            source = THEME / relative
            root = ET.parse(source).getroot()
            width, height = dimension(root.get("width")), dimension(root.get("height"))
            for scale in SCALES:
                expected = (round(width * scale), round(height * scale))
                output = target / f"{source.stem}-{str(scale).replace('.', '_')}.png"
                subprocess.run(
                    [magick, "-background", "none", str(source), "-resize", f"{expected[0]}x{expected[1]}!", str(output)],
                    check=True,
                )
                if png_dimensions(output) != expected or output.stat().st_size < 256:
                    raise SystemExit(f"empty, clipped, or wrongly sized raster: {relative} at {scale}")
                outputs.append(output)
        if len({path.read_bytes() for path in outputs}) != len(outputs):
            raise SystemExit("Plasma scale raster matrix reused identical image data")
    print(f"Plasma raster matrix passed: {len(ASSETS)} assets x {len(SCALES)} scales")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
