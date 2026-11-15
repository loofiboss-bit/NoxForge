# SPDX-License-Identifier: MIT
"""Automated contracts and regression tests for NoxForge v20.0.0 (Kinetic Iconography, Multi-Level Status Engine & Ecosystem v3)."""

from __future__ import annotations

import hashlib
import importlib.machinery
import importlib.util
import json
import os
import re
import runpy
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


class NoxForgeV20ContractsTests(unittest.TestCase):
    def test_v20_plan_manifest_and_tokens_schema_16(self) -> None:
        plan = ROOT / "docs/NOXFORGE_V20_PLAN.md"
        self.assertTrue(plan.is_file(), "docs/NOXFORGE_V20_PLAN.md is missing")
        plan_text = plan.read_text(encoding="utf-8")
        self.assertIn("NoxForge 20.0.0", plan_text)
        self.assertIn("Kinetic Iconography", plan_text)

        impl_plan = (ROOT / "docs/IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
        self.assertIn("NOXFORGE_V20_PLAN.md", impl_plan)

        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(version, "20.0.0")
        self.assertEqual(noxforge_core.get_app_version(), "20.0.0")

        manifest = json.loads((ROOT / "distribution/release-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["release"]["version"], "20.0.0")
        self.assertEqual(manifest["release"]["activePlan"], "docs/NOXFORGE_V20_PLAN.md")
        self.assertEqual(manifest["evidence"]["activeRoot"], "docs/evidence/v20")
        self.assertIn("docs/evidence/v20", manifest["source"]["include"])

        tokens = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))
        self.assertEqual(tokens["schemaVersion"], 16)
        self.assertEqual(tokens["version"], "20.0.0")
        self.assertEqual(
            tokens["kineticIconography"]["levels"],
            [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        )
        self.assertEqual(tokens["kineticIconography"]["spriteFrames"], 16)
        self.assertTrue(tokens["kineticIconography"]["respectsReducedMotion"])
        self.assertEqual(tokens["ecosystemV3"]["apps"], ["yazi", "lazygit", "zellij", "tmux"])

    def test_icons_multi_level_matrix_and_kinetic_animations(self) -> None:
        scalable_dir = ROOT / "icons/NoxForge/scalable"
        status_dir = scalable_dir / "status"
        required_rel: list[str] = []
        for lvl in range(0, 101, 10):
            required_rel.append(f"status/battery-{lvl:03d}.svg")
            required_rel.append(f"status/battery-{lvl:03d}-charging.svg")
            required_rel.append(f"status/battery-{lvl:03d}-profile-powersave.svg")
            required_rel.append(f"status/battery-{lvl:03d}-profile-balanced.svg")
            required_rel.append(f"status/battery-{lvl:03d}-profile-performance.svg")
        for lvl in (0, 20, 40, 60, 80, 100):
            required_rel.append(f"status/network-wireless-{lvl}.svg")
            required_rel.append(f"status/network-wireless-connected-{lvl:02d}-limited.svg")
            required_rel.append(f"status/network-wireless-connected-{lvl:02d}-locked.svg")
            required_rel.append(f"status/network-mobile-{lvl}.svg")
        for lvl in (25, 50, 75):
            required_rel.append(f"status/network-wireless-connected-{lvl:02d}.svg")
            required_rel.append(f"status/network-wireless-connected-{lvl:02d}-symbolic.svg")
        required_rel.extend(
            [
                "status/battery-ups.svg",
                "devices/input-gaming-battery.svg",
                "devices/input-keyboard-battery.svg",
                "devices/input-mouse-battery.svg",
                "devices/phone-battery.svg",
                "devices/preferences-system-bluetooth-battery.svg",
                "status/network-wireless-acquiring.svg",
                "status/network-wireless-locked.svg",
                "status/network-wireless-limited.svg",
                "status/network-vpn.svg",
                "status/network-flightmode-on.svg",
                "status/audio-volume-high-warning.svg",
                "status/audio-volume-high-danger.svg",
                "status/display-brightness-off.svg",
                "status/display-brightness-low.svg",
                "status/display-brightness-medium.svg",
                "status/display-brightness-high.svg",
                "status/keyboard-brightness-off.svg",
                "status/keyboard-brightness-low.svg",
                "status/keyboard-brightness-medium.svg",
                "status/keyboard-brightness-high.svg",
            ]
        )
        for rel in sorted(set(required_rel)):
            path = scalable_dir / rel
            self.assertTrue(path.is_file(), f"Missing v20 icon: {path}")

        # Verify kinetic motion CSS gating in animated SVGs
        motion_candidates = [
            status_dir / "battery-060-charging.svg",
            status_dir / "network-wireless-acquiring.svg",
        ]
        for svg_path in motion_candidates:
            svg_text = svg_path.read_text(encoding="utf-8")
            self.assertIn("@media (prefers-reduced-motion: no-preference)", svg_text)

        # Verify 16-frame sprite sheets across 16px & 22px and animated vector in scalable animations
        for sprite_path, expected_vb in (
            (ROOT / "icons/NoxForge/16x16/animations/process-working.svg", 'viewBox="0 0 16 256"'),
            (ROOT / "icons/NoxForge/22x22/animations/process-working.svg", 'viewBox="0 0 22 352"'),
        ):
            self.assertTrue(sprite_path.is_file(), f"Missing animation sprite: {sprite_path}")
            self.assertIn(expected_vb, sprite_path.read_text(encoding="utf-8"))

        scalable_spin = ROOT / "icons/NoxForge/scalable/animations/process-working.svg"
        self.assertTrue(scalable_spin.is_file())
        spin_text = scalable_spin.read_text(encoding="utf-8")
        self.assertIn('viewBox="0 0 24 24"', spin_text)
        self.assertIn("@media (prefers-reduced-motion: no-preference)", spin_text)
        self.assertIn("animateTransform", spin_text)

        # Verify zero unexpected duplicate SVGs under scalable (exact allowlist match)
        gen = runpy.run_path(str(ROOT / "scripts/generate_visual_assets.py"), run_name="gen_visual_v20")
        allowlist = {tuple(sorted(group)) for group in gen["DUPLICATE_ALLOWLIST"]}
        hashes: dict[str, list[str]] = {}
        for svg in sorted((ROOT / "icons/NoxForge/scalable").rglob("*.svg")):
            digest = hashlib.sha256(svg.read_bytes()).hexdigest()
            hashes.setdefault(digest, []).append(svg.relative_to(ROOT / "icons/NoxForge/scalable").as_posix())
        unexpected = [
            sorted(group)
            for group in hashes.values()
            if len(group) > 1 and tuple(sorted(group)) not in allowlist
        ]
        self.assertEqual(unexpected, [], f"Unexpected duplicate scalable SVGs: {unexpected}")

    def test_plasma_desktoptheme_icon_sheets_and_elements(self) -> None:
        contract = json.loads((ROOT / "design/plasma-semantic-contract.json").read_text(encoding="utf-8"))
        families = contract["iconSheetFamilies"]
        self.assertEqual(len(families), 8)
        expected_ids = {
            "audio": ["audio-volume-high", "audio-volume-muted", "microphone-sensitivity-high"],
            "battery": ["Battery", "battery-charging", "Fill0", "Fill100"],
            "kdeconnect": ["kdeconnect", "kdeconnect-tray"],
            "media": ["media-playback-start", "media-playback-pause", "media-playback-stop"],
            "network": ["network-wireless-100", "network-wireless-60", "network-wireless-0", "network-wireless-acquiring"],
            "notification": ["notification-active", "notification-inactive", "notification-disabled"],
            "osd": ["osd-rotate-cw", "osd-shutd-screen", "osd-duplicate"],
            "system": ["system-shutdown", "system-reboot", "system-suspend"],
        }

        for theme_id in (
            "io.github.loofiboss.noxforge.desktop",
            "io.github.loofiboss.noxforge.obsidian.desktop",
        ):
            icons_dir = ROOT / "plasma/desktoptheme" / theme_id / "icons"
            self.assertTrue(icons_dir.is_dir(), f"Missing Plasma icons directory: {icons_dir}")
            for sheet_name in families:
                sheet_path = icons_dir / f"{sheet_name}.svg"
                self.assertTrue(sheet_path.is_file(), f"Missing Plasma icon sheet: {sheet_path}")
                text = sheet_path.read_text(encoding="utf-8")
                self.assertIn(".ColorScheme-Text", text)
                for element_id in expected_ids[sheet_name]:
                    self.assertIn(f'id="{element_id}"', text, f"Missing element id={element_id} in {sheet_path}")

    def test_ecosystem_v3_files_and_dry_run_apply(self) -> None:
        v3_files = (
            "apps/yazi/theme.toml",
            "apps/yazi/theme_obsidian.toml",
            "apps/lazygit/config.yml",
            "apps/lazygit/config_obsidian.yml",
            "terminals/zellij/noxforge.kdl",
            "terminals/zellij/noxforge_obsidian.kdl",
            "terminals/tmux/noxforge.conf",
            "terminals/tmux/noxforge_obsidian.conf",
        )
        for rel in v3_files:
            path = ROOT / rel
            self.assertTrue(path.is_file(), f"Missing Ecosystem v3 file: {path}")
            self.assertIn("@noxforge-version: 20.0.0", path.read_text(encoding="utf-8"))

        ctl_ns = runpy.run_path(str(ROOT / "tools/noxforge-ctl"), run_name="noxforge_ctl_v20_eco3")
        for app_id in ("yazi", "lazygit", "zellij", "tmux"):
            self.assertIn(app_id, ctl_ns["SUPPORTED_ECOSYSTEM_APPS"])

        res = subprocess.run(
            [sys.executable, str(ROOT / "tools/noxforge-ctl"), "ecosystem", "apply", "yazi", "lazygit", "zellij", "tmux", "--dry-run", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res.returncode, 0, res.stderr)
        payload = json.loads(res.stdout)
        self.assertEqual(payload["status"], "dry-run")
        self.assertEqual(payload["applied"], ["yazi", "lazygit", "zellij", "tmux"])

    def test_lockscreen_forge_status_pill_and_reduced_motion(self) -> None:
        qml_paths = (
            ROOT / "qml/shared/lockscreen/LockScreen.qml",
            ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/lockscreen/LockScreen.qml",
            ROOT / "look-and-feel/io.github.loofiboss.noxforge.obsidian.desktop/contents/lockscreen/LockScreen.qml",
        )
        for qml_path in qml_paths:
            self.assertTrue(qml_path.is_file())
            text = qml_path.read_text(encoding="utf-8")
            self.assertIn("id: forgeStatusPill", text)
            self.assertIn("id: kineticPulseDot", text)
            self.assertIn("!root.reducedMotion", text)
            self.assertIsNone(
                re.search(r"#[0-9A-Fa-f]{6}", text),
                f"Raw hex literal forbidden in generated LockScreen QML: {qml_path}",
            )

    def test_noxforge_ctl_icons_and_completions(self) -> None:
        for action in ("--status", "--verify", "--sync-accent"):
            cmd = [sys.executable, str(ROOT / "tools/noxforge-ctl"), "icons", action, "--json"]
            if action == "--sync-accent":
                cmd.append("--dry-run")
            res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(res.returncode, 0, f"{cmd} failed: {res.stderr}")
            data = json.loads(res.stdout)
            self.assertEqual(data["status"], "ok")
            self.assertTrue(data["verified"])
            self.assertGreaterEqual(data["batteryLevels"], 11)
            self.assertGreaterEqual(data["wifiLevels"], 8)
            self.assertEqual(data["plasmaIconSheets"], {"standard": 8, "obsidian": 8})

        for shell in ("bash", "zsh", "fish"):
            comp = subprocess.run(
                [sys.executable, str(ROOT / "tools/noxforge-ctl"), "completion", shell],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(comp.returncode, 0)
            self.assertIn("icons", comp.stdout)
            self.assertIn("yazi", comp.stdout)
            self.assertIn("tmux", comp.stdout)

    def test_doctor_schema_13_and_icon_level_matrix(self) -> None:
        import shutil

        with tempfile.TemporaryDirectory(prefix="noxforge-v20-doc-") as temp:
            root = Path(temp)
            stage_complete(root)
            shutil.copytree(ROOT / "icons/NoxForge", root / "usr/share/icons/NoxForge", dirs_exist_ok=True)
            for theme_id in (
                "io.github.loofiboss.noxforge.desktop",
                "io.github.loofiboss.noxforge.obsidian.desktop",
            ):
                shutil.copytree(
                    ROOT / "plasma/desktoptheme" / theme_id / "icons",
                    root / "usr/share/plasma/desktoptheme" / theme_id / "icons",
                    dirs_exist_ok=True,
                )
            report = doctor_fn["build_report"](root)
            self.assertEqual(report["schemaVersion"], 13)
            self.assertEqual(report["status"], "ok")
            matrix = report.get("iconLevelMatrix", {})
            self.assertEqual(matrix.get("status"), "ok")
            self.assertGreaterEqual(matrix.get("batteryLevels", 0), 11)
            self.assertGreaterEqual(matrix.get("wifiLevels", 0), 6)
            self.assertEqual(matrix.get("plasmaIconSheets"), {"standard": 8, "obsidian": 8})
            unknown = [k for k, v in report["components"].items() if v["metadataStatus"] == "unknown"]
            self.assertEqual(unknown, [])

    @unittest.skipUnless(HAVE_PYSIDE6, "PySide6 is not installed")
    def test_control_center_v5_kinetic_icon_studio(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PySide6 import QtWidgets

        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        _ = app
        loader = importlib.machinery.SourceFileLoader("cc_v20", str(ROOT / "tools/control_center.py"))
        spec = importlib.util.spec_from_loader("cc_v20", loader)
        assert spec is not None
        cc = importlib.util.module_from_spec(spec)
        loader.exec_module(cc)

        win = cc.ControlCenterWindow()
        self.assertEqual(win.tabs.count(), 5)
        self.assertTrue(hasattr(win.tab_health, "badge_icons"))

        prof = win.tab_profile
        self.assertEqual(prof.level_slider.minimum(), 0)
        self.assertEqual(prof.level_slider.maximum(), 120)
        self.assertEqual(prof.level_slider.accessibleName(), "Kinetic Icon Level Slider")
        self.assertEqual(prof.anim_toggle.accessibleName(), "Kinetic Icon Animation Toggle")
        self.assertEqual(set(prof.studio_cards.keys()), {"battery", "wifi", "audio", "brightness", "spinner"})

        prof.level_slider.setValue(0)
        self.assertIn("MUTED", prof.level_value_lbl.text())
        prof.level_slider.setValue(118)
        self.assertIn("DANGER", prof.level_value_lbl.text())
        prof.set_reduced_motion(True)
        self.assertFalse(prof.kinetic_timer.isActive())
        win.close()

    def test_v20_packaging_and_store_validator_parity(self) -> None:
        cmake = (ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
        self.assertIn("DIRECTORY apps/", cmake)
        self.assertIn("DIRECTORY terminals/", cmake)
        self.assertIn("DIRECTORY icons/NoxForge/", cmake)

        spec = (ROOT / "packaging/noxforge.spec").read_text(encoding="utf-8")
        self.assertIn("20.0.0-1", spec)
        self.assertIn("%{_datadir}/noxforge/apps/", spec)
        self.assertIn("%{_datadir}/noxforge/terminals/", spec)

        store_val = (ROOT / "scripts/validate_store_packages.py").read_text(encoding="utf-8")
        self.assertIn('"icons/"', store_val)
        self.assertIn("components/apps/yazi/theme.toml", store_val)
        self.assertIn("components/terminals/tmux/noxforge.conf", store_val)


if __name__ == "__main__":
    unittest.main()
