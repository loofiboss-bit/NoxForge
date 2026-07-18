from __future__ import annotations

import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME_ID = "io.github.loofiboss.noxforge.desktop"
LOOK = ROOT / "look-and-feel" / THEME_ID
PLASMA = ROOT / "plasma/desktoptheme" / THEME_ID


class PhaseSixGlobalThemeTests(unittest.TestCase):
    def test_strict_plasma6_look_and_feel_contract(self) -> None:
        for name in ("metadata.json", "manifest.json"):
            data = json.loads((LOOK / name).read_text(encoding="utf-8"))
            self.assertEqual(data["KPackageStructure"], "Plasma/LookAndFeel")
            self.assertEqual(data["KPlugin"]["Id"], THEME_ID)
        defaults = (LOOK / "contents/defaults").read_text(encoding="utf-8").lower()
        self.assertNotIn("breeze", defaults)
        self.assertIn("widgetstyle=noxforge", defaults)
        self.assertIn("cursortheme=noxforge-cursors", defaults)

    def test_shell_qml_and_optional_layout_are_present(self) -> None:
        self.assertTrue((LOOK / "contents/splash/Splash.qml").is_file())
        self.assertTrue((LOOK / "contents/logout/Logout.qml").is_file())
        layout = (LOOK / "contents/layouts/org.kde.plasma.desktop-layout.js").read_text(encoding="utf-8")
        self.assertIn("new Panel", layout)
        self.assertNotIn("remove", layout.lower())

    def test_expanded_plasma_assets_are_original_xml(self) -> None:
        required = {
            "actionbutton.svg",
            "arrows.svg",
            "checkmarks.svg",
            "frame.svg",
            "listitem.svg",
            "menubaritem.svg",
            "radiobutton.svg",
            "scrollbar.svg",
            "slider.svg",
            "switch.svg",
            "tabbar.svg",
            "toolbar.svg",
        }
        found = {path.name for path in (PLASMA / "widgets").glob("*.svg")}
        self.assertTrue(required.issubset(found))
        for name in required:
            root = ET.parse(PLASMA / "widgets" / name).getroot()
            self.assertEqual(root.tag.rsplit("}", 1)[-1], "svg")
        self.assertGreaterEqual(len(list(PLASMA.rglob("*.svg"))), 50)
        self.assertNotIn("FallbackTheme", (PLASMA / "plasmarc").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
