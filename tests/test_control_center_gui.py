#!/usr/bin/env python3
"""Headless GUI tests for NoxForge Control Center and Accessibility Tab."""

from __future__ import annotations

import os
from pathlib import Path
import unittest

# Ensure headless offscreen platform for Qt
os.environ["QT_QPA_PLATFORM"] = "offscreen"

ROOT = Path(__file__).resolve().parents[1]
import sys
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import importlib.util

HAVE_PYSIDE6 = bool(importlib.util.find_spec("PySide6"))
if HAVE_PYSIDE6:
    from PySide6 import QtWidgets  # noqa: E402
    from tools import control_center, opacity_gui  # noqa: E402


@unittest.skipUnless(HAVE_PYSIDE6, "PySide6 not installed in environment")
class TestControlCenterGUI(unittest.TestCase):
    """Test suite for the unified tabbed Control Center GUI."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(["test"])

    def test_window_tabs_instantiation(self) -> None:
        """ControlCenterWindow must instantiate 5 functional tabs."""
        win = control_center.ControlCenterWindow()
        self.assertEqual(win.tabs.count(), 5)
        self.assertIn("Profile", win.tabs.tabText(0))
        self.assertIn("Transparency", win.tabs.tabText(1))
        self.assertIn("Accessibility", win.tabs.tabText(2))
        self.assertIn("Health", win.tabs.tabText(3))
        self.assertIn("Ecosystem", win.tabs.tabText(4))
        win.close()

    def test_initial_tab_navigation(self) -> None:
        """Initial tab selection must activate the requested tab index."""
        win_profile = control_center.ControlCenterWindow(initial_tab="profile")
        self.assertEqual(win_profile.tabs.currentIndex(), 0)
        win_profile.close()

        win_opacity = control_center.ControlCenterWindow(initial_tab="opacity")
        self.assertEqual(win_opacity.tabs.currentIndex(), 1)
        win_opacity.close()

        win_a11y = control_center.ControlCenterWindow(initial_tab="a11y")
        self.assertEqual(win_a11y.tabs.currentIndex(), 2)
        win_a11y.close()

        win_health = control_center.ControlCenterWindow(initial_tab="health")
        self.assertEqual(win_health.tabs.currentIndex(), 3)
        win_health.close()

        win_eco = control_center.ControlCenterWindow(initial_tab="ecosystem")
        self.assertEqual(win_eco.tabs.currentIndex(), 4)
        win_eco.close()

    def test_ecosystem_tab_instantiation(self) -> None:
        """EcosystemTab instantiates with application table and action buttons."""
        tab = control_center.EcosystemTab()
        self.assertGreaterEqual(tab.table.rowCount(), 5)
        self.assertTrue(tab.btn_apply_all.isEnabled())
        self.assertTrue(tab.btn_refresh.isEnabled())

    def test_accessibility_tab_contrast_readout(self) -> None:
        """AccessibilityTab contrast readout validates high-contrast vs low-contrast hex."""
        tab = control_center.AccessibilityTab()

        # Valid high-contrast Electric Lime
        tab.update_contrast_readout("#A3FF47")
        self.assertIn("PASS", tab.contrast_label.text())
        self.assertTrue(tab.btn_apply_custom.isEnabled())

        # Valid Molten Amber
        tab.update_contrast_readout("#FBBF24")
        self.assertIn("PASS", tab.contrast_label.text())
        self.assertTrue(tab.btn_apply_custom.isEnabled())

        # Low-contrast dark blue (#1A2B3C)
        tab.update_contrast_readout("#1A2B3C")
        self.assertIn("FAIL", tab.contrast_label.text())
        self.assertFalse(tab.btn_apply_custom.isEnabled())

        # Invalid format
        tab.update_contrast_readout("invalid")
        self.assertFalse(tab.btn_apply_custom.isEnabled())

    def test_accessibility_tab_simulations(self) -> None:
        """AccessibilityTab simulations trigger cleanly without exceptions."""
        tab = control_center.AccessibilityTab()
        tab.play_edge_flash()
        self.assertIn("border: 2px solid #FF5555", tab.sim_input.styleSheet())

        tab.play_kinetic_shake()
        self.assertIn("border: 2px solid #FF5555", tab.sim_input.styleSheet())

    def test_opacity_gui_shim(self) -> None:
        """opacity_gui.py provides compatibility main function delegating to opacity tab."""
        self.assertTrue(callable(opacity_gui.main))
        self.assertTrue(callable(opacity_gui.launch_gui))


if __name__ == "__main__":
    unittest.main()
