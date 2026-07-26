from __future__ import annotations

import configparser
import gzip
import hashlib
import json
import struct
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME_ID = "io.github.loofiboss.noxforge.desktop"
CONTRACT = json.loads((ROOT / "design/session-surface-contract.json").read_text(encoding="utf-8"))
EVIDENCE = json.loads((ROOT / "docs/evidence/v5/session-surfaces.json").read_text(encoding="utf-8"))


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"not a PNG: {path}")
    return struct.unpack(">II", data[16:24])


class V5PhaseFiveTests(unittest.TestCase):
    def test_session_contracts_remain_complete_without_private_lock_screen(self) -> None:
        sddm = (ROOT / "sddm/NoxForge/Main.qml").read_text(encoding="utf-8")
        for value in (
            "sddm.login",
            "sessionModel",
            "keyboard.layouts",
            "sddm.suspend",
            "sddm.reboot",
            "sddm.powerOff",
            "onLoginFailed",
            "onLoginSucceeded",
        ):
            self.assertIn(value, sddm)
        logout = (
            ROOT / f"look-and-feel/{THEME_ID}/contents/logout/Logout.qml"
        ).read_text(encoding="utf-8")
        for signal in (
            "logoutRequested",
            "haltRequested",
            "haltUpdateRequested",
            "suspendRequested",
            "rebootRequested",
            "rebootRequested2",
            "rebootUpdateRequested",
            "cancelRequested",
            "lockScreenRequested",
            "cancelSoftwareUpdateRequested",
        ):
            self.assertIn(f"signal {signal}", logout)
        self.assertFalse(CONTRACT["privateLockScreen"])
        self.assertFalse(
            any(path.name.lower().startswith("lock") for path in (ROOT / "look-and-feel").rglob("*.qml"))
        )

    def test_long_empty_localized_rtl_keyboard_and_reduced_motion_contracts(self) -> None:
        sddm = (ROOT / "sddm/NoxForge/Main.qml").read_text(encoding="utf-8")
        self.assertIn("Layout.minimumHeight: 40", sddm)
        self.assertIn("Layout.maximumHeight: 40", sddm)
        self.assertIn("maximumLineCount: 2", sddm)
        self.assertIn("KeyNavigation.tab", sddm)
        self.assertIn("KeyNavigation.backtab", sddm)
        self.assertIn("id: sessionChoices", sddm)
        self.assertIn("sessionChoices.itemAt(index + 1)", sddm)
        self.assertIn("sessionChoices.itemAt(index - 1)", sddm)
        self.assertIn("LayoutMirroring.enabled", sddm)

        logout = (
            ROOT / f"look-and-feel/{THEME_ID}/contents/logout/Logout.qml"
        ).read_text(encoding="utf-8")
        self.assertIn("LayoutMirroring.enabled", logout)
        self.assertIn("KeyNavigation.tab", logout)

        splash = (
            ROOT / f"look-and-feel/{THEME_ID}/contents/splash/Splash.qml"
        ).read_text(encoding="utf-8")
        switcher = (
            ROOT / f"kwin/tabbox/{THEME_ID}/contents/ui/Switcher.qml"
        ).read_text(encoding="utf-8")
        for qml in (splash, switcher):
            self.assertIn("Kirigami.Units.longDuration <= 0", qml)
            self.assertIn("tokens.reducedMotionDuration", qml)
        for value in ('qsTr("No windows available")', "Text.ElideRight", "LayoutMirroring.enabled"):
            self.assertIn(value, switcher)

        covered = {
            item
            for composition in CONTRACT["compositions"]
            for item in composition["covers"]
        }
        self.assertTrue(set(CONTRACT["requiredCoverage"]).issubset(covered))

    def test_authentic_qml_matrix_covers_all_four_compositions(self) -> None:
        self.assertTrue(EVIDENCE["authenticQml"])
        self.assertEqual(
            EVIDENCE["themeContext"],
            "isolated NoxForge Plasma and icon context",
        )
        self.assertFalse(EVIDENCE["liveSession"])
        self.assertEqual(EVIDENCE["reviewStatus"], "reviewed")
        expected = {
            (surface, composition["width"], composition["height"], composition["scenario"])
            for surface in CONTRACT["surfaces"]
            for composition in CONTRACT["compositions"]
        }
        observed = {
            (item["surface"], item["width"], item["height"], item["scenario"])
            for item in EVIDENCE["captures"]
        }
        self.assertEqual(observed, expected)
        hashes = set()
        for item in EVIDENCE["captures"]:
            path = ROOT / "docs/evidence/v5" / item["file"]
            self.assertEqual(png_dimensions(path), (item["width"], item["height"]))
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest, item["sha256"])
            hashes.add(digest)
        self.assertEqual(len(hashes), len(EVIDENCE["captures"]))

    def test_aurorae_states_and_canonical_compression_are_structurally_complete(self) -> None:
        theme = ROOT / f"aurorae/{THEME_ID}"
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(theme / f"{THEME_ID}rc", encoding="utf-8")
        self.assertEqual(parser["General"]["Animation"], "140")
        self.assertEqual(parser["General"]["RightButtons"], "IAX")

        decoration = ET.parse(theme / "decoration.svg")
        elements = {node.get("id"): node for node in decoration.iter() if node.get("id")}
        positions = {
            "topleft",
            "top",
            "topright",
            "left",
            "center",
            "right",
            "bottomleft",
            "bottom",
            "bottomright",
        }
        for prefix in ("decoration", "decoration-inactive"):
            self.assertTrue({f"{prefix}-{position}" for position in positions}.issubset(elements))
        active_highlights = [
            node
            for node in elements["decoration-top"].iter()
            if node.get("class") == "ColorScheme-Highlight"
        ]
        inactive_highlights = [
            node
            for node in elements["decoration-inactive-top"].iter()
            if node.get("class") == "ColorScheme-Highlight"
        ]
        self.assertEqual(len(active_highlights), 1)
        self.assertEqual(inactive_highlights, [])

        states = {
            "active",
            "inactive",
            "hover",
            "hover-inactive",
            "pressed",
            "pressed-inactive",
            "deactivated",
            "deactivated-inactive",
        }
        for name in ("close", "minimize", "maximize", "restore"):
            source = theme / f"{name}.svg"
            ids = {node.get("id") for node in ET.parse(source).iter() if node.get("id")}
            self.assertTrue({f"{state}-center" for state in states}.issubset(ids))
            self.assertEqual(gzip.decompress((theme / f"{name}.svgz").read_bytes()), source.read_bytes())
        source = theme / "decoration.svg"
        self.assertEqual(gzip.decompress((theme / "decoration.svgz").read_bytes()), source.read_bytes())

    def test_phase_plan_records_completed_gate(self) -> None:
        plan = (ROOT / "docs/NOXFORGE_V5_PLAN.md").read_text(encoding="utf-8")
        phase = plan.split("## Phase 5", 1)[1].split("## Phase 6", 1)[0]
        self.assertIn("**Outcome (2026-07-26):**", phase)


if __name__ == "__main__":
    unittest.main()
