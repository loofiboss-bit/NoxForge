# SPDX-License-Identifier: MIT
"""Automated contracts and regression tests for NoxForge v13 True Obsidian OLED Parity & Dual-Stack Architecture."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class NoxForgeV13ContractsTests(unittest.TestCase):
    def test_v13_plan_is_present_and_indexed(self) -> None:
        plan = ROOT / "docs/NOXFORGE_V13_PLAN.md"
        self.assertTrue(plan.is_file())
        text = plan.read_text(encoding="utf-8")
        self.assertIn("NoxForge 13", text)
        self.assertIn("True Obsidian OLED Parity", text)

        impl_plan = (ROOT / "docs/IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
        self.assertIn("NOXFORGE_V13_PLAN.md", impl_plan)

    def test_v13_version_and_release_manifest_authority(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertIn(version, ("13.0.0", "13.0.1", "13.0.2"))

        manifest = json.loads((ROOT / "distribution/release-manifest.json").read_text(encoding="utf-8"))
        self.assertIn(manifest["release"]["version"], ("13.0.0", "13.0.1", "13.0.2"))
        self.assertIn(manifest["release"]["stableVersion"], ("13.0.0", "13.0.1", "13.0.2"))
        self.assertEqual(manifest["release"]["activePlan"], "docs/NOXFORGE_V13_PLAN.md")
        self.assertEqual(manifest["evidence"]["activeRoot"], "docs/evidence/v13")

    def test_v13_tokens_schema_9_and_obsidian_palette(self) -> None:
        tokens = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))
        self.assertEqual(tokens["schemaVersion"], 9)
        self.assertIn(tokens["version"], ("13.0.0", "13.0.1", "13.0.2"))

        colors = tokens["colors"]
        obsidian = tokens["colorsObsidian"]

        # Obsidian surfaces must be pure black or very deep black
        self.assertEqual(obsidian["background"], "#000000")
        self.assertEqual(obsidian["surfaceSunken"], "#05080A")
        self.assertEqual(obsidian["surface"], "#0A0F13")

        # Standard graphite surfaces differ from obsidian
        self.assertEqual(colors["background"], "#0D1419")
        self.assertEqual(colors["surfaceSunken"], "#10191F")
        self.assertEqual(colors["surface"], "#141E25")

        # Text, accent, border, and detail tokens must be 100% identical between standard and obsidian
        self.assertEqual(colors["accent"], obsidian["accent"])
        self.assertEqual(colors["accentPressed"], obsidian["accentPressed"])
        self.assertEqual(colors["textPrimary"], obsidian["textPrimary"])
        self.assertEqual(colors["textSecondary"], obsidian["textSecondary"])
        self.assertEqual(colors["border"], obsidian["border"])
        self.assertEqual(colors["borderStrong"], obsidian["borderStrong"])

    def test_cpp_style_dual_palette_generation(self) -> None:
        header = (ROOT / "src/style/noxforgepalette.h").read_text(encoding="utf-8")
        self.assertIn("namespace Standard", header)
        self.assertIn("namespace Obsidian", header)
        self.assertIn("struct PaletteColors", header)
        self.assertIn("inline PaletteColors palette(bool obsidian = false)", header)
        self.assertIn("inline QColor background(bool obsidian = false)", header)

    def test_plasma_and_aurorae_obsidian_assets_exist(self) -> None:
        plasma_dir = ROOT / "plasma/desktoptheme/io.github.loofiboss.noxforge.obsidian.desktop"
        self.assertTrue((plasma_dir / "metadata.json").is_file())
        self.assertTrue((plasma_dir / "plasmarc").is_file())
        self.assertTrue((plasma_dir / "colors").is_file())

        aurorae_dir = ROOT / "aurorae/io.github.loofiboss.noxforge.obsidian.desktop"
        self.assertTrue((aurorae_dir / "metadata.desktop").is_file())
        self.assertTrue((aurorae_dir / "decoration.svg").is_file())
        rc = (aurorae_dir / "io.github.loofiboss.noxforge.obsidian.desktoprc").read_text(encoding="utf-8")
        self.assertIn("BorderLeft=6", rc)
        self.assertIn("PaddingTop=0", rc)
        self.assertIn("Shadow=false", rc)

    def test_wallpapers_and_sddm_obsidian_exist(self) -> None:
        self.assertTrue((ROOT / "wallpapers/NoxForge-Obsidian/metadata.json").is_file())
        self.assertTrue((ROOT / "wallpapers/NoxForge-Obsidian-Ultrawide/metadata.json").is_file())
        self.assertTrue((ROOT / "wallpapers/NoxForge-Obsidian/contents/images/3840x2160.png").is_file())

        sddm_dir = ROOT / "sddm/NoxForgeObsidian"
        self.assertTrue((sddm_dir / "metadata.desktop").is_file())
        self.assertTrue((sddm_dir / "Main.qml").is_file())
        self.assertTrue((sddm_dir / "theme.conf").is_file())
        self.assertTrue((sddm_dir / "Tokens.qml").is_file())
        self.assertTrue((sddm_dir / "background.png").is_file())

    def test_neovim_and_helix_editor_themes_exist(self) -> None:
        self.assertTrue((ROOT / "editors/neovim/colors/noxforge.lua").is_file())
        self.assertTrue((ROOT / "editors/neovim/colors/noxforge_obsidian.lua").is_file())
        self.assertTrue((ROOT / "editors/helix/themes/noxforge.toml").is_file())
        self.assertTrue((ROOT / "editors/helix/themes/noxforge_obsidian.toml").is_file())

        nvim_text = (ROOT / "editors/neovim/colors/noxforge_obsidian.lua").read_text(encoding="utf-8")
        self.assertIn("NoxForge Obsidian Neovim", nvim_text)
        self.assertIn("#000000", nvim_text)

        helix_text = (ROOT / "editors/helix/themes/noxforge_obsidian.toml").read_text(encoding="utf-8")
        self.assertIn("NoxForge Obsidian Helix", helix_text)
        self.assertIn('"#000000"', helix_text)

    def test_doctor_schema_6_and_palette_synchronization(self) -> None:
        doctor = ROOT / "tools/noxforge-doctor"
        with tempfile.TemporaryDirectory(prefix="noxforge-v13-doctor-") as temp:
            result = subprocess.run(
                [sys.executable, str(doctor), "--root", temp, "--json"],
                capture_output=True,
                text=True,
                check=False,
                cwd=ROOT,
            )
        report = json.loads(result.stdout)
        self.assertEqual(report["schemaVersion"], 6)
        self.assertIn("paletteSynchronization", report)
        self.assertIn("editor-neovim", report["missing"])
        self.assertIn("editor-neovim-obsidian", report["missing"])
        self.assertIn("editor-helix", report["missing"])
        self.assertIn("editor-helix-obsidian", report["missing"])
        self.assertIn("global-theme-obsidian", report["missing"])
        self.assertIn("plasma-style-obsidian", report["missing"])
        self.assertIn("aurorae-obsidian", report["missing"])
        self.assertIn("wallpaper-obsidian", report["missing"])

    def test_build_system_installs_v13_assets(self) -> None:
        cmake = (ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
        self.assertIn("NOXFORGE_OBSIDIAN_THEME_ID", cmake)
        self.assertIn("editors/neovim", cmake)
        self.assertIn("editors/helix", cmake)
        self.assertIn("wallpapers/NoxForge-Obsidian", cmake)
        self.assertIn("sddm/NoxForgeObsidian", cmake)
        self.assertIn("sddm-obsidian-qml-surface", cmake)

        spec = (ROOT / "packaging/noxforge.spec").read_text(encoding="utf-8")
        self.assertTrue(any(f"Version:        {v}" in spec for v in ("13.0.0", "13.0.1", "13.0.2")))
        self.assertIn("NoxForgeObsidian", spec)

        pkgbuild = (ROOT / "packaging/arch/PKGBUILD").read_text(encoding="utf-8")
        self.assertTrue(any(f"pkgver={v}" in pkgbuild for v in ("13.0.0", "13.0.1", "13.0.2")))


if __name__ == "__main__":
    unittest.main()
