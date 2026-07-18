from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME_ID = "io.github.loofiboss.noxforge.desktop"


class VisualContractTests(unittest.TestCase):
    def test_qml_surfaces_use_generated_tokens_without_raw_palette_values(self) -> None:
        files = (
            ROOT / f"look-and-feel/{THEME_ID}/contents/splash/Splash.qml",
            ROOT / f"look-and-feel/{THEME_ID}/contents/logout/Logout.qml",
            ROOT / f"kwin/tabbox/{THEME_ID}/contents/ui/main.qml",
            ROOT / "sddm/NoxForge/Main.qml",
        )
        for path in files:
            text = path.read_text(encoding="utf-8")
            self.assertIn("Tokens {", text)
            self.assertIsNone(re.search(r"#[0-9A-Fa-f]{6,8}", text))

    def test_token_and_brand_copies_are_physical_and_identical(self) -> None:
        roots = (
            ROOT / f"look-and-feel/{THEME_ID}/contents/splash",
            ROOT / f"look-and-feel/{THEME_ID}/contents/logout",
            ROOT / f"kwin/tabbox/{THEME_ID}/contents/ui",
            ROOT / "sddm/NoxForge",
        )
        for filename in ("Tokens.qml", "NoxForgeMark.svg"):
            paths = [root / filename for root in roots]
            self.assertFalse(any(path.is_symlink() for path in paths))
            self.assertEqual(len({path.read_bytes() for path in paths}), 1)

    def test_plasma_contract_has_exact_target_family_count(self) -> None:
        contract = json.loads((ROOT / "design/plasma-semantic-contract.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["plasmaVersion"], "6.7")
        self.assertEqual(len(contract["widgetFamilies"]), 43)
        for family in ("dragger", "glowbar", "margins-highlight", "monitor"):
            self.assertIn(family, contract["widgetFamilies"])


if __name__ == "__main__":
    unittest.main()
