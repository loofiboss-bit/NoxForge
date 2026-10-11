from __future__ import annotations

import configparser
import hashlib
import json
import subprocess
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "icons/NoxForge"
CONTRACT = json.loads((ROOT / "design/v7-icon-contract.json").read_text(encoding="utf-8"))


class V7PhaseTwoTests(unittest.TestCase):
    def test_overlay_uses_verified_fedora_fallback_chain(self) -> None:
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(THEME / "index.theme", encoding="utf-8")
        self.assertEqual(
            parser["Icon Theme"]["Inherits"].split(","),
            ["breeze-dark", "breeze", "hicolor"],
        )
        for theme_name in CONTRACT["overlayPolicy"]["inherits"]:
            self.assertTrue((Path("/usr/share/icons") / theme_name).is_dir(), theme_name)

    def test_required_core_icons_are_original_distinct_physical_svgs(self) -> None:
        hashes: set[str] = set()
        for entry in CONTRACT["required"]:
            path = THEME / "scalable" / entry["context"] / f"{entry['name']}.svg"
            with self.subTest(icon=entry["name"]):
                self.assertTrue(path.is_file())
                self.assertFalse(path.is_symlink())
                root = ET.parse(path).getroot()
                self.assertEqual(root.get("viewBox"), "0 0 24 24")
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertNotIn(digest, hashes)
                hashes.add(digest)

    def test_logout_requests_distinct_session_semantics(self) -> None:
        qml = (
            ROOT
            / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/logout/Logout.qml"
        ).read_text(encoding="utf-8")
        for name in (
            "system-lock-screen",
            "system-log-out",
            "system-suspend",
            "system-reboot",
            "system-shutdown",
        ):
            self.assertIn(f'iconName: "{name}"', qml)

    def test_render_matrix_covers_required_sizes_and_states(self) -> None:
        matrix = CONTRACT["renderMatrix"]
        self.assertEqual(matrix["logicalSizes"], [16, 22, 24, 32, 48])
        self.assertEqual(matrix["modes"], ["normal", "selected"])
        cmake = (ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
        self.assertIn("icon-theme-resolution", cmake)
        self.assertIn("noxforge_icon_resolution_probe", cmake)

    def test_icon_evidence_is_current(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/check_v7_icons.py", "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
