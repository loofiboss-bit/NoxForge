# SPDX-License-Identifier: MIT
"""Automated contracts and regression tests for NoxForge v15.0.0."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class NoxForgeV15ContractsTests(unittest.TestCase):
    def test_v15_plan_is_present_and_indexed(self) -> None:
        plan = ROOT / "docs/NOXFORGE_V15_PLAN.md"
        self.assertTrue(plan.is_file(), "docs/NOXFORGE_V15_PLAN.md is missing")
        text = plan.read_text(encoding="utf-8")
        self.assertIn("NoxForge 15", text)
        self.assertIn("v15.0.0", text)

        impl_plan = (ROOT / "docs/IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
        self.assertIn("NOXFORGE_V15_PLAN.md", impl_plan)

    def test_version_and_release_manifest_authority(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(version, "15.0.0")

        manifest = json.loads((ROOT / "distribution/release-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["release"]["version"], "15.0.0")
        self.assertEqual(manifest["release"]["stableVersion"], "15.0.0")
        self.assertEqual(manifest["release"]["activePlan"], "docs/NOXFORGE_V15_PLAN.md")

    def test_tokens_schema_11_and_signal_interactions(self) -> None:
        tokens = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))
        self.assertEqual(tokens["schemaVersion"], 11)
        self.assertEqual(tokens["version"], "15.0.0")

        # Signal tokens
        self.assertIn("signal", tokens["iconography"])
        signal = tokens["iconography"]["signal"]
        for key in ("tiers", "arcRadii", "inactiveOpacity", "dotRadius"):
            self.assertIn(key, signal, f"Missing {key} in signal tokens")
        self.assertEqual(signal["tiers"], [0, 25, 50, 75, 100])
        self.assertEqual(signal["inactiveOpacity"], 0.25)
        self.assertEqual(signal["arcRadii"], [6, 10, 14])
        self.assertEqual(signal["dotRadius"], 1.5)

        # Motion interactions tokens
        self.assertIn("interactions", tokens["motion"])
        interactions = tokens["motion"]["interactions"]
        self.assertIn("errorShake", interactions)
        self.assertEqual(interactions["errorShake"]["durationMs"], 220)
        self.assertEqual(interactions["errorShake"]["steps"], [-8, 8, -5, 5, -2, 0])
        self.assertEqual(interactions["cardScale"], 1.04)
        self.assertEqual(interactions["progressPulseMs"], 1200)

    def test_v15_vector_icon_suite_geometry_and_color_scheme(self) -> None:
        v15_icons = [
            "status/network-wireless-connected-00.svg",
            "status/network-wireless-connected-25.svg",
            "status/network-wireless-connected-50.svg",
            "status/network-wireless-connected-75.svg",
            "status/network-wireless-connected-100.svg",
            "status/network-wireless-acquiring.svg",
            "status/network-wireless-locked.svg",
            "status/network-wireless-hotspot.svg",
            "status/network-wireless-disconnected.svg",
            "status/battery-000.svg",
            "status/battery-100.svg",
        ]
        scalable_dir = ROOT / "icons/NoxForge/scalable"
        opt_16 = ROOT / "icons/NoxForge/16x16"
        opt_22 = ROOT / "icons/NoxForge/22x22"

        seen_bodies: set[str] = set()
        for rel in v15_icons:
            svg_path = scalable_dir / rel
            self.assertTrue(svg_path.is_file(), f"Missing scalable icon: {rel}")
            content = svg_path.read_text(encoding="utf-8")

            # Check FreeDesktop / KDE current-color-scheme styling
            self.assertIn('id="current-color-scheme"', content, f"{rel} lacks current-color-scheme")
            self.assertIn("ColorScheme-Text", content, f"{rel} lacks ColorScheme-Text")

            # XML valid root and 24x24 viewBox
            root = ET.fromstring(content)
            self.assertEqual(root.attrib.get("viewBox"), "0 0 24 24")

            # Verify optical variants exist
            self.assertTrue((opt_16 / rel).is_file(), f"Missing 16x16 variant for {rel}")
            self.assertTrue((opt_22 / rel).is_file(), f"Missing 22x22 variant for {rel}")

            # Verify geometric uniqueness among signal levels
            seen_bodies.add(content)

        # Every icon in the suite must have distinct content (no fallback aliasing)
        self.assertEqual(len(seen_bodies), len(v15_icons), "Found identical SVG bodies in v15 icon suite")

    def test_plasma_busywidget_orbital_radar(self) -> None:
        standard_busy = ROOT / "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop/widgets/busywidget.svg"
        obsidian_busy = ROOT / "plasma/desktoptheme/io.github.loofiboss.noxforge.obsidian.desktop/widgets/busywidget.svg"

        self.assertTrue(standard_busy.is_file())
        self.assertTrue(obsidian_busy.is_file())

        std_content = standard_busy.read_text(encoding="utf-8")
        obs_content = obsidian_busy.read_text(encoding="utf-8")

        # Must contain orbital radar geometry
        self.assertIn("busywidget", std_content)
        self.assertIn("16-16-busywidget", std_content)
        self.assertIn("22-22-busywidget", std_content)
        self.assertIn("busywidget", obs_content)

        # Verify XML well-formedness
        ET.fromstring(std_content)
        ET.fromstring(obs_content)

    def test_kinetic_surfaces_error_shake_and_tokens(self) -> None:
        graphite_ls = ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/lockscreen/LockScreen.qml"
        obsidian_ls = ROOT / "look-and-feel/io.github.loofiboss.noxforge.obsidian.desktop/contents/lockscreen/LockScreen.qml"

        for ls_path in (graphite_ls, obsidian_ls):
            content = ls_path.read_text(encoding="utf-8")
            self.assertIn("errorShakeAnim", content, f"errorShakeAnim missing in {ls_path}")
            self.assertIn("shakeOffset", content, f"shakeOffset missing in {ls_path}")
            self.assertIn("network-wireless", content, f"Wi-Fi status badge missing in {ls_path}")
            self.assertIn("battery", content, f"Battery status badge missing in {ls_path}")

        sddm_main = ROOT / "sddm/NoxForge/Main.qml"
        sddm_obsidian = ROOT / "sddm/NoxForgeObsidian/Main.qml"

        for sddm_path in (sddm_main, sddm_obsidian):
            content = sddm_path.read_text(encoding="utf-8")
            self.assertIn("errorShakeAnim", content, f"errorShakeAnim missing in {sddm_path}")
            self.assertIn("shakeOffset", content, f"shakeOffset missing in {sddm_path}")

    def test_control_center_live_preview_and_shake(self) -> None:
        cc_path = ROOT / "tools/control_center.py"
        self.assertTrue(cc_path.is_file())
        content = cc_path.read_text(encoding="utf-8")

        self.assertIn("Live Icon & Kinetic Motion Preview", content)
        self.assertIn("Test Kinetic Spring Motion (220ms)", content)
        self.assertIn("play_test_shake", content)
        self.assertIn("preview_badges", content)

    def test_doctor_schema_8_and_icon_adaptation(self) -> None:
        doctor = ROOT / "tools/noxforge-doctor"
        with tempfile.TemporaryDirectory(prefix="noxforge-v15-doctor-") as temp:
            root = Path(temp)
            # Stage the repository icons
            shutil.copytree(ROOT / "icons/NoxForge", root / "usr/share/icons/NoxForge")
            result = subprocess.run(
                [sys.executable, str(doctor), "--root", str(root), "--json"],
                capture_output=True,
                text=True,
                check=False,
                cwd=ROOT,
            )
        self.assertEqual(result.returncode, 0)  # Component edition with standalone icons is valid
        report = json.loads(result.stdout)
        self.assertEqual(report["schemaVersion"], 8)
        self.assertIn("iconAdaptation", report)

        adaptation = report["iconAdaptation"]
        self.assertEqual(adaptation["status"], "ok")
        self.assertEqual(adaptation["scalableAdaptiveCount"], 201)
        self.assertEqual(adaptation["missingAdaptive"], [])
        self.assertEqual(adaptation["v15SignalSuite"]["status"], "ok")
        self.assertEqual(adaptation["v15SignalSuite"]["checked"], 11)
        self.assertEqual(adaptation["v15SignalSuite"]["missing"], [])

    def test_build_system_installs_v15_assets(self) -> None:
        spec = (ROOT / "packaging/noxforge.spec").read_text(encoding="utf-8")
        self.assertIn("Version:        15.0.0", spec)

        pkgbuild = (ROOT / "packaging/arch/PKGBUILD").read_text(encoding="utf-8")
        self.assertIn("pkgver=15.0.0", pkgbuild)

        srcinfo = (ROOT / "packaging/arch/.SRCINFO").read_text(encoding="utf-8")
        self.assertIn("pkgver = 15.0.0", srcinfo)

    def test_ctl_sync_subcommand(self) -> None:
        ctl = ROOT / "tools/noxforge-ctl"
        res = subprocess.run(
            [sys.executable, str(ctl), "sync", "-n", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertEqual(data["status"], "dry-run")
        self.assertIn("cursorTheme", data["changes"])
        self.assertEqual(data["changes"]["cursorTheme"], "NoxForge-Cursors")
        self.assertEqual(data["changes"]["widgetStyle"], "NoxForge")
        self.assertEqual(data["changes"]["iconTheme"], "NoxForge")

    def test_application_icons_and_desktop_entries(self) -> None:
        cc_icon = ROOT / "icons/hicolor/scalable/apps/io.github.loofiboss.noxforge.controlcenter.svg"
        op_icon = ROOT / "icons/hicolor/scalable/apps/io.github.loofiboss.noxforge.opacity.svg"
        self.assertTrue(cc_icon.is_file(), "Control center app icon must exist")
        self.assertTrue(op_icon.is_file(), "Opacity configurator app icon must exist")
        self.assertIn("viewBox=\"0 0 512 512\"", cc_icon.read_text(encoding="utf-8"))
        self.assertIn("viewBox=\"0 0 512 512\"", op_icon.read_text(encoding="utf-8"))

        cc_desk = (ROOT / "distribution/io.github.loofiboss.noxforge.controlcenter.desktop").read_text(encoding="utf-8")
        op_desk = (ROOT / "distribution/io.github.loofiboss.noxforge.opacity.desktop").read_text(encoding="utf-8")
        self.assertIn("Icon=io.github.loofiboss.noxforge.controlcenter", cc_desk)
        self.assertIn("Icon=io.github.loofiboss.noxforge.opacity", op_desk)

        cmake = (ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
        self.assertIn("icons/hicolor/scalable/apps/io.github.loofiboss.noxforge.controlcenter.svg", cmake)
        self.assertIn("icons/hicolor/scalable/apps/io.github.loofiboss.noxforge.opacity.svg", cmake)

        spec = (ROOT / "packaging/noxforge.spec").read_text(encoding="utf-8")
        self.assertIn("%{_datadir}/icons/hicolor/scalable/apps/io.github.loofiboss.noxforge.controlcenter.svg", spec)
        self.assertIn("%{_datadir}/icons/hicolor/scalable/apps/io.github.loofiboss.noxforge.opacity.svg", spec)


if __name__ == "__main__":
    unittest.main()
