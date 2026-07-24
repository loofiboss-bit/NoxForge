from __future__ import annotations

import configparser
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_URL = "https://github.com/loofiboss-bit/NoxForge"


class PhaseNineIntegrationTests(unittest.TestCase):
    def test_all_public_metadata_matches_version(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(version, "3.0.0")
        self.assertEqual(json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))["version"], version)
        for path in (
            ROOT / "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop/metadata.json",
            ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/metadata.json",
            ROOT / "kwin/tabbox/io.github.loofiboss.noxforge.desktop/metadata.json",
            ROOT / "wallpapers/NoxForge/metadata.json",
        ):
            plugin = json.loads(path.read_text(encoding="utf-8"))["KPlugin"]
            self.assertEqual(plugin["Version"], version)
            if "Website" in plugin:
                self.assertEqual(plugin["Website"], REPOSITORY_URL)

        parser = configparser.ConfigParser(interpolation=None)
        parser.read(
            ROOT / "aurorae/io.github.loofiboss.noxforge.desktop/metadata.desktop",
            encoding="utf-8",
        )
        self.assertEqual(parser["Desktop Entry"]["X-KDE-PluginInfo-Version"], version)
        self.assertEqual(parser["Desktop Entry"]["X-KDE-PluginInfo-Website"], REPOSITORY_URL)
        parser.read(ROOT / "sddm/NoxForge/metadata.desktop", encoding="utf-8")
        self.assertEqual(parser["SddmGreeterTheme"]["Version"], version)
        self.assertEqual(parser["SddmGreeterTheme"]["Website"], REPOSITORY_URL)

    def test_sddm_has_required_original_flows(self) -> None:
        root = ROOT / "sddm/NoxForge"
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(root / "metadata.desktop", encoding="utf-8")
        self.assertEqual(parser["SddmGreeterTheme"]["QtVersion"], "6")
        qml = (root / "Main.qml").read_text(encoding="utf-8")
        for value in ("userModel", "sessionModel", "keyboard.layouts", "sddm.login", "sddm.powerOff"):
            self.assertIn(value, qml)
        for value in ('qsTr("Username")', 'qsTr("Password")', "Accessible.name", "activeFocusOnTab"):
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
