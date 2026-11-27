# SPDX-License-Identifier: MIT
"""Automated contracts and regression tests for NoxForge v21.0.0 (Duotone Visual Craft, Aurorae v2, Live Control Core & Ecosystem v4)."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import re
import runpy
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

HAVE_PYSIDE6 = bool(importlib.util.find_spec("PySide6"))

from tests.test_doctor import DOCTOR_FUNCTIONS as doctor_fn, stage_complete  # noqa: E402
from tools import noxforge_core  # noqa: E402


class NoxForgeV21ContractsTests(unittest.TestCase):
    def test_v21_plan_manifest_and_tokens_schema_17(self) -> None:
        plan = ROOT / "docs/NOXFORGE_V21_PLAN.md"
        self.assertTrue(plan.is_file(), "docs/NOXFORGE_V21_PLAN.md is missing")
        plan_text = plan.read_text(encoding="utf-8")
        self.assertIn("NoxForge 21.0.0", plan_text)
        self.assertIn("Duotone", plan_text)
        self.assertIn("Aurorae v2", plan_text)
        self.assertIn("Ecosystem v4", plan_text)

        impl_plan = (ROOT / "docs/IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
        self.assertIn("NOXFORGE_V21_PLAN.md", impl_plan)

        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertRegex(version, r"^21\.0\.\d+$")
        self.assertEqual(noxforge_core.get_app_version(), version)

        manifest = json.loads((ROOT / "distribution/release-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["release"]["version"], version)
        self.assertEqual(manifest["release"]["activePlan"], "docs/NOXFORGE_V21_PLAN.md")
        self.assertEqual(manifest["evidence"]["activeRoot"], "docs/evidence/v21")
        self.assertEqual(manifest["source"]["archiveRoot"], f"NoxForge-{version}")
        self.assertIn("docs/evidence/v21", manifest["source"]["include"])

        tokens = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))
        self.assertEqual(tokens["schemaVersion"], 17)
        self.assertEqual(tokens["version"], version)

        # 6 WCAG-verified accents
        expected_accents = {
            "lime": "#A3FF47",
            "cyan": "#22D3EE",
            "violet": "#A78BFA",
            "amber": "#FBBF24",
            "crimson": "#FF8FA3",
            "ice": "#93C5FD",
        }
        for key, hex_color in expected_accents.items():
            self.assertIn(key, tokens["accents"])
            self.assertEqual(tokens["accents"][key]["accent"], hex_color)
            ratio_g, ratio_o = noxforge_core.validate_custom_accent_contrast(hex_color)
            self.assertGreaterEqual(ratio_g, 4.5, f"{key} contrast on Graphite below WCAG AA")
            self.assertGreaterEqual(ratio_o, 4.5, f"{key} contrast on Obsidian below WCAG AA")

        self.assertEqual(tokens["duotoneIconography"]["opticalSizes"], [16, 22, 32, 48, 64])
        self.assertTrue(tokens["auroraeV2"]["shadowEnabled"])
        self.assertTrue(tokens["auroraeV2"]["maximizedFlat"])
        self.assertTrue(tokens["auroraeV2"]["dynamicAccentRail"])
        self.assertEqual(tokens["wallpaperV2"]["colorDepth"], "PNG24")
        self.assertTrue(tokens["wallpaperV2"]["dynamicDayNight"])
        self.assertEqual(
            tokens["ecosystemV4"]["apps"],
            ["bat", "delta", "fzf", "eza", "wofi", "fastfetch"],
        )

    def test_duotone_icons_scalable_cursors_audio_v2_and_png24_wallpapers(self) -> None:
        icons_root = ROOT / "icons/NoxForge"
        coverage = json.loads((icons_root / "coverage.json").read_text(encoding="utf-8"))
        self.assertEqual(coverage["opticalSizes"], [16, 22, 32, 48, 64])
        self.assertGreaterEqual(len(coverage["icons"]), 430)
        self.assertGreaterEqual(coverage["opticalCount"], 890)

        # Category breadth: NoxForge-owned apps only (third-party apps keep upstream icons)
        apps_svgs = sorted(p.name for p in (icons_root / "scalable/apps").glob("*.svg"))
        mime_svgs = list((icons_root / "scalable/mimetypes").glob("*.svg"))
        places_svgs = list((icons_root / "scalable/places").glob("*.svg"))
        self.assertEqual(
            apps_svgs,
            [
                "io.github.loofiboss.noxforge.controlcenter.svg",
                "io.github.loofiboss.noxforge.opacity.svg",
                "noxforge-controlcenter.svg",
                "noxforge-opacity.svg",
            ],
        )
        for forbidden_third_party in (
            "firefox.svg",
            "vlc.svg",
            "steam.svg",
            "discord.svg",
            "gimp.svg",
            "com.bitwarden.desktop.svg",
            "org.telegram.desktop.svg",
            "org.kde.dolphin.svg",
            "code.svg",
            "spotify.svg",
        ):
            for size_dir in ("scalable", "32x32", "48x48", "64x64"):
                self.assertFalse(
                    (icons_root / size_dir / "apps" / forbidden_third_party).exists(),
                    f"Third-party app icon must not be overridden: {size_dir}/apps/{forbidden_third_party}",
                )
        self.assertGreaterEqual(len(mime_svgs), 28)
        self.assertGreaterEqual(len(places_svgs), 24)

        # 6 accent folders
        for accent in ("lime", "cyan", "violet", "amber", "crimson", "ice"):
            folder_svg = icons_root / f"scalable/places/folder-{accent}.svg"
            self.assertTrue(folder_svg.is_file(), f"Missing accent folder: {folder_svg}")

        # Duotone styling on NoxForge apps and places (surface plate + inner bevel + Forge Notch)
        cc_svg = (icons_root / "scalable/apps/io.github.loofiboss.noxforge.controlcenter.svg").read_text(encoding="utf-8")
        self.assertIn("surface-plate", cc_svg)
        self.assertIn("surface-bevel", cc_svg)

        # Cursors: 5-size Xcursor + Plasma 6 scalable Wayland SVGs, zero symlinks
        cursors_root = ROOT / "cursors/NoxForge-Cursors"
        xcursors = list((cursors_root / "cursors").iterdir())
        self.assertGreaterEqual(len(xcursors), 90)
        self.assertFalse(any(p.is_symlink() for p in xcursors))
        scalable_dir = cursors_root / "cursors_scalable"
        self.assertTrue(scalable_dir.is_dir())
        self.assertTrue((scalable_dir / "default/default.svg").is_file())
        self.assertTrue((scalable_dir / "default/metadata.json").is_file())
        scalable_dirs = [p for p in scalable_dir.iterdir() if p.is_dir()]
        scalable_files = [p for p in scalable_dir.rglob("*") if p.is_file()]
        self.assertGreaterEqual(len(scalable_dirs), 90)
        self.assertGreaterEqual(len(scalable_files), 240)
        self.assertFalse(any(p.is_symlink() for p in scalable_dir.rglob("*")))

        # Tactile Forge Audio v2
        sounds_root = ROOT / "sounds/NoxForge"
        wavs = list((sounds_root / "source").glob("*.wav"))
        ogas = list((sounds_root / "stereo").glob("*.oga"))
        self.assertGreaterEqual(len(wavs), 27)
        self.assertGreaterEqual(len(ogas), 32)

        # Wallpapers: PNG24 color type (2), 16:10, 32:9, and Plasma 6 images_dark/
        for rel in (
            "wallpapers/NoxForge/contents/images/2560x1600.png",
            "wallpapers/NoxForge/contents/images/3840x2400.png",
            "wallpapers/NoxForge/contents/images/5120x1440.png",
            "wallpapers/NoxForge/contents/images_dark/2560x1440.png",
            "wallpapers/NoxForge-Obsidian/contents/images/2560x1600.png",
            "wallpapers/NoxForge-Obsidian/contents/images/5120x1440.png",
        ):
            wp = ROOT / rel
            self.assertTrue(wp.is_file(), f"Missing wallpaper: {rel}")
            header = wp.read_bytes()[:29]
            self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
            _, _, depth, color_type = struct.unpack(">IIBB", header[16:26])
            self.assertEqual(depth, 8, f"Expected 8-bit PNG in {rel}")
            self.assertIn(color_type, (2, 6), f"Expected truecolor PNG24/32 (not indexed) in {rel}")

    def test_aurorae_v2_plasma_svgs_and_osd_systemdialog_qml(self) -> None:
        for theme_id in (
            "io.github.loofiboss.noxforge.desktop",
            "io.github.loofiboss.noxforge.obsidian.desktop",
        ):
            aur_dir = ROOT / "aurorae" / theme_id
            rc = (aur_dir / f"{theme_id}rc").read_text(encoding="utf-8")
            self.assertIn("Shadow=true", rc)
            self.assertIn("PaddingTop=8", rc)
            self.assertIn("PaddingBottom=16", rc)
            self.assertIn("PaddingLeft=12", rc)
            self.assertIn("PaddingRight=12", rc)
            self.assertIn("TitleEdgeTopMaximized=0", rc)

            meta_json = aur_dir / "metadata.json"
            self.assertTrue(meta_json.is_file(), f"Missing Aurorae v2 metadata.json: {meta_json}")
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            self.assertEqual(meta["KPlugin"]["Version"], (ROOT / "VERSION").read_text(encoding="utf-8").strip())

            dec_svg = (aur_dir / "decoration.svg").read_text(encoding="utf-8")
            self.assertIn('id="decoration-maximized-top"', dec_svg)
            self.assertIn('id="decoration-maximized-center"', dec_svg)
            self.assertIn('id="decoration-maximized-inactive-center"', dec_svg)
            self.assertIn('id="noxforge-decoration-style"', dec_svg)
            self.assertIn('id="hint-stretch-borders"', dec_svg)
            self.assertIn("BorderLeft=2", rc)
            self.assertIn("BorderRight=2", rc)
            self.assertIn("BorderBottom=2", rc)
            self.assertNotIn("<filter", dec_svg)
            self.assertNotIn("feGaussianBlur", dec_svg)
            # Regression: decoration-top must never contain a partial accent rail that tiles as green dashes
            top_match = re.search(r'<g id="decoration-top">.*?</g>', dec_svg, re.DOTALL)
            self.assertIsNotNone(top_match)
            self.assertNotIn("ColorScheme-Highlight", top_match.group(0))

            # Plasma desktoptheme overhauled widgets & KF6Svg-safe custom style block
            plasma_dir = ROOT / "plasma/desktoptheme" / theme_id / "widgets"
            for widget_svg in ("notes.svg", "clock.svg", "calendar.svg", "analog_meter.svg", "glowbar.svg", "checkmarks.svg"):
                p = plasma_dir / widget_svg
                self.assertTrue(p.is_file(), f"Missing {theme_id}/widgets/{widget_svg}")
                self.assertIn('id="noxforge-plasma-style"', p.read_text(encoding="utf-8"))

            # Look-and-Feel OSD & SystemDialog canonical generated QML with zero raw hex
            lnf_dir = ROOT / "look-and-feel" / theme_id / "contents"
            for rel, src in (
                ("osd/Osd.qml", "qml/shared/osd/Osd.qml"),
                ("osd/OsdItem.qml", "qml/shared/osd/OsdItem.qml"),
                ("systemdialog/SystemDialog.qml", "qml/shared/systemdialog/SystemDialog.qml"),
            ):
                qml = lnf_dir / rel
                self.assertTrue(qml.is_file(), f"Missing generated QML: {qml}")
                text = qml.read_text(encoding="utf-8")
                self.assertTrue(text.startswith(f"// GENERATED from {src}"), f"Bad header in {qml}")
                self.assertIsNone(
                    re.search(r"#[0-9A-Fa-f]{6}", text),
                    f"Raw hex literal forbidden in {qml}",
                )

    def test_union_68_modular_css_and_differentiated_gtk3_gtk4(self) -> None:
        modules = (
            "defaults.css",
            "button.css",
            "check.css",
            "bars.css",
            "tabs.css",
            "text.css",
            "popup.css",
            "tables.css",
            "kirigami.css",
            "calendar.css",
        )
        for style_id in ("noxforge", "noxforge-obsidian"):
            css_dir = ROOT / "union/styles" / style_id / "contents/css"
            style_css = (css_dir / "style.css").read_text(encoding="utf-8")
            self.assertIn('@import "variables.css";', style_css)
            for mod in modules:
                self.assertIn(f'@import "{mod}";', style_css)
                self.assertTrue((css_dir / mod).is_file(), f"Missing Union module: {css_dir / mod}")

        for theme_dir in ("themes/NoxForge", "themes/NoxForgeObsidian"):
            gtk3 = (ROOT / theme_dir / "gtk-3.0/gtk.css").read_text(encoding="utf-8")
            gtk4 = (ROOT / theme_dir / "gtk-4.0/gtk.css").read_text(encoding="utf-8")
            self.assertNotEqual(gtk3, gtk4, f"{theme_dir} GTK 3 and GTK 4 CSS should be differentiated")
            for selector in ("windowcontrols", "switch > slider", "viewswitcher", "statuspage", ":backdrop"):
                self.assertIn(selector, gtk4, f"Missing GTK 4 selector {selector} in {theme_dir}")

    def test_noxforge_ctl_v21_live_core_presets_fastfetch_and_flatpak(self) -> None:
        ctl = ROOT / "tools/noxforge-ctl"
        env = os.environ.copy()
        env["NOXFORGE_SKIP_LIVE_RELOAD"] = "1"

        # New accents crimson & ice
        for name, expected_hex in (("crimson", "#FF8FA3"), ("ice", "#93C5FD")):
            res = subprocess.run(
                [sys.executable, str(ctl), "accent", name, "--dry-run", "--json"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res.returncode, 0, res.stderr)
            payload = json.loads(res.stdout)
            self.assertEqual(payload["hex"], expected_hex)
            self.assertIn("auroraeSynced", payload)

        # Wallpaper accent extraction
        wp_path = ROOT / "wallpapers/NoxForge/contents/images/1920x1080.png"
        ext = subprocess.run(
            [sys.executable, str(ctl), "accent", "--from-wallpaper", str(wp_path), "--dry-run", "--json"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(ext.returncode, 0, ext.stderr)
        ext_data = json.loads(ext.stdout)
        self.assertRegex(ext_data["hex"], r"^#[0-9A-F]{6}$")
        ratio_g, ratio_o = noxforge_core.validate_custom_accent_contrast(ext_data["hex"])
        self.assertGreaterEqual(ratio_g, 4.5)
        self.assertGreaterEqual(ratio_o, 4.5)

        # Presets CRUD + Fastfetch presets + Flatpak icons/cursors overrides
        with tempfile.TemporaryDirectory(prefix="noxforge-v21-ctl-") as temp:
            iso_env = env.copy()
            iso_env["HOME"] = temp
            iso_env["XDG_CONFIG_HOME"] = str(Path(temp) / ".config")
            iso_env["XDG_DATA_HOME"] = str(Path(temp) / ".local/share")

            save_res = subprocess.run(
                [sys.executable, str(ctl), "preset", "save", "studio-night", "--json"],
                cwd=ROOT,
                env=iso_env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(save_res.returncode, 0, save_res.stderr)
            self.assertEqual(json.loads(save_res.stdout)["status"], "saved")

            list_res = subprocess.run(
                [sys.executable, str(ctl), "preset", "list", "--json"],
                cwd=ROOT,
                env=iso_env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(list_res.returncode, 0, list_res.stderr)
            presets = json.loads(list_res.stdout)["presets"]
            self.assertIn("studio-night", presets)
            self.assertIn("profile", presets["studio-night"])

            del_res = subprocess.run(
                [sys.executable, str(ctl), "preset", "delete", "studio-night", "--json"],
                cwd=ROOT,
                env=iso_env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(del_res.returncode, 0, del_res.stderr)
            self.assertEqual(json.loads(del_res.stdout)["status"], "deleted")

            for ff_preset in ("main", "cyber", "minimal"):
                ff_res = subprocess.run(
                    [sys.executable, str(ctl), "fastfetch", "--preset", ff_preset, "--dry-run", "--json"],
                    cwd=ROOT,
                    env=iso_env,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(ff_res.returncode, 0, ff_res.stderr)
                self.assertEqual(json.loads(ff_res.stdout)["preset"], ff_preset)

            fp_res = subprocess.run(
                [sys.executable, str(ctl), "flatpak", "--enable", "--json"],
                cwd=ROOT,
                env=iso_env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(fp_res.returncode, 0, fp_res.stderr)
            fp_content = (Path(iso_env["XDG_DATA_HOME"]) / "flatpak/overrides/global").read_text(encoding="utf-8")
            self.assertIn("xdg-data/icons:ro", fp_content)
            self.assertIn("xdg-data/cursors:ro", fp_content)

        # Shell completions expose V21 subcommands, accents, and apps
        for shell in ("bash", "zsh", "fish"):
            comp = subprocess.run(
                [sys.executable, str(ctl), "completion", shell],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(comp.returncode, 0, comp.stderr)
            for token in ("crimson", "ice", "preset", "fastfetch", "bat", "delta", "fzf", "eza", "wofi"):
                self.assertIn(token, comp.stdout, f"Missing {token} in {shell} completion")

    def test_ecosystem_v4_25_apps_neovim_vscode_firefox_and_fastfetch(self) -> None:
        ctl_ns = runpy.run_path(str(ROOT / "tools/noxforge-ctl"), run_name="noxforge_ctl_v21_eco4")
        self.assertGreaterEqual(len(ctl_ns["SUPPORTED_ECOSYSTEM_APPS"]), 25)
        for app_id in ("bat", "delta", "fzf", "eza", "wofi", "fastfetch"):
            self.assertIn(app_id, ctl_ns["SUPPORTED_ECOSYSTEM_APPS"])

        v4_files = (
            "terminals/bat/NoxForge.tmTheme",
            "terminals/bat/NoxForgeObsidian.tmTheme",
            "terminals/delta/noxforge.gitconfig",
            "terminals/delta/noxforge_obsidian.gitconfig",
            "terminals/fzf/noxforge.sh",
            "terminals/fzf/noxforge_obsidian.sh",
            "terminals/eza/theme.yml",
            "terminals/eza/theme_obsidian.yml",
            "apps/wofi/style.css",
            "apps/wofi/style_obsidian.css",
            "tools/fastfetch/noxforge.jsonc",
            "tools/fastfetch/noxforge-cyber.jsonc",
            "tools/fastfetch/noxforge-minimal.jsonc",
            "browsers/firefox/userContent.css",
            "browsers/firefox/userContent_obsidian.css",
            "terminals/starship/starship-obsidian.toml",
        )
        for rel in v4_files:
            path = ROOT / rel
            self.assertTrue(path.is_file(), f"Missing Ecosystem v4 file: {rel}")
            if not rel.endswith(".jsonc"):
                expected_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
                self.assertIn(expected_version, path.read_text(encoding="utf-8"), f"Missing version marker in {rel}")
            else:
                parsed = json.loads(path.read_text(encoding="utf-8"))
                self.assertIn("modules", parsed)
        for logo in ("tools/fastfetch/logo.txt", "tools/fastfetch/logo_cyber.txt", "tools/fastfetch/logo_minimal.txt"):
            self.assertTrue((ROOT / logo).is_file(), f"Missing Fastfetch logo: {logo}")

        # Deepened Neovim & VS Code
        nvim = (ROOT / "editors/neovim/colors/noxforge.lua").read_text(encoding="utf-8")
        hi_matches = re.findall(r'^\s+(?:[A-Za-z_][A-Za-z0-9_]*|\["[^"]+"\])\s*=\s*\{', nvim, re.MULTILINE)
        self.assertGreaterEqual(len(hi_matches), 140, f"Expected >=140 Neovim highlight groups, got {len(hi_matches)}")

        vscode = json.loads((ROOT / "editors/vscode/themes/noxforge-dark-color-theme.json").read_text(encoding="utf-8"))
        self.assertTrue(vscode.get("semanticHighlighting"))
        self.assertGreaterEqual(len(vscode.get("semanticTokenColors", {})), 15)

        res = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools/noxforge-ctl"),
                "ecosystem",
                "apply",
                "bat",
                "delta",
                "fzf",
                "eza",
                "wofi",
                "fastfetch",
                "--dry-run",
                "--json",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res.returncode, 0, res.stderr)
        payload = json.loads(res.stdout)
        self.assertEqual(payload["status"], "dry-run")
        self.assertEqual(payload["applied"], ["bat", "delta", "fzf", "eza", "wofi", "fastfetch"])

    def test_doctor_schema_14_and_honest_metadata_version(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noxforge-v21-doc-") as temp:
            root = Path(temp)
            stage_complete(root)
            report = doctor_fn["build_report"](root)
            self.assertEqual(report["schemaVersion"], 14)
            self.assertEqual(report["status"], "ok")
            for key in (
                "qtStyleLoadable",
                "kwinBlurStatus",
                "gtkImportIntegrity",
                "flatpakIconAccess",
                "dayNightTimerStatus",
            ):
                self.assertIn(key, report, f"Missing Doctor Schema 14 field: {key}")
            self.assertIn("configDrift", report["ecosystemState"])
            unknown = [k for k, v in report["components"].items() if v["metadataStatus"] == "unknown"]
            self.assertEqual(unknown, [])

            # Honest metadata_version regression: stripping version comment must yield metadataStatus == "unknown"
            color_file = root / "usr/share/color-schemes/NoxForgeDark.colors"
            color_file.write_text("[General]\nName=NoxForge Dark\n", encoding="utf-8")
            report_unversioned = doctor_fn["build_report"](root)
            self.assertEqual(
                report_unversioned["components"]["color-scheme"]["metadataStatus"],
                "unknown",
                "Doctor must NOT blindly report ok when version metadata is absent",
            )

    @unittest.skipUnless(HAVE_PYSIDE6, "PySide6 is not installed")
    def test_control_center_v6_ui_and_obsidian_surface(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PySide6 import QtWidgets

        _app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        loader = importlib.machinery.SourceFileLoader("cc_v21", str(ROOT / "tools/control_center.py"))
        spec = importlib.util.spec_from_loader("cc_v21", loader)
        assert spec is not None
        cc = importlib.util.module_from_spec(spec)
        loader.exec_module(cc)

        self.assertTrue(hasattr(cc, "CommandWorker"))
        win = cc.ControlCenterWindow()
        prof = win.tab_profile
        self.assertTrue({"lime", "cyan", "violet", "amber", "crimson", "ice", "system"}.issubset(set(prof.accent_buttons.keys())))
        self.assertTrue(hasattr(prof, "btn_extract_wallpaper"))
        self.assertTrue(hasattr(prof, "chk_sync_wallpaper"))
        self.assertTrue(hasattr(prof, "live_preview_group"))
        self.assertTrue(hasattr(prof, "presets_group"))
        self.assertTrue(hasattr(win.tab_health, "themeChanged"))

        eco = win.tab_eco
        self.assertEqual(eco.fastfetch_combo.count(), 3)
        self.assertGreaterEqual(eco.table.rowCount(), 25)
        eco.search_input.setText("eza")
        visible_rows = [r for r in range(eco.table.rowCount()) if not eco.table.isRowHidden(r)]
        self.assertEqual(len(visible_rows), 1)
        eco.search_input.clear()

        win.refresh_theme(profile="obsidian", accent_hex="#FF8FA3")
        qss = win.styleSheet()
        self.assertIn("#000000", qss)
        self.assertIn("#FF8FA3", qss)
        win.close()


if __name__ == "__main__":
    unittest.main()
