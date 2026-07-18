from __future__ import annotations

import configparser
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("noxforge_validate", ROOT / "scripts/validate.py")
assert SPEC and SPEC.loader
VALIDATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATE)


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    channels = []
    for channel in rgb:
        value = channel / 255
        channels.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast(first: tuple[int, int, int], second: tuple[int, int, int]) -> float:
    light, dark = sorted((relative_luminance(first), relative_luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


class PhaseOneTests(unittest.TestCase):
    def test_repository_validation(self) -> None:
        VALIDATE.validate()

    def test_locked_text_contrast(self) -> None:
        self.assertGreaterEqual(contrast((232, 240, 242), (14, 19, 24)), 7.0)
        self.assertGreaterEqual(contrast((14, 19, 24), (163, 255, 71)), 7.0)

    def test_color_scheme_is_complete_and_consistent(self) -> None:
        standalone = ROOT / "color-schemes/NoxForgeDark.colors"
        embedded = ROOT / "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop/colors"
        self.assertEqual(standalone.read_bytes(), embedded.read_bytes())
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(standalone, encoding="utf-8")
        self.assertEqual(parser["General"]["ColorScheme"], "NoxForgeDark")
        self.assertEqual(parser["Colors:Selection"]["BackgroundNormal"], "163,255,71")


if __name__ == "__main__":
    unittest.main()
