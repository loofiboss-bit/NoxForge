# SPDX-License-Identifier: MIT
"""Automated contracts and regression tests for NoxForge v14.0.0."""

from __future__ import annotations

import configparser
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def parse_rgb(value: str) -> tuple[int, int, int]:
    parts = [int(p.strip()) for p in value.split(",")]
    return parts[0], parts[1], parts[2]


class NoxForgeV14ContractsTests(unittest.TestCase):
    def test_v14_plan_is_present_and_indexed(self) -> None:
        plan = ROOT / "docs/NOXFORGE_V14_PLAN.md"
        self.assertTrue(plan.is_file(), "docs/NOXFORGE_V14_PLAN.md is missing")
        text = plan.read_text(encoding="utf-8")
        self.assertIn("NoxForge 14", text)
        self.assertIn("v14.0.0", text)

        impl_plan = (ROOT / "docs/IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
        self.assertIn("NOXFORGE_V14_PLAN.md", impl_plan)

    def test_version_and_release_manifest_authority(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertIn(version, ("14.0.0", "14.0.1", "14.0.2", "15.0.0"))

        manifest = json.loads((ROOT / "distribution/release-manifest.json").read_text(encoding="utf-8"))
        self.assertIn(manifest["release"]["version"], ("14.0.0", "14.0.1", "14.0.2", "15.0.0"))
        self.assertIn(manifest["release"]["stableVersion"], ("14.0.0", "14.0.1", "14.0.2", "15.0.0"))
        self.assertIn(manifest["release"]["activePlan"], ("docs/NOXFORGE_V14_PLAN.md", "docs/NOXFORGE_V15_PLAN.md"))

    def test_tokens_schema_10_and_accents_matrix(self) -> None:
        tokens = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))
        self.assertIn(tokens["schemaVersion"], (10, 11))
        self.assertIn(tokens["version"], ("14.0.0", "14.0.1", "14.0.2", "15.0.0"))

        self.assertIn("accents", tokens)
        accents = tokens["accents"]
        self.assertEqual(set(accents.keys()), {"lime", "cyan", "violet", "amber"})

        self.assertEqual(accents["lime"]["accent"], "#A3FF47")
        self.assertEqual(accents["cyan"]["accent"], "#22D3EE")
        self.assertEqual(accents["violet"]["accent"], "#A78BFA")
        self.assertEqual(accents["amber"]["accent"], "#FBBF24")

        for key, entry in accents.items():
            for req in ("name", "accent", "accentSoft", "accentMuted", "accentPressed"):
                self.assertIn(req, entry, f"Missing {req} in accent {key}")

    def test_kwin_tabbox_obsidian_parity(self) -> None:
        obsidian_dir = ROOT / "kwin/tabbox/io.github.loofiboss.noxforge.obsidian.desktop"
        self.assertTrue(obsidian_dir.is_dir())
        metadata_path = obsidian_dir / "metadata.json"
        self.assertTrue(metadata_path.is_file())
        meta = json.loads(metadata_path.read_text(encoding="utf-8"))
        self.assertEqual(meta["KPlugin"]["Id"], "io.github.loofiboss.noxforge.obsidian.desktop")
        self.assertIn(meta["KPlugin"]["Version"], ("14.0.0", "14.0.1", "14.0.2", "15.0.0"))

        ui_dir = obsidian_dir / "contents/ui"
        for name in ("main.qml", "Switcher.qml", "Tokens.qml"):
            file_path = ui_dir / name
            self.assertTrue(file_path.is_file(), f"{name} is missing in obsidian tabbox")

        tokens_qml = (ui_dir / "Tokens.qml").read_text(encoding="utf-8")
        self.assertIn('#000000', tokens_qml)
        self.assertIn('property int notch: 4', tokens_qml)

    def test_lockscreen_qml_exists_and_uses_tokens(self) -> None:
        graphite_ls = ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/lockscreen"
        obsidian_ls = ROOT / "look-and-feel/io.github.loofiboss.noxforge.obsidian.desktop/contents/lockscreen"

        for ls_dir, is_obsidian in ((graphite_ls, False), (obsidian_ls, True)):
            self.assertTrue(ls_dir.is_dir(), f"{ls_dir} is not a directory")
            qml = ls_dir / "LockScreen.qml"
            self.assertTrue(qml.is_file(), f"{qml} is missing")
            content = qml.read_text(encoding="utf-8")
            self.assertIn("Tokens", content)
            self.assertIn("MotionPolicy", content)
            self.assertIn("NoxForgeLockup.svg", content)

            tokens_file = ls_dir / "Tokens.qml"
            self.assertTrue(tokens_file.is_file())
            tokens_content = tokens_file.read_text(encoding="utf-8")
            if is_obsidian:
                self.assertIn('#000000', tokens_content)
            else:
                self.assertIn('#0D1419', tokens_content)

    def test_unified_control_suite_cli_and_gui(self) -> None:
        ctl = ROOT / "tools/noxforge-ctl"
        self.assertTrue(ctl.is_file())
        self.assertTrue(os.access(ctl, os.X_OK))

        result = subprocess.run(
            [sys.executable, str(ctl), "switch", "-n", "obsidian", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["status"], "dry-run")
        self.assertEqual(data["changes"]["profile"], "obsidian")
        self.assertEqual(data["changes"]["colorScheme"], "NoxForgeObsidian")

        gui = ROOT / "tools/control_center.py"
        self.assertTrue(gui.is_file())
        self.assertTrue(os.access(gui, os.X_OK))

        desktop = ROOT / "distribution/io.github.loofiboss.noxforge.controlcenter.desktop"
        self.assertTrue(desktop.is_file())
        desk_text = desktop.read_text(encoding="utf-8")
        self.assertIn("Name=NoxForge Control Center", desk_text)
        self.assertIn("Exec=noxforge-ctl gui", desk_text)

    def test_ecosystem_assets_presence_and_palette(self) -> None:
        # Firefox
        ff_chrome = ROOT / "browsers/firefox/userChrome.css"
        ff_manifest = ROOT / "browsers/firefox/manifest.json"
        self.assertTrue(ff_chrome.is_file())
        self.assertTrue(ff_manifest.is_file())
        self.assertIn("#0D1419", ff_chrome.read_text(encoding="utf-8"))
        self.assertIn("#A3FF47", ff_chrome.read_text(encoding="utf-8"))

        # Zed
        zed_graphite = ROOT / "editors/zed/themes/noxforge.json"
        zed_obsidian = ROOT / "editors/zed/themes/noxforge_obsidian.json"
        self.assertTrue(zed_graphite.is_file())
        self.assertTrue(zed_obsidian.is_file())
        zed_g_data = json.loads(zed_graphite.read_text(encoding="utf-8"))
        zed_o_data = json.loads(zed_obsidian.read_text(encoding="utf-8"))
        self.assertEqual(zed_g_data["name"], "NoxForge")
        self.assertEqual(zed_o_data["name"], "NoxForge Obsidian")

        # btop
        btop_g = ROOT / "terminals/btop/themes/noxforge.theme"
        btop_o = ROOT / "terminals/btop/themes/noxforge_obsidian.theme"
        self.assertTrue(btop_g.is_file())
        self.assertTrue(btop_o.is_file())
        self.assertIn('#0D1419', btop_g.read_text(encoding="utf-8"))
        self.assertIn('#000000', btop_o.read_text(encoding="utf-8"))

        # Starship
        starship = ROOT / "terminals/starship/starship.toml"
        self.assertTrue(starship.is_file())
        self.assertIn("#A3FF47", starship.read_text(encoding="utf-8"))

        # Fastfetch
        ff = ROOT / "tools/fastfetch/noxforge.jsonc"
        self.assertTrue(ff.is_file())
        self.assertIn("163;255;71", ff.read_text(encoding="utf-8"))

        # Discord
        discord_g = ROOT / "apps/discord/noxforge.theme.css"
        discord_o = ROOT / "apps/discord/noxforge_obsidian.theme.css"
        self.assertTrue(discord_g.is_file())
        self.assertTrue(discord_o.is_file())
        self.assertIn("#0D1419", discord_g.read_text(encoding="utf-8"))
        self.assertIn("#000000", discord_o.read_text(encoding="utf-8"))

    def test_doctor_schema_7_and_v14_components(self) -> None:
        doctor = ROOT / "tools/noxforge-doctor"
        with tempfile.TemporaryDirectory(prefix="noxforge-v14-doctor-") as temp:
            result = subprocess.run(
                [sys.executable, str(doctor), "--root", temp, "--json"],
                capture_output=True,
                text=True,
                check=False,
                cwd=ROOT,
            )
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertIn(report["schemaVersion"], (7, 8))

        missing = set(report["missing"])
        v14_required = {
            "kwin-switcher-obsidian",
            "lockscreen",
            "lockscreen-obsidian",
            "editor-zed",
            "editor-zed-obsidian",
            "terminal-btop",
            "terminal-btop-obsidian",
            "browser-firefox",
            "shell-starship",
        }
        self.assertTrue(v14_required.issubset(missing), f"Missing v14 components in report: {v14_required - missing}")

    def test_build_system_installs_v14_assets(self) -> None:
        cmake = (ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
        self.assertIn("tools/noxforge-ctl", cmake)
        self.assertIn("tools/control_center.py", cmake)
        self.assertIn("distribution/io.github.loofiboss.noxforge.controlcenter.desktop", cmake)
        self.assertIn("editors/zed/", cmake)
        self.assertIn("browsers/", cmake)
        self.assertIn("kwin/tabbox/${NOXFORGE_OBSIDIAN_THEME_ID}/", cmake)

        spec = (ROOT / "packaging/noxforge.spec").read_text(encoding="utf-8")
        self.assertIn("%{_bindir}/noxforge-ctl", spec)
        self.assertIn("%{_datadir}/applications/io.github.loofiboss.noxforge.controlcenter.desktop", spec)
        self.assertIn("%{_datadir}/noxforge/control_center.py", spec)
        self.assertIn("%{_datadir}/noxforge/browsers/", spec)
        self.assertIn("%{_datadir}/kwin/tabbox/io.github.loofiboss.noxforge.obsidian.desktop/", spec)

        pkgbuild = (ROOT / "packaging/arch/PKGBUILD").read_text(encoding="utf-8")
        self.assertTrue(any(f"pkgver={v}" in pkgbuild for v in ("14.0.0", "14.0.1", "14.0.2", "15.0.0")))


if __name__ == "__main__":
    unittest.main()
