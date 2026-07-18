from __future__ import annotations

import configparser
import gzip
import json
import struct
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AURORAE = ROOT / "aurorae/io.github.loofiboss.noxforge.desktop"
ICONS = ROOT / "icons/NoxForge"
WALLPAPER = ROOT / "wallpapers/NoxForge"


def ids(path: Path) -> set[str]:
    return {element.get("id") for element in ET.parse(path).iter() if element.get("id")}


class PhaseThreeTests(unittest.TestCase):
    def test_aurorae_active_inactive_and_button_states(self) -> None:
        positions = {"top", "topright", "right", "bottomright", "bottom", "bottomleft", "left", "topleft", "center"}
        decoration = ids(AURORAE / "decoration.svg")
        for prefix in ("decoration", "decoration-inactive"):
            self.assertTrue({f"{prefix}-{position}" for position in positions}.issubset(decoration))
        states = {"active", "inactive", "hover", "hover-inactive", "pressed", "pressed-inactive", "deactivated", "deactivated-inactive"}
        for name in ("close", "minimize", "maximize", "restore"):
            with self.subTest(name=name):
                self.assertTrue({f"{state}-center" for state in states}.issubset(ids(AURORAE / f"{name}.svg")))

    def test_aurorae_compression_is_reproducible(self) -> None:
        for svg in sorted(AURORAE.glob("*.svg")):
            with self.subTest(svg=svg.name):
                svgz = svg.with_suffix(".svgz")
                self.assertEqual(gzip.decompress(svgz.read_bytes()), svg.read_bytes())
                self.assertEqual(struct.unpack("<I", svgz.read_bytes()[4:8])[0], 0)

    def test_icon_theme_has_system_coverage_and_neutral_app_fallback(self) -> None:
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(ICONS / "index.theme", encoding="utf-8")
        self.assertEqual(parser["Icon Theme"]["Inherits"], "hicolor")
        icons = list((ICONS / "scalable").glob("*/*.svg"))
        self.assertGreaterEqual(len(icons), 120)
        self.assertEqual(
            {path.parent.name for path in icons},
            {"actions", "applets", "categories", "devices", "emblems", "mimetypes", "places", "preferences", "status"},
        )

    def test_wallpaper_has_editable_source_and_release_output(self) -> None:
        source = ET.parse(WALLPAPER / "contents/source/NoxForge.svg").getroot()
        self.assertEqual(source.get("viewBox"), "0 0 2560 1440")
        png = (WALLPAPER / "contents/images/2560x1440.png").read_bytes()[:24]
        self.assertEqual(struct.unpack(">II", png[16:24]), (2560, 1440))
        metadata = json.loads((WALLPAPER / "metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["KPlugin"]["License"], "MIT")

    def test_artwork_provenance_is_recorded(self) -> None:
        text = (ROOT / "docs/ARTWORK.md").read_text(encoding="utf-8")
        self.assertIn("No artwork from Breeze", text)
        self.assertIn("another theme", text)
        self.assertIn("system icon SVGs", text)


if __name__ == "__main__":
    unittest.main()
