from __future__ import annotations

import configparser
import hashlib
import json
import struct
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"not a PNG: {path}")
    return struct.unpack(">II", data[16:24])


class LuminaContractTests(unittest.TestCase):
    def test_aurorae_shadow_uses_the_plasma_padding_contract(self) -> None:
        parser = configparser.ConfigParser(interpolation=None, strict=True)
        parser.optionxform = str.lower
        parser.read(
            ROOT / "aurorae/io.github.loofiboss.noxforge.desktop/io.github.loofiboss.noxforge.desktoprc",
            encoding="utf-8",
        )
        general = parser["General"]
        layout = parser["Layout"]
        self.assertEqual(general["shadow"].lower(), "false")
        self.assertEqual(general.get("rightbuttons"), "IAX")
        for key in ("paddingtop", "paddingbottom", "paddingleft", "paddingright"):
            self.assertTrue(key not in layout or int(layout[key]) == 0)
        self.assertFalse(
            any(key.startswith(("activeshadow", "inactiveshadow")) for key in general)
        )

    def test_active_plan_and_preview_are_current(self) -> None:
        manifest = json.loads(
            (ROOT / "distribution/release-manifest.json").read_text(encoding="utf-8")
        )
        self.assertIn(manifest["release"]["activePlan"], ("docs/NOXFORGE_V11_PLAN.md", "docs/NOXFORGE_V12_PLAN.md", "docs/NOXFORGE_V13_PLAN.md"))
        self.assertIn(manifest["release"]["stableVersion"], ("11.0.0", "12.0.0", "12.0.1", "13.0.0", "13.0.1"))
        self.assertIn((ROOT / "VERSION").read_text(encoding="utf-8").strip(), ("11.0.0", "12.0.0", "12.0.1", "13.0.0", "13.0.1"))
        preview = ROOT / "sddm/NoxForge/preview.png"
        evidence = ROOT / "docs/evidence/sddm_login_100pct.png"
        self.assertEqual(png_dimensions(preview), (960, 540))
        self.assertEqual(hashlib.sha256(preview.read_bytes()).digest(), hashlib.sha256(evidence.read_bytes()).digest())


if __name__ == "__main__":
    unittest.main()
