#!/usr/bin/env python3
"""Tests for noxforge-opacity transparency configurator."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import shutil
import tempfile
from pathlib import Path
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
OPACITY_TOOL = ROOT / "tools/noxforge-opacity"

import sys

# Dynamic load of noxforge-opacity
loader = importlib.machinery.SourceFileLoader("noxforge_opacity", str(OPACITY_TOOL))
spec = importlib.util.spec_from_loader("noxforge_opacity", loader)
assert spec and spec.loader
noxforge_opacity = importlib.util.module_from_spec(spec)
sys.modules["noxforge_opacity"] = noxforge_opacity
spec.loader.exec_module(noxforge_opacity)


class TestNoxForgeOpacity(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="noxforge_opacity_test_"))
        self.theme_dir = self.temp_dir / "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop"
        self.aurorae_dir = self.temp_dir / "aurorae/io.github.loofiboss.noxforge.desktop"

        # Copy sample theme and aurorae assets
        src_theme = ROOT / "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop"
        src_aurorae = ROOT / "aurorae/io.github.loofiboss.noxforge.desktop"

        if src_theme.is_dir():
            shutil.copytree(src_theme, self.theme_dir)
        if src_aurorae.is_dir():
            shutil.copytree(src_aurorae, self.aurorae_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_presets_defined(self) -> None:
        self.assertIn("solid", noxforge_opacity.PRESETS)
        self.assertIn("original", noxforge_opacity.PRESETS)
        self.assertIn("frost", noxforge_opacity.PRESETS)
        self.assertIn("glass", noxforge_opacity.PRESETS)
        self.assertIn("ultra", noxforge_opacity.PRESETS)

        frost = noxforge_opacity.OpacityRecipe.from_preset("frost")
        self.assertEqual(frost.panel, 0.78)
        self.assertEqual(frost.dialog, 0.78)
        self.assertEqual(frost.widget, 0.76)
        self.assertEqual(frost.tooltip, 0.88)
        self.assertEqual(frost.aurorae_active, 0.85)
        self.assertEqual(frost.aurorae_inactive, 0.75)

    def test_custom_recipe_from_base(self) -> None:
        recipe = noxforge_opacity.OpacityRecipe.from_base(0.70)
        self.assertEqual(recipe.panel, 0.70)
        self.assertEqual(recipe.dialog, 0.70)
        self.assertEqual(recipe.widget, 0.68)
        self.assertEqual(recipe.tooltip, 0.80)
        self.assertEqual(recipe.aurorae_active, 0.77)
        self.assertEqual(recipe.aurorae_inactive, 0.65)

    def test_extract_and_replace_svg_opacity(self) -> None:
        panel_svg = self.theme_dir / "translucent/widgets/panel-background.svg"
        self.assertTrue(panel_svg.is_file())
        initial_content = panel_svg.read_text(encoding="utf-8")

        initial_op = noxforge_opacity.extract_svg_opacity(initial_content)
        self.assertEqual(initial_op, 0.94)

        # Replace with 0.78
        new_content, count = noxforge_opacity.replace_svg_opacity(initial_content, 0.78)
        self.assertEqual(count, 9)
        updated_op = noxforge_opacity.extract_svg_opacity(new_content)
        self.assertEqual(updated_op, 0.78)
        # Verify edge highlight stroke opacity remains untouched
        self.assertIn('stroke-opacity="0.72"', new_content)
        # Verify hint remains untouched
        self.assertIn('fill-opacity="0"', new_content)

    def test_extract_and_replace_aurorae_opacity(self) -> None:
        dec_svg = self.aurorae_dir / "decoration.svg"
        self.assertTrue(dec_svg.is_file())
        initial_content = dec_svg.read_text(encoding="utf-8")

        act_op, inact_op = noxforge_opacity.extract_aurorae_opacity(initial_content)
        self.assertEqual(act_op, 1.0)
        self.assertEqual(inact_op, 0.9)

        # Replace with 0.85 and 0.75
        new_content, count = noxforge_opacity.replace_aurorae_opacity(initial_content, 0.85, 0.75)
        self.assertEqual(count, 18)  # 9 active + 9 inactive
        act_updated, inact_updated = noxforge_opacity.extract_aurorae_opacity(new_content)
        self.assertEqual(act_updated, 0.85)
        self.assertEqual(inact_updated, 0.75)

    def test_apply_opacity_dry_run(self) -> None:
        recipe = noxforge_opacity.OpacityRecipe.from_preset("frost")
        panel_svg = self.theme_dir / "translucent/widgets/panel-background.svg"
        orig_text = panel_svg.read_text(encoding="utf-8")

        modified = noxforge_opacity.apply_opacity(
            recipe=recipe,
            custom_theme_dir=self.theme_dir,
            dry_run=True,
        )
        self.assertEqual(len(modified), 4)
        # Ensure file was not modified
        self.assertEqual(panel_svg.read_text(encoding="utf-8"), orig_text)

    def test_apply_opacity_actual_write(self) -> None:
        recipe = noxforge_opacity.OpacityRecipe.from_preset("glass")
        panel_svg = self.theme_dir / "translucent/widgets/panel-background.svg"
        dialog_svg = self.theme_dir / "translucent/dialogs/background.svg"

        modified = noxforge_opacity.apply_opacity(
            recipe=recipe,
            custom_theme_dir=self.theme_dir,
            custom_aurorae_dir=self.aurorae_dir,
            include_aurorae=True,
            include_root=True,
            dry_run=False,
        )
        self.assertEqual(len(modified), 7)  # 4 translucent + 2 root + 1 aurorae

        # Read back
        self.assertEqual(noxforge_opacity.extract_svg_opacity(panel_svg.read_text(encoding="utf-8")), 0.60)
        self.assertEqual(noxforge_opacity.extract_svg_opacity(dialog_svg.read_text(encoding="utf-8")), 0.62)
        dec_svg = self.aurorae_dir / "decoration.svg"
        act, inact = noxforge_opacity.extract_aurorae_opacity(dec_svg.read_text(encoding="utf-8"))
        self.assertEqual(act, 0.75)
        self.assertEqual(inact, 0.65)

    def test_cli_status(self) -> None:
        status = noxforge_opacity.get_status(custom_theme_dir=self.theme_dir)
        self.assertIn("graphite", status["themes"])
        files = status["themes"]["graphite"]["files"]
        self.assertEqual(files["panel"]["percent"], "94%")

    def test_cli_main_preset_dry_run_json(self) -> None:
        code = noxforge_opacity.main([
            "--theme-dir", str(self.theme_dir),
            "--preset", "frost",
            "--dry-run",
            "--json",
            "--no-reload",
        ])
        self.assertEqual(code, 0)

    def test_gui_components_and_preview(self) -> None:
        from PySide6 import QtCore, QtGui, QtWidgets
        import importlib.util

        gui_path = ROOT / "tools/opacity_gui.py"
        spec = importlib.util.spec_from_file_location("opacity_gui", gui_path)
        assert spec and spec.loader
        gui_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gui_mod)

        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

        # Create window offscreen
        win = gui_mod.OpacityConfiguratorWindow()
        self.assertIsNotNone(win)

        # Check preset click
        win._on_preset_clicked("glass")
        self.assertEqual(win.slider_panel.value(), 60)
        self.assertEqual(win.slider_dialog.value(), 62)
        self.assertEqual(win.slider_widget.value(), 60)
        self.assertEqual(win.slider_tooltip.value(), 80)

        # Render preview offscreen to verify paintEvent works without errors
        preview = win.preview_canvas
        preview.resize(400, 500)
        pix = QtGui.QPixmap(400, 500)
        preview.render(pix)
        self.assertFalse(pix.isNull())
        self.assertEqual(pix.width(), 400)
        self.assertEqual(pix.height(), 500)


if __name__ == "__main__":
    unittest.main()
