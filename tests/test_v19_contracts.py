# SPDX-License-Identifier: MIT
"""Automated contracts and regression tests for NoxForge v19.0.0 (KDE Plasma 6.8 Union Engine, Fastfetch Kinetic Studio v2 & Wayland Precision)."""

from __future__ import annotations

import importlib.util
import json
import os
import runpy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

HAVE_PYSIDE6 = bool(importlib.util.find_spec("PySide6"))

from tests.test_doctor import DOCTOR_FUNCTIONS as doctor_fn, stage_complete  # noqa: E402
from tools import noxforge_core  # noqa: E402


class NoxForgeV19ContractsTests(unittest.TestCase):
    def test_v19_plan_manifest_and_tokens_schema_15(self) -> None:
        plan = ROOT / "docs/NOXFORGE_V19_PLAN.md"
        self.assertTrue(plan.is_file(), "docs/NOXFORGE_V19_PLAN.md is missing")
        plan_text = plan.read_text(encoding="utf-8")
        self.assertIn("NoxForge 19.0.0", plan_text)
        self.assertIn("Plasma 6.8", plan_text)

        impl_plan = (ROOT / "docs/IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
        self.assertIn("NOXFORGE_V19_PLAN.md", impl_plan)

        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(version, "19.0.0")
        self.assertEqual(noxforge_core.get_app_version(), "19.0.0")

        manifest = json.loads((ROOT / "distribution/release-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["release"]["version"], "19.0.0")
        self.assertEqual(manifest["release"]["activePlan"], "docs/NOXFORGE_V19_PLAN.md")
        self.assertEqual(manifest["compatibility"]["arch"]["plasma"], ">=6.8")
        self.assertEqual(manifest["evidence"]["activeRoot"], "docs/evidence/v19")
        self.assertIn("union", manifest["source"]["include"])

        tokens = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))
        self.assertEqual(tokens["schemaVersion"], 15)
        self.assertEqual(tokens["version"], "19.0.0")
        self.assertIn("union", tokens)
        self.assertEqual(tokens["union"]["engineVersion"], "6.8")
        self.assertEqual(tokens["union"]["inputType"], "css")
        self.assertEqual(tokens["union"]["styles"], ["noxforge", "noxforge-obsidian"])
        self.assertIn("kwin68", tokens)
        self.assertEqual(tokens["kwin68"]["displayProtocol"], "wayland-only")
        self.assertTrue(tokens["kwin68"]["csdRuleSync"])

    def test_union_68_generated_styles_and_kcolorscheme_bindings(self) -> None:
        for style_id, expected_bg in (("noxforge", "#0D1419"), ("noxforge-obsidian", "#000000")):
            style_dir = ROOT / "union/styles" / style_id
            self.assertTrue(style_dir.is_dir(), f"Missing Union style directory: {style_dir}")

            meta_path = style_dir / "metadata.json"
            self.assertTrue(meta_path.is_file())
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            self.assertEqual(meta["input-type"], "css")
            self.assertEqual(meta["input-version"], 1)
            self.assertEqual(meta["version"], "19.0.0")
            self.assertEqual(meta["license"], "MIT")

            vars_css = (style_dir / "contents/css/variables.css").read_text(encoding="utf-8")
            self.assertIn("--noxforge-canvas-fallback:", vars_css)
            self.assertIn(expected_bg, vars_css)
            self.assertIn('custom-color("kcolorscheme"', vars_css)

            style_css = (style_dir / "contents/css/style.css").read_text(encoding="utf-8")
            self.assertIn('@import "variables.css";', style_css)
            self.assertIn("applicationwindow {", style_css)
            self.assertIn("toolbutton,", style_css)
            self.assertIn("tabbutton {", style_css)
            self.assertIn("abstractcard {", style_css)

    def test_union_and_kwin_csd_cli_lifecycle(self) -> None:
        ctl_ns = runpy.run_path(str(ROOT / "tools/noxforge-ctl"), run_name="noxforge_ctl_v19_union")
        with tempfile.TemporaryDirectory(prefix="noxforge-v19-kwin-") as temp:
            temp_path = Path(temp)
            cfg_home = temp_path / ".config"
            old_cfg = os.environ.get("XDG_CONFIG_HOME")
            try:
                os.environ["XDG_CONFIG_HOME"] = str(cfg_home)
                cfg_home.mkdir(parents=True, exist_ok=True)

                # Union dry-run & status
                u_status = ctl_ns["manage_union"](action="status", profile="obsidian")
                self.assertIn("unionStyle", u_status)
                self.assertEqual(u_status["targetUnionStyle"], "noxforge-obsidian")

                u_enable_dry = ctl_ns["manage_union"](action="enable", profile="obsidian", dry_run=True)
                self.assertEqual(u_enable_dry["status"], "dry-run")
                self.assertEqual(u_enable_dry["widgetStyle"], "Union")
                self.assertEqual(u_enable_dry["unionStyle"], "noxforge-obsidian")

                # KWin 6.8 CSD rule lifecycle with pre-existing kwinrulesrc
                rules_file = cfg_home / "kwinrulesrc"
                rules_file.write_text("[General]\ncount=1\nrules=1\n\n[1]\nDescription=User rule\n", encoding="utf-8")

                csd_enable = ctl_ns["manage_kwin_csd"](action="enable", profile="obsidian", dry_run=False)
                self.assertEqual(csd_enable["status"], "enabled")
                self.assertTrue(csd_enable["enabled"])
                self.assertEqual(csd_enable["decoColor"], "NoxForgeObsidian")
                self.assertTrue((cfg_home / "kwinrulesrc.noxforge.bak").is_file())

                rules_content = rules_file.read_text(encoding="utf-8")
                self.assertIn("[noxforge-csd-harmonizer]", rules_content)
                self.assertIn("decocolor=NoxForgeObsidian", rules_content)
                self.assertIn("Description=User rule", rules_content)

                csd_disable = ctl_ns["manage_kwin_csd"](action="disable", dry_run=False)
                self.assertEqual(csd_disable["status"], "disabled")
                self.assertFalse(csd_disable["enabled"])
                self.assertEqual(
                    rules_file.read_text(encoding="utf-8"),
                    "[General]\ncount=1\nrules=1\n\n[1]\nDescription=User rule\n",
                )
            finally:
                if old_cfg is None:
                    os.environ.pop("XDG_CONFIG_HOME", None)
                else:
                    os.environ["XDG_CONFIG_HOME"] = old_cfg

    def test_systemmonitor_telemetry_page_and_ecosystem_apply(self) -> None:
        page_path = ROOT / "apps/systemmonitor/noxforge-telemetry.page"
        self.assertTrue(page_path.is_file(), "Missing apps/systemmonitor/noxforge-telemetry.page")
        page_text = page_path.read_text(encoding="utf-8")
        self.assertIn("Title=NoxForge Kinetic Telemetry", page_text)
        self.assertIn("gpu/all/usedVram", page_text)
        self.assertIn("163,255,71", page_text)

        ctl_ns = runpy.run_path(str(ROOT / "tools/noxforge-ctl"), run_name="noxforge_ctl_v19_sysmon")
        with tempfile.TemporaryDirectory(prefix="noxforge-v19-sysmon-") as temp:
            temp_path = Path(temp)
            cfg_home = temp_path / ".config"
            data_home = temp_path / ".local/share"
            old_cfg = os.environ.get("XDG_CONFIG_HOME")
            old_data = os.environ.get("XDG_DATA_HOME")
            try:
                os.environ["XDG_CONFIG_HOME"] = str(cfg_home)
                os.environ["XDG_DATA_HOME"] = str(data_home)

                res = ctl_ns["ecosystem_apply"](
                    app_names=["systemmonitor"],
                    dry_run=False,
                    profile="obsidian",
                    accent_hex="#22D3EE",
                )
                self.assertEqual(res["status"], "applied")
                self.assertIn("systemmonitor", res["applied"])

                target_page = data_home / "plasma-systemmonitor/noxforge-telemetry.page"
                self.assertTrue(target_page.is_file())
                self.assertIn("34,211,238", target_page.read_text(encoding="utf-8"))
            finally:
                for key, val in (("XDG_CONFIG_HOME", old_cfg), ("XDG_DATA_HOME", old_data)):
                    if val is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = val

    def test_doctor_schema_12_zero_metadata_unknown_and_obsidian_wallpaper(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noxforge-v19-doc-") as temp:
            root = Path(temp)
            stage_complete(root)
            report = doctor_fn["build_report"](root)
            self.assertEqual(report["schemaVersion"], 12)
            self.assertEqual(report["status"], "ok")
            self.assertIn("unionStyleStatus", report)
            self.assertIn("waylandCompositor", report)

            # Verify zero metadata-unknown across all components when VERSION is known
            unknown_components = [
                name
                for name, state in report["components"].items()
                if state["metadataStatus"] == "unknown"
            ]
            self.assertEqual(
                unknown_components,
                [],
                f"Expected 0 metadata-unknown components on complete staged root, got: {unknown_components}",
            )

            # Verify Obsidian wallpaper recognition in detect_wallpaper and login_surface_report
            cfg_dir = root / "config"
            cfg_dir.mkdir(parents=True, exist_ok=True)
            appletsrc = cfg_dir / "plasma-org.kde.plasma.desktop-appletsrc"
            appletsrc.write_text(
                "[Containments][1]\n"
                "lastScreen=0\n"
                "plugin=org.kde.plasma.folder\n"
                "wallpaperplugin=org.kde.image\n\n"
                "[Containments][1][Wallpaper][org.kde.image][General]\n"
                "Image=file:///usr/share/wallpapers/NoxForge-Obsidian/contents/images/2560x1440.png\n",
                encoding="utf-8",
            )
            old_cfg = os.environ.get("XDG_CONFIG_HOME")
            try:
                os.environ["XDG_CONFIG_HOME"] = str(cfg_dir)
                self.assertEqual(doctor_fn["detect_wallpaper"](), "NoxForge-Obsidian")
            finally:
                if old_cfg is None:
                    os.environ.pop("XDG_CONFIG_HOME", None)
                else:
                    os.environ["XDG_CONFIG_HOME"] = old_cfg

            plm_cfg = root / "etc/plasmalogin.conf"
            plm_cfg.parent.mkdir(parents=True, exist_ok=True)
            plm_cfg.write_text(
                "[Greeter][Wallpaper][org.kde.image][General]\n"
                "Image=/usr/share/wallpapers/NoxForge-Obsidian-Ultrawide/contents/images/3440x1440.png\n",
                encoding="utf-8",
            )
            with patch.dict(
                doctor_fn["build_report"].__globals__,
                {"display_manager_state": lambda _r: ("plasmalogin", "active")},
            ):
                login_rep = doctor_fn["login_surface_report"](root, report["components"])
                self.assertEqual(login_rep["asset"], "NoxForge-Obsidian-Ultrawide")
                self.assertTrue(login_rep["available"])
                self.assertTrue(login_rep["selected"])
                self.assertEqual(login_rep["status"], "selected")

    def test_v19_packaging_and_installer_parity(self) -> None:
        for rel_file in (
            "CMakeLists.txt",
            "packaging/noxforge.spec",
            "scripts/install.sh",
            "scripts/uninstall.sh",
            "scripts/uninstall-system.sh",
            "scripts/build_store_packages.py",
        ):
            text = (ROOT / rel_file).read_text(encoding="utf-8")
            self.assertIn("union/styles", text, f"Missing union/styles in {rel_file}")

        spec = (ROOT / "packaging/noxforge.spec").read_text(encoding="utf-8")
        self.assertIn("Requires:       kwin >= 6.8", spec)
        self.assertIn("Requires:       plasma-workspace >= 6.8", spec)
        self.assertIn("Recommends:     plasma-union", spec)

        pkgbuild = (ROOT / "packaging/arch/PKGBUILD").read_text(encoding="utf-8")
        self.assertIn("plasma-union", pkgbuild)

    def test_completion_generator_and_shell_scripts(self) -> None:
        ctl_ns = runpy.run_path(str(ROOT / "tools/noxforge-ctl"), run_name="noxforge_ctl_v19_comp")
        gen_comp = ctl_ns["generate_completion"]
        for shell in ("bash", "zsh", "fish"):
            script = gen_comp(shell)
            self.assertTrue(len(script) > 100, f"Empty completion for {shell}")
            self.assertIn("noxforge-ctl", script)
            self.assertIn("switch", script)
            self.assertIn("union", script)
            self.assertIn("kwin-csd", script)
            self.assertIn("completion", script)
            self.assertIn("obsidian", script)
            self.assertIn("rofi", script)

    def test_obsidian_and_rofi_ecosystem_themes(self) -> None:
        for rel_file in (
            "apps/obsidian/noxforge.css",
            "apps/obsidian/noxforge_obsidian.css",
            "apps/rofi/noxforge.rasi",
            "apps/rofi/noxforge_obsidian.rasi",
        ):
            path = ROOT / rel_file
            self.assertTrue(path.is_file(), f"Missing ecosystem file: {rel_file}")
            text = path.read_text(encoding="utf-8")
            self.assertIn("@noxforge-version: 19.0.0", text)

        ctl_ns = runpy.run_path(str(ROOT / "tools/noxforge-ctl"), run_name="noxforge_ctl_v19_eco_new")
        self.assertIn("obsidian", ctl_ns["SUPPORTED_ECOSYSTEM_APPS"])
        self.assertIn("rofi", ctl_ns["SUPPORTED_ECOSYSTEM_APPS"])

    def test_union_css_transitions_and_forge_notch(self) -> None:
        for style_id in ("noxforge", "noxforge-obsidian"):
            css = (ROOT / f"union/styles/{style_id}/contents/css/style.css").read_text(encoding="utf-8")
            self.assertIn("border-bottom: var(--forge-notch-size) solid var(--highlight-color);", css)
            self.assertIn("transition: background-color 140ms ease", css)
            self.assertIn("scrollbar {", css)
            self.assertIn("scrollbar-slider {", css)
            self.assertIn("tooltip {", css)


if __name__ == "__main__":
    unittest.main()
