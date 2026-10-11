#!/usr/bin/env python3
"""Unit tests for NoxForge v16 accessibility, reduced-motion, and custom accent contrast."""

from __future__ import annotations

import importlib.machinery
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

# Import noxforge-ctl dynamically
CTL_PATH = ROOT / "tools/noxforge-ctl"
loader = importlib.machinery.SourceFileLoader("noxforge_ctl", str(CTL_PATH))
ctl = importlib.util.module_from_spec(importlib.util.spec_from_loader("noxforge_ctl", loader))
loader.exec_module(ctl)


class TestV16Accessibility(unittest.TestCase):
    """Test suite for Phase 5 reduced-motion and WCAG AA custom accent contrast."""

    def test_custom_accent_wcag_contrast_pass(self) -> None:
        """High-contrast colors must pass WCAG AA 4.5:1 against Graphite and Obsidian."""
        # Lime default (#A3FF47)
        cg, co = ctl.validate_custom_accent_contrast("#A3FF47")
        self.assertGreaterEqual(cg, 4.5)
        self.assertGreaterEqual(co, 4.5)

        # Cyan (#22D3EE)
        cg, co = ctl.validate_custom_accent_contrast("#22D3EE")
        self.assertGreaterEqual(cg, 4.5)
        self.assertGreaterEqual(co, 4.5)

        # Amber (#FBBF24)
        cg, co = ctl.validate_custom_accent_contrast("#FBBF24")
        self.assertGreaterEqual(cg, 4.5)
        self.assertGreaterEqual(co, 4.5)

        # White (#FFFFFF)
        cg, co = ctl.validate_custom_accent_contrast("#FFFFFF")
        self.assertGreaterEqual(cg, 4.5)
        self.assertGreaterEqual(co, 4.5)

    def test_custom_accent_wcag_contrast_fail(self) -> None:
        """Low-contrast dark colors must fail WCAG AA 4.5:1 requirement."""
        low_contrast_colors = [
            "#141E25",  # identical to graphite canvas
            "#000000",  # identical to obsidian canvas
            "#1A2B3C",  # dark navy (~1.17:1)
            "#2B2B2B",  # dark gray
            "#334155",  # slate
        ]
        for color in low_contrast_colors:
            with self.subTest(color=color):
                with self.assertRaises(ValueError) as ctx:
                    ctl.validate_custom_accent_contrast(color)
                self.assertIn("fails WCAG AA 4.5:1 contrast requirement", str(ctx.exception))

    def test_custom_accent_invalid_format(self) -> None:
        """Invalid hex formats must raise ValueError."""
        invalid_inputs = ["lime", "red", "#FFF", "#GGGGGG", "123456", "#12345"]
        for item in invalid_inputs:
            with self.subTest(item=item):
                with self.assertRaises(ValueError) as ctx:
                    ctl.validate_custom_accent_contrast(item)
                self.assertIn("Invalid hex color format", str(ctx.exception))

    def test_noxforge_ctl_set_accent_dry_run(self) -> None:
        """noxforge-ctl set_accent in dry-run mode returns contrast metrics."""
        result = ctl.set_accent("custom", custom_hex="#A3FF47", dry_run=True)
        self.assertEqual(result["status"], "dry-run")
        self.assertEqual(result["accent"], "custom")
        self.assertEqual(result["hex"], "#A3FF47")
        self.assertIn("contrastGraphite", result)
        self.assertIn("contrastObsidian", result)
        self.assertGreaterEqual(result["contrastGraphite"], 4.5)
        self.assertGreaterEqual(result["contrastObsidian"], 4.5)

        # Direct hex input
        result_hex = ctl.set_accent("#FBBF24", dry_run=True)
        self.assertEqual(result_hex["status"], "dry-run")
        self.assertEqual(result_hex["accent"], "custom")
        self.assertEqual(result_hex["hex"], "#FBBF24")

    def test_motion_policy_contains_long_duration_suppression(self) -> None:
        """MotionPolicy.qml must check Kirigami.Units.longDuration <= 0."""
        policy_files = [
            ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/splash/MotionPolicy.qml",
            ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/logout/MotionPolicy.qml",
            ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/lockscreen/MotionPolicy.qml",
            ROOT / "kwin/tabbox/io.github.loofiboss.noxforge.desktop/contents/ui/MotionPolicy.qml",
            ROOT / "look-and-feel/io.github.loofiboss.noxforge.obsidian.desktop/contents/splash/MotionPolicy.qml",
            ROOT / "look-and-feel/io.github.loofiboss.noxforge.obsidian.desktop/contents/logout/MotionPolicy.qml",
            ROOT / "look-and-feel/io.github.loofiboss.noxforge.obsidian.desktop/contents/lockscreen/MotionPolicy.qml",
            ROOT / "kwin/tabbox/io.github.loofiboss.noxforge.obsidian.desktop/contents/ui/MotionPolicy.qml",
        ]
        for path in policy_files:
            with self.subTest(file=path.name):
                content = path.read_text(encoding="utf-8")
                self.assertIn("Kirigami.Units.longDuration <= 0", content)
                self.assertIn("readonly property bool reducedMotion", content)

    def test_shared_lockscreen_reduced_motion_edge_flash(self) -> None:
        """LockScreen.qml must implement 220ms edge-flash and Accessible roles."""
        lockscreen = (ROOT / "qml/shared/lockscreen/LockScreen.qml").read_text(encoding="utf-8")
        self.assertIn("property bool edgeFlash: false", lockscreen)
        self.assertIn("interval: 220", lockscreen)
        self.assertIn("root.edgeFlash = true", lockscreen)
        self.assertIn("Accessible.role: Accessible.EditableText", lockscreen)
        self.assertIn("Accessible.name: qsTr(\"Password\")", lockscreen)
        self.assertIn("Accessible.role: root.statusDanger ? Accessible.AlertMessage : Accessible.StaticText", lockscreen)

    def test_shared_sddm_reduced_motion_edge_flash(self) -> None:
        """SDDM Main.qml must implement edge-flash, sddmReduced check, and Accessible roles."""
        sddm = (ROOT / "qml/shared/sddm/Main.qml").read_text(encoding="utf-8")
        self.assertIn("property bool edgeFlash: false", sddm)
        self.assertIn("interval: 220", sddm)
        self.assertIn("config.reducedMotion", sddm)
        self.assertIn("root.edgeFlash = true", sddm)
        self.assertIn("Accessible.role: root.statusDanger ? Accessible.AlertMessage : Accessible.StaticText", sddm)

    def test_sddm_theme_conf_reduced_motion_option(self) -> None:
        """SDDM theme.conf files must declare reducedMotion=false."""
        for path in (
            ROOT / "sddm/NoxForge/theme.conf",
            ROOT / "sddm/NoxForgeObsidian/theme.conf",
        ):
            with self.subTest(theme=path.parent.name):
                content = path.read_text(encoding="utf-8")
                self.assertIn("reducedMotion=false", content)


if __name__ == "__main__":
    unittest.main()
