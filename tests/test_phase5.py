from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(first: str, second: str) -> float:
    light, dark = sorted((relative_luminance(first), relative_luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


class PhaseFiveDesignTests(unittest.TestCase):
    def test_design_authority_and_schema(self) -> None:
        design = (ROOT / "DESIGN.md").read_text(encoding="utf-8")
        self.assertIn("Industrial Precision", design)
        self.assertIn("Hallmark", design)
        tokens = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))
        self.assertEqual(tokens["schemaVersion"], 2)
        self.assertEqual(tokens["colors"]["surfaceSelected"], "#26361D")
        self.assertEqual(tokens["geometry"]["forgeNotch"], 4)

    def test_large_selection_is_dark_and_readable(self) -> None:
        tokens = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))
        colors = tokens["colors"]
        self.assertGreaterEqual(contrast(colors["textPrimary"], colors["surfaceSelected"]), 7.0)
        self.assertGreaterEqual(contrast(colors["accentInk"], colors["accent"]), 7.0)
        self.assertLess(relative_luminance(colors["surfaceSelected"]), 0.06)


if __name__ == "__main__":
    unittest.main()
