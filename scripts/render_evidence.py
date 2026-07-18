#!/usr/bin/env python3
"""Capture authentic offscreen Qt and SDDM surfaces for the v2 visual gate."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build/cmake"
EVIDENCE = ROOT / "docs/evidence"
SCALES = (("100", "1.0"), ("125", "1.25"), ("140", "1.4"), ("200", "2.0"))
ICON_NAMES = (
    "actions/go-previous.svg",
    "actions/media-playback-pause.svg",
    "actions/media-playback-stop.svg",
    "status/audio-volume-muted.svg",
    "status/battery-charging.svg",
    "status/network-wireless-disconnected.svg",
)


def run(command: list[str], *, env: dict[str, str] | None = None) -> None:
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def main() -> int:
    gallery = BUILD / "noxforge_widget_gallery"
    sddm_renderer = BUILD / "noxforge_sddm_renderer"
    magick = shutil.which("magick")
    if not gallery.is_file() or not sddm_renderer.is_file() or not magick:
        raise SystemExit("Build the CMake targets and install ImageMagick before rendering evidence")
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="noxforge-evidence-") as temporary:
        temp = Path(temporary)
        gallery_outputs: list[Path] = []
        for direction in ("ltr", "rtl"):
            for percent, scale in SCALES:
                output = temp / f"gallery_{direction}_{percent}pct.png"
                env = os.environ.copy()
                env.update({
                    "QT_QPA_PLATFORM": "offscreen",
                    "QT_PLUGIN_PATH": str(BUILD / "plugins"),
                    "QT_SCALE_FACTOR": scale,
                })
                command = [str(gallery)]
                if direction == "rtl":
                    command.append("--rtl")
                command.append(str(output))
                run(command, env=env)
                gallery_outputs.append(output)

        data_output = temp / "gallery_data_ltr_100pct.png"
        env = os.environ.copy()
        env.update({"QT_QPA_PLATFORM": "offscreen", "QT_PLUGIN_PATH": str(BUILD / "plugins"), "QT_SCALE_FACTOR": "1.0"})
        run([str(gallery), "--data", str(data_output)], env=env)
        gallery_outputs.append(data_output)

        sddm_output = temp / "sddm_login_100pct.png"
        run(
            [
                str(sddm_renderer),
                str(ROOT / "sddm/NoxForge/Main.qml"),
                str(ROOT / "sddm/NoxForge/background.png"),
                str(sddm_output),
            ],
            env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
        )

        tiles: list[Path] = []
        for row, relative in enumerate(ICON_NAMES):
            for size in (16, 22, 24, 32, 48):
                source_root = ROOT / f"icons/NoxForge/{size}x{size}" if size in (16, 22) else ROOT / "icons/NoxForge/scalable"
                tile = temp / f"icon-{row}-{size}.png"
                run([
                    magick, "-background", "#0E1318", str(source_root / relative), "-resize", f"{size}x{size}",
                    "-gravity", "center", "-extent", "72x72", str(tile),
                ])
                tiles.append(tile)
        icon_sheet = temp / "icons_16_22_24_32_48px.png"
        run([magick, "montage", *map(str, tiles), "-tile", "5x", "-geometry", "+4+4", "-background", "#141B21", str(icon_sheet)])

        aurorae_decoration = temp / "aurorae_decoration.png"
        aurorae_buttons = temp / "aurorae_close_states.png"
        run([magick, str(ROOT / "aurorae/io.github.loofiboss.noxforge.desktop/decoration.svg"), "-resize", "640x320", str(aurorae_decoration)])
        run([magick, str(ROOT / "aurorae/io.github.loofiboss.noxforge.desktop/close.svg"), "-resize", "1024x96", str(aurorae_buttons)])

        hashes = {path.read_bytes() for path in gallery_outputs}
        if len(hashes) != len(gallery_outputs):
            raise SystemExit("render matrix reused identical image data")
        for path in (*gallery_outputs, sddm_output, icon_sheet, aurorae_decoration, aurorae_buttons):
            shutil.copyfile(path, EVIDENCE / path.name)
        shutil.copyfile(sddm_output, ROOT / "sddm/NoxForge/preview.png")
        run([magick, str(gallery_outputs[0]), "-resize", "480x380", str(ROOT / f"look-and-feel/{THEME_ID}/contents/previews/preview.png")])
    print("Rendered 9 Qt matrix captures, authentic SDDM preview, icon contact sheet, and Aurorae structural evidence")
    return 0


THEME_ID = "io.github.loofiboss.noxforge.desktop"

if __name__ == "__main__":
    raise SystemExit(main())
