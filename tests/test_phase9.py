from __future__ import annotations

import configparser
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PhaseNineIntegrationTests(unittest.TestCase):
    def test_all_public_metadata_is_v1(self) -> None:
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), "1.0.0")
        self.assertEqual(json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))["version"], "1.0.0")
        for path in (
            ROOT / "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop/metadata.json",
            ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/metadata.json",
            ROOT / "kwin/tabbox/io.github.loofiboss.noxforge.desktop/metadata.json",
            ROOT / "wallpapers/NoxForge/metadata.json",
        ):
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["KPlugin"]["Version"], "1.0.0")

        parser = configparser.ConfigParser(interpolation=None)
        parser.read(
            ROOT / "aurorae/io.github.loofiboss.noxforge.desktop/metadata.desktop",
            encoding="utf-8",
        )
        self.assertEqual(parser["Desktop Entry"]["X-KDE-PluginInfo-Version"], "1.0.0")
        parser.read(ROOT / "sddm/NoxForge/metadata.desktop", encoding="utf-8")
        self.assertEqual(parser["SddmGreeterTheme"]["Version"], "1.0.0")

    def test_sddm_has_required_original_flows(self) -> None:
        root = ROOT / "sddm/NoxForge"
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(root / "metadata.desktop", encoding="utf-8")
        self.assertEqual(parser["SddmGreeterTheme"]["QtVersion"], "6")
        qml = (root / "Main.qml").read_text(encoding="utf-8")
        for value in ("userModel", "sessionModel", "keyboard.layouts", "sddm.login", "sddm.powerOff"):
            self.assertIn(value, qml)
        self.assertNotIn("Breeze", qml)

    def test_installers_never_apply_or_reconfigure(self) -> None:
        forbidden = ("plasma-apply-", "kwriteconfig", "qdbus", "systemctl", "plasmashell --replace")
        for name in ("install.sh", "uninstall.sh", "install-system.sh", "uninstall-system.sh"):
            text = (ROOT / "scripts" / name).read_text(encoding="utf-8")
            for command in forbidden:
                self.assertNotIn(command, text)


if __name__ == "__main__":
    unittest.main()
