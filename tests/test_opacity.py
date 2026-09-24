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

try:
    import PySide6
    HAVE_PYSIDE6 = True
except ImportError:
    HAVE_PYSIDE6 = False


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

    @unittest.skipUnless(HAVE_PYSIDE6, "PySide6 not installed in environment")
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

        # Test blur toggle
        win.chk_simulate_blur.setChecked(False)
        self.assertFalse(preview.simulate_blur)
        preview.render(pix)
        win.chk_simulate_blur.setChecked(True)
        self.assertTrue(preview.simulate_blur)
        preview.render(pix)

        # Test closeEvent
        close_event = QtGui.QCloseEvent()
        win.closeEvent(close_event)
        self.assertTrue(close_event.isAccepted())

    def test_svg_opacity_injection_when_missing(self) -> None:
        """Verify fill-opacity is cleanly injected into elements that lack it."""
        sample_svg = (
            '<svg xmlns="http://www.w3.org/2000/svg">\n'
            '  <rect class="ColorScheme-Background" fill="currentColor" width="10" height="10"/>\n'
            '  <path class="NoxForge-Overlay" d="M0 0h10v10H0z" fill="#000000"/>\n'
            '</svg>'
        )
        self.assertIsNone(noxforge_opacity.extract_svg_opacity(sample_svg))
        modified, count = noxforge_opacity.replace_svg_opacity(sample_svg, 0.78)
        self.assertEqual(count, 2)
        self.assertIn('fill-opacity="0.78"', modified)
        self.assertEqual(noxforge_opacity.extract_svg_opacity(modified), 0.78)

    def test_aurorae_opacity_injection_when_missing(self) -> None:
        """Verify fill-opacity is injected into Aurorae frames lacking fill-opacity."""
        sample_svg = (
            '<svg xmlns="http://www.w3.org/2000/svg">\n'
            '  <rect id="active-bg" class="ColorScheme-Raised" fill="currentColor"/>\n'
            '  <rect id="inactive-bg" class="ColorScheme-Sunken" fill="currentColor"/>\n'
            '</svg>'
        )
        modified, count = noxforge_opacity.replace_aurorae_opacity(sample_svg, 0.85, 0.75)
        self.assertEqual(count, 2)
        act, inact = noxforge_opacity.extract_aurorae_opacity(modified)
        self.assertEqual(act, 0.85)
    def test_extract_svg_opacity_inline_style_precedence(self) -> None:
        """Verify inline style fill-opacity takes precedence over presentation attribute."""
        sample_svg = (
            '<svg xmlns="http://www.w3.org/2000/svg">\n'
            '  <rect class="ColorScheme-Background" fill-opacity="1.0" style="fill-opacity:0.65" width="10" height="10"/>\n'
            '</svg>'
        )
        self.assertEqual(noxforge_opacity.extract_svg_opacity(sample_svg), 0.65)

    def test_opacity_percentage_and_exponent_handling(self) -> None:
        """Verify percentages and exponents are parsed cleanly and replaced in full."""
        pct_svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect class="ColorScheme-Background" style="fill-opacity:50%"/></svg>'
        self.assertAlmostEqual(noxforge_opacity.extract_svg_opacity(pct_svg), 0.5)
        replaced, count = noxforge_opacity.replace_svg_opacity(pct_svg, 0.78)
        self.assertEqual(count, 1)
        self.assertIn('style="fill-opacity:0.78"', replaced)
        self.assertNotIn('%', replaced)

        exp_svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect class="ColorScheme-Background" fill-opacity="1e-1"/></svg>'
        self.assertAlmostEqual(noxforge_opacity.extract_svg_opacity(exp_svg), 0.1)
        replaced_exp, count = noxforge_opacity.replace_svg_opacity(exp_svg, 0.85)
        self.assertEqual(count, 1)
        self.assertIn('fill-opacity="0.85"', replaced_exp)
        self.assertNotIn('1e-1', replaced_exp)

    def test_detect_wallpaper_url_decoding(self) -> None:
        """Verify detect_active_plasma_wallpaper handles XDG_CONFIG_HOME and percent-encoded URLs."""
        if not HAVE_PYSIDE6:
            self.skipTest("PySide6 not available")
        from tools import opacity_gui
        cfg_dir = self.temp_dir / "config"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        wall_dir = self.temp_dir / "Wallpapers Folder"
        wall_dir.mkdir(parents=True, exist_ok=True)
        wall_file = wall_dir / "Custom Wallpaper.png"
        wall_file.write_bytes(b"dummy")

        appletsrc = cfg_dir / "plasma-org.kde.plasma.desktop-appletsrc"
        appletsrc.write_text(f"[Containments][1][Applets][2][Configuration][Wallpaper]\nImage=file://{wall_dir.as_posix()}/Custom%20Wallpaper.png\n", encoding="utf-8")

        old_xdg = os.environ.get("XDG_CONFIG_HOME")
        try:
            os.environ["XDG_CONFIG_HOME"] = str(cfg_dir)
            detected = opacity_gui.detect_active_plasma_wallpaper()
            self.assertIsNotNone(detected)
            self.assertEqual(detected, wall_file)
        finally:
            if old_xdg is not None:
                os.environ["XDG_CONFIG_HOME"] = old_xdg
            else:
                os.environ.pop("XDG_CONFIG_HOME", None)


if __name__ == "__main__":
    unittest.main()
