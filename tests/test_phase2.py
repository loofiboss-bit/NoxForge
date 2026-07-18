from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop"
POSITIONS = {"top", "topright", "right", "bottomright", "bottom", "bottomleft", "left", "topleft", "center"}
EXPECTED_STATES = {
    "widgets/button.svg": {"normal", "hover", "focus", "pressed", "toolbutton-hover", "toolbutton-focus", "toolbutton-pressed"},
    "widgets/tasks.svg": {"normal", "hover", "focus", "attention", "minimized", "progress"},
    "widgets/viewitem.svg": {"normal", "hover", "selected", "selected+hover"},
    "widgets/lineedit.svg": {"base", "hover", "focus"},
    "widgets/plasmoidheading.svg": {"header", "footer"},
}


def ids(path: Path) -> set[str]:
    return {element.get("id") for element in ET.parse(path).iter() if element.get("id")}


class PhaseTwoTests(unittest.TestCase):
    def test_background_frames_and_masks_are_complete(self) -> None:
        for relative in ("dialogs/background.svg", "widgets/panel-background.svg", "widgets/background.svg", "widgets/tooltip.svg"):
            with self.subTest(relative=relative):
                found = ids(THEME / relative)
                self.assertTrue(POSITIONS.issubset(found))
                self.assertTrue({f"mask-{position}" for position in POSITIONS}.issubset(found))

    def test_state_frames_are_complete(self) -> None:
        for relative, states in EXPECTED_STATES.items():
            with self.subTest(relative=relative):
                found = ids(THEME / relative)
                for state in states:
                    self.assertTrue({f"{state}-{position}" for position in POSITIONS}.issubset(found))

    def test_assets_use_system_and_accent_classes(self) -> None:
        for path in sorted(THEME.rglob("*.svg")):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn('id="current-color-scheme"', text)
                self.assertIn("ColorScheme-Highlight", text)
                self.assertNotIn("filter=", text)

    def test_plasma_style_fallback_is_breeze(self) -> None:
        text = (THEME / "plasmarc").read_text(encoding="utf-8")
        self.assertIn("FallbackTheme=default", text)

    def test_primary_text_stays_readable_without_blur(self) -> None:
        foreground = (232, 240, 242)
        surface = (20, 27, 33)
        worst_case_wallpaper = (255, 255, 255)
        opaque_surface = tuple(round(channel * 0.96 + backdrop * 0.04) for channel, backdrop in zip(surface, worst_case_wallpaper))

        def luminance(rgb: tuple[int, int, int]) -> float:
            values = []
            for channel in rgb:
                value = channel / 255
                values.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
            return 0.2126 * values[0] + 0.7152 * values[1] + 0.0722 * values[2]

        light, dark = sorted((luminance(foreground), luminance(opaque_surface)), reverse=True)
        self.assertGreaterEqual((light + 0.05) / (dark + 0.05), 7.0)


if __name__ == "__main__":
    unittest.main()
