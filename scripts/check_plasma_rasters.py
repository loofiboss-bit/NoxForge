#!/usr/bin/env python3
"""Generate and verify the complete NoxForge Plasma Style raster atlas."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop"
CONTRACT_PATH = ROOT / "design/plasma-semantic-contract.json"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
if VERSION.startswith("6."):
    EVIDENCE_SERIES = "v6"
elif VERSION.startswith("7."):
    EVIDENCE_SERIES = "v7"
elif VERSION.startswith("8."):
    EVIDENCE_SERIES = "v8"
else:
    EVIDENCE_SERIES = "v9"
EVIDENCE = ROOT / f"docs/evidence/{EVIDENCE_SERIES}/plasma-shell"
MANIFEST = EVIDENCE / "atlas-manifest.json"
SCALES = (
    (1.0, "100"),
    (1.25, "125"),
    (1.4, "140"),
    (1.5, "150"),
    (1.75, "175"),
    (2.0, "200"),
)
COLUMNS = 8
GUTTER = 4


def dimension(value: str | None) -> int:
    if value is None:
        raise ValueError("missing SVG dimension")
    return round(float(value.removesuffix("px")))


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"invalid raster output: {path}")
    return struct.unpack(">II", data[16:24])


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def asset_paths(contract: dict[str, object]) -> list[str]:
    widgets = [f"widgets/{name}.svg" for name in contract["widgetFamilies"]]
    weather = [f"weather/{name}.svg" for name in contract["weatherFamilies"]]
    variants = list(contract["backgroundVariants"])
    return widgets + weather + ["dialogs/background.svg"] + variants


def render_asset(magick: str, source: Path, output: Path, scale: float) -> tuple[int, int]:
    root = ET.parse(source).getroot()
    width = round(dimension(root.get("width")) * scale / 4)
    height = round(dimension(root.get("height")) * scale / 4)
    inset = max(8, round(12 * scale))
    subprocess.run(
        [
            magick,
            "-background",
            "none",
            str(source),
            "-trim",
            "+repage",
            "-resize",
            "400%",
            "-resize",
            f"{width - inset * 2}x{height - inset * 2}>",
            "-gravity",
            "center",
            "-extent",
            f"{width}x{height}",
            "-strip",
            f"PNG32:{output}",
        ],
        check=True,
    )
    alpha = float(
        subprocess.run(
            [magick, str(output), "-format", "%[fx:mean.a]", "info:"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    )
    if png_dimensions(output) != (width, height) or alpha <= 0:
        raise RuntimeError(f"empty, clipped, or wrongly sized raster: {source.relative_to(THEME)} at {scale}")
    return width, height


def compose_atlas(
    magick: str,
    tiles: list[Path],
    output: Path,
    cell: tuple[int, int],
) -> tuple[int, int]:
    rows = math.ceil(len(tiles) / COLUMNS)
    width = COLUMNS * cell[0] + (COLUMNS + 1) * GUTTER
    height = rows * cell[1] + (rows + 1) * GUTTER
    command = [magick, "-size", f"{width}x{height}", "xc:#0D1419"]
    for index, tile in enumerate(tiles):
        x = GUTTER + (index % COLUMNS) * (cell[0] + GUTTER)
        y = GUTTER + (index // COLUMNS) * (cell[1] + GUTTER)
        command.extend([str(tile), "-geometry", f"+{x}+{y}", "-composite"])
    command.extend(["-strip", str(output)])
    subprocess.run(command, check=True)
    if png_dimensions(output) != (width, height):
        raise RuntimeError(f"wrongly sized Plasma atlas: {output.name}")
    return width, height


def render_all(target: Path, magick: str, contract: dict[str, object]) -> tuple[dict[str, object], list[Path]]:
    assets = asset_paths(contract)
    expected_count = len(contract["widgetFamilies"]) + len(contract["weatherFamilies"]) + 1 + len(
        contract["backgroundVariants"]
    )
    if len(assets) != expected_count or len(set(assets)) != len(assets):
        raise RuntimeError("Plasma atlas asset inventory is incomplete or duplicated")

    atlas_entries: list[dict[str, object]] = []
    material_entries: list[dict[str, object]] = []
    outputs: list[Path] = []
    source_entries = [
        {
            "path": relative,
            "sha256": digest(THEME / relative),
            "recipe": contract["familyRecipes"].get(Path(relative).stem),
        }
        for relative in assets
    ]
    for scale, label in SCALES:
        tiles: list[Path] = []
        tiles_by_asset: dict[str, Path] = {}
        cell: tuple[int, int] | None = None
        for index, relative in enumerate(assets):
            output = target / f"{index:02d}-{label}.png"
            rendered = render_asset(magick, THEME / relative, output, scale)
            if cell is None:
                cell = rendered
            elif rendered != cell:
                raise RuntimeError(f"Plasma atlas source dimensions differ: {relative}")
            tiles.append(output)
            tiles_by_asset[relative] = output
        assert cell is not None
        atlas = target / f"plasma-style-atlas-{label}pct.png"
        width, height = compose_atlas(magick, tiles, atlas, cell)
        outputs.append(atlas)
        atlas_entries.append(
            {
                "scale": scale,
                "file": atlas.name,
                "width": width,
                "height": height,
                "sha256": digest(atlas),
            }
        )
        variants = contract["backgroundVariantRecipes"]
        for blur in ("on", "off"):
            material_tiles = [
                tiles_by_asset[relative]
                for relative in contract["backgroundVariants"]
                if variants[relative]["blur"] == blur
            ]
            material_atlas = target / f"material-atlas-blur-{blur}-{label}pct.png"
            material_width, material_height = compose_atlas(
                magick,
                material_tiles,
                material_atlas,
                cell,
            )
            outputs.append(material_atlas)
            material_entries.append(
                {
                    "scale": scale,
                    "blur": blur,
                    "file": material_atlas.name,
                    "assetCount": len(material_tiles),
                    "width": material_width,
                    "height": material_height,
                    "sha256": digest(material_atlas),
                }
            )

    capture_matrix = contract["sourceCaptureMatrix"]
    scenario_count = math.prod(
        len(capture_matrix[key])
        for key in ("scales", "panelEdges", "layouts", "virtualOutputs", "blur")
    )
    manifest = {
        "schemaVersion": 2,
        "version": VERSION,
        "plasmaVersion": contract["plasmaVersion"],
        "themeId": contract["themeId"],
        "evidenceClass": capture_matrix["evidenceClass"],
        "qualifiesLivePlasma": capture_matrix["qualifiesLivePlasma"],
        "limitations": [
            "Static SVG source rasterization does not prove a running Plasma shell or compositor.",
            "Live panel, blur, compact-layout, and multi-output checks remain pending.",
        ],
        "assetCount": len(assets),
        "columns": COLUMNS,
        "assets": source_entries,
        "qualifiedSurfaces": contract["qualifiedSurfaces"],
        "stateFrames": contract["stateFrames"],
        "orientedTaskStates": contract["orientedTaskStates"],
        "sourceCaptureMatrix": capture_matrix,
        "staticScenarioCount": scenario_count,
        "atlases": atlas_entries,
        "materialAtlases": material_entries,
    }
    return manifest, outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write the generated atlas evidence")
    mode.add_argument("--check", action="store_true", help="verify committed atlas evidence (default)")
    arguments = parser.parse_args()

    magick = shutil.which("magick")
    if not magick:
        raise SystemExit("ImageMagick 'magick' is required for Plasma raster checks")
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="noxforge-plasma-atlas-") as temporary:
        generated, atlases = render_all(Path(temporary), magick, contract)
        generated_text = json.dumps(generated, indent=2, sort_keys=True) + "\n"
        if arguments.write:
            EVIDENCE.mkdir(parents=True, exist_ok=True)
            for atlas in atlases:
                shutil.copyfile(atlas, EVIDENCE / atlas.name)
            MANIFEST.write_text(generated_text, encoding="utf-8", newline="\n")
        else:
            if not MANIFEST.is_file() or MANIFEST.read_text(encoding="utf-8") != generated_text:
                raise SystemExit("stale Plasma raster atlas manifest; run scripts/check_plasma_rasters.py --write")
            for atlas in atlases:
                committed = EVIDENCE / atlas.name
                if not committed.is_file() or committed.read_bytes() != atlas.read_bytes():
                    raise SystemExit(
                        f"stale Plasma raster atlas: {atlas.name}; run scripts/check_plasma_rasters.py --write"
                    )

    action = "written" if arguments.write else "passed"
    print(
        f"Plasma raster atlas {action}: {generated['assetCount']} assets x "
        f"{len(SCALES)} scales, complete states and panel orientations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
