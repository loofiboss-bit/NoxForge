# SPDX-License-Identifier: MIT
"""Automated contracts and regression tests for NoxForge v18.0.0."""

from __future__ import annotations

import json
import os
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import noxforge_core  # noqa: E402


class NoxForgeV18ContractsTests(unittest.TestCase):
    def test_v18_plan_and_tokens_schema_14(self) -> None:
        plan = ROOT / "docs/NOXFORGE_V18_PLAN.md"
        self.assertTrue(plan.is_file(), "docs/NOXFORGE_V18_PLAN.md is missing")
        text = plan.read_text(encoding="utf-8")
        self.assertIn("NoxForge 18", text)
        self.assertIn("v18.0.0", text)

        impl_plan = (ROOT / "docs/IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
        self.assertIn("NOXFORGE_V18_PLAN.md", impl_plan)

        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(version, "18.0.0")

        tokens = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))
        self.assertEqual(tokens["schemaVersion"], 14)
        self.assertEqual(tokens["version"], "18.0.0")
        self.assertIn("gtk", tokens)
        self.assertTrue(tokens["gtk"]["dynamicCssVariables"])
        self.assertTrue(tokens["gtk"]["managedUserImport"])
        self.assertEqual(tokens["gtk"]["supportedVersions"], ["3.0", "4.0"])
        self.assertIn("ecosystem", tokens)
        self.assertEqual(tokens["ecosystem"]["syncPolicy"], "stateful-reversible")
        self.assertEqual(tokens["ecosystem"]["backupSuffix"], ".noxforge.bak")
        self.assertEqual(tokens["ecosystem"]["stateFile"], "noxforge/ecosystem-state.json")

    def test_noxforge_core_shared_library_and_dynamic_stylesheet(self) -> None:
        self.assertEqual(noxforge_core.get_app_version(), "18.0.0")
        self.assertEqual(noxforge_core.hex_to_rgb_tuple("#A3FF47"), (163, 255, 71))
        ratio_g, ratio_o = noxforge_core.validate_custom_accent_contrast("#A3FF47")
        self.assertGreaterEqual(ratio_g, 4.5)
        self.assertGreaterEqual(ratio_o, 4.5)

        pal = noxforge_core.resolve_accent_palette("#22D3EE", is_obsidian=True)
        self.assertEqual(pal["accent"], "#22D3EE")
        self.assertTrue(pal["accentPressed"].startswith("#"))
        self.assertEqual(pal["accentInk"], "#000000")

        qss_graphite = noxforge_core.build_qt_stylesheet("graphite", "#A3FF47")
        self.assertIn("#0D1419", qss_graphite)
        self.assertIn("#A3FF47", qss_graphite)

        qss_obsidian = noxforge_core.build_qt_stylesheet("obsidian", "#22D3EE")
        self.assertIn("#000000", qss_obsidian)
        self.assertIn("#22D3EE", qss_obsidian)
        self.assertIn("QTableWidget", qss_obsidian)
        self.assertIn("QScrollBar:vertical", qss_obsidian)
        self.assertIn("QFrame#headerBanner", qss_obsidian)

    def test_libadwaita_deep_gtk_css_selectors(self) -> None:
        for theme_dir in ("themes/NoxForge", "themes/NoxForgeObsidian"):
            for gtk_ver in ("gtk-3.0", "gtk-4.0"):
                css = (ROOT / theme_dir / gtk_ver / "gtk.css").read_text(encoding="utf-8")
                self.assertIn(".navigation-sidebar", css)
                self.assertIn("list.boxed-list", css)
                self.assertIn("tabbar tab:checked", css)
                self.assertIn("toast", css)
                self.assertIn("popover", css)
                self.assertIn("::selection", css)

    def test_gtk_3_4_dynamic_accent_variables_and_import_chaining(self) -> None:
        for theme_dir in ("themes/NoxForge", "themes/NoxForgeObsidian"):
            for gtk_ver in ("gtk-3.0", "gtk-4.0"):
                css_path = ROOT / theme_dir / gtk_ver / "gtk.css"
                self.assertTrue(css_path.is_file(), f"Missing {css_path}")
                css = css_path.read_text(encoding="utf-8")
                self.assertIn("@define-color accent_color #A3FF47;", css)
                self.assertIn("background-color: @accent_bg_color;", css)
                self.assertIn("border-color: @accent_color;", css)
                self.assertIn("background-color: @theme_view_active;", css)
                self.assertIn("border-color: @accent_pressed_color;", css)

        ctl_ns = runpy.run_path(str(ROOT / "tools/noxforge-ctl"), run_name="noxforge_ctl_test")
        with tempfile.TemporaryDirectory(prefix="noxforge-v18-gtk-") as temp:
            temp_path = Path(temp)
            old_cfg = os.environ.get("XDG_CONFIG_HOME")
            try:
                os.environ["XDG_CONFIG_HOME"] = str(temp_path / ".config")
                gtk4_dir = temp_path / ".config/gtk-4.0"
                gtk4_dir.mkdir(parents=True, exist_ok=True)
                (gtk4_dir / "gtk.css").write_text("/* user custom rule */\nwindow { margin: 0; }\n", encoding="utf-8")

                ctl_ns["sync_gtk_config"](
                    profile="obsidian",
                    accent_hex="#22D3EE",
                    dry_run=False,
                )

                gtk3_text = (temp_path / ".config/gtk-3.0/gtk.css").read_text(encoding="utf-8")
                gtk4_text = (temp_path / ".config/gtk-4.0/gtk.css").read_text(encoding="utf-8")
                self.assertIn("/* user custom rule */", gtk4_text)
                self.assertIn("NoxForgeObsidian/gtk-4.0/gtk.css", gtk4_text)
                self.assertIn("@define-color accent_color #22D3EE;", gtk4_text)
                self.assertIn("@define-color accent_pressed_color #06B6D4;", gtk4_text)
                self.assertIn("NoxForgeObsidian/gtk-3.0/gtk.css", gtk3_text)
                self.assertIn("@define-color accent_color #22D3EE;", gtk3_text)
            finally:
                if old_cfg is None:
                    os.environ.pop("XDG_CONFIG_HOME", None)
                else:
                    os.environ["XDG_CONFIG_HOME"] = old_cfg

    def test_flatpak_override_lifecycle(self) -> None:
        ctl = ROOT / "tools/noxforge-ctl"
        with tempfile.TemporaryDirectory(prefix="noxforge-v18-flatpak-") as temp:
            env = os.environ.copy()
            env["XDG_DATA_HOME"] = str(Path(temp) / ".local/share")
            override_file = Path(env["XDG_DATA_HOME"]) / "flatpak/overrides/global"
            override_file.parent.mkdir(parents=True, exist_ok=True)
            override_file.write_text("[Context]\nfilesystems=home:ro;\n", encoding="utf-8")

            res_status = subprocess.run(
                [sys.executable, str(ctl), "flatpak", "--status", "--json"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res_status.returncode, 0)
            status_payload = json.loads(res_status.stdout)
            self.assertEqual(status_payload["status"], "not-configured")
            self.assertFalse(status_payload["enabled"])

            res_enable = subprocess.run(
                [sys.executable, str(ctl), "flatpak", "--enable", "--json"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res_enable.returncode, 0)
            enable_payload = json.loads(res_enable.stdout)
            self.assertEqual(enable_payload["status"], "enabled")
            self.assertTrue(enable_payload["enabled"])
            content = override_file.read_text(encoding="utf-8")
            self.assertIn("home:ro", content)
            self.assertIn("xdg-data/themes:ro", content)
            self.assertIn("xdg-config/gtk-3.0:ro", content)
            self.assertIn("xdg-config/gtk-4.0:ro", content)

            res_disable = subprocess.run(
                [sys.executable, str(ctl), "flatpak", "--disable", "--json"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res_disable.returncode, 0)
            disable_payload = json.loads(res_disable.stdout)
            self.assertEqual(disable_payload["status"], "disabled")
            self.assertFalse(disable_payload["enabled"])
            after_content = override_file.read_text(encoding="utf-8")
            self.assertIn("home:ro", after_content)
            self.assertNotIn("xdg-data/themes:ro", after_content)

    def test_reversible_ecosystem_engine_v2_backup_inject_and_restore(self) -> None:
        ctl_ns = runpy.run_path(str(ROOT / "tools/noxforge-ctl"), run_name="noxforge_ctl_eco_test")
        with tempfile.TemporaryDirectory(prefix="noxforge-v18-eco-") as temp:
            temp_path = Path(temp)
            cfg_home = temp_path / ".config"
            data_home = temp_path / ".local/share"
            old_cfg = os.environ.get("XDG_CONFIG_HOME")
            old_data = os.environ.get("XDG_DATA_HOME")
            old_home = os.environ.get("HOME")
            try:
                os.environ["HOME"] = str(temp_path)
                os.environ["XDG_CONFIG_HOME"] = str(cfg_home)
                os.environ["XDG_DATA_HOME"] = str(data_home)

                # Pre-existing user files
                starship_file = cfg_home / "starship.toml"
                starship_file.parent.mkdir(parents=True, exist_ok=True)
                starship_file.write_text("# original user starship\n", encoding="utf-8")

                fastfetch_file = cfg_home / "fastfetch/config.jsonc"
                fastfetch_file.parent.mkdir(parents=True, exist_ok=True)
                fastfetch_file.write_text("// original user fastfetch\n", encoding="utf-8")

                discord_file = cfg_home / "Vencord/themes/noxforge.theme.css"
                discord_file.parent.mkdir(parents=True, exist_ok=True)
                discord_file.write_text("/* original user discord */\n", encoding="utf-8")

                ff_profile = temp_path / ".mozilla/firefox/test.default-release"
                (ff_profile / "chrome").mkdir(parents=True, exist_ok=True)
                ff_chrome = ff_profile / "chrome/userChrome.css"
                ff_chrome.write_text("/* original user firefox */\n", encoding="utf-8")

                res_apply = ctl_ns["ecosystem_apply"](
                    app_names=["starship", "fastfetch", "discord", "firefox"],
                    dry_run=False,
                    profile="obsidian",
                    accent_hex="#22D3EE",
                )
                self.assertEqual(res_apply["status"], "applied")
                self.assertEqual(
                    sorted(res_apply["applied"]),
                    ["discord", "fastfetch", "firefox", "starship"],
                )

                # Verify .noxforge.bak backups exist
                self.assertTrue((cfg_home / "starship.toml.noxforge.bak").is_file())
                self.assertTrue((cfg_home / "fastfetch/config.jsonc.noxforge.bak").is_file())
                self.assertTrue((cfg_home / "Vencord/themes/noxforge.theme.css.noxforge.bak").is_file())
                self.assertTrue((ff_profile / "chrome/userChrome.css.noxforge.bak").is_file())

                # Verify active profile (obsidian #000000) and accent (#22D3EE / 34;211;238) injection
                self.assertIn("#22D3EE", starship_file.read_text(encoding="utf-8"))
                self.assertIn("34;211;238", fastfetch_file.read_text(encoding="utf-8"))
                discord_deployed = discord_file.read_text(encoding="utf-8")
                self.assertIn("#000000", discord_deployed)
                self.assertIn("#22D3EE", discord_deployed)
                ff_deployed = ff_chrome.read_text(encoding="utf-8")
                self.assertIn("#000000", ff_deployed)
                self.assertIn("#22D3EE", ff_deployed)

                # Verify ecosystem-state.json
                state_path = cfg_home / "noxforge/ecosystem-state.json"
                self.assertTrue(state_path.is_file())
                state = json.loads(state_path.read_text(encoding="utf-8"))
                self.assertEqual(
                    sorted(state["apps"].keys()),
                    ["discord", "fastfetch", "firefox", "starship"],
                )
                self.assertEqual(state["apps"]["discord"]["profile"], "obsidian")
                self.assertEqual(state["apps"]["discord"]["accent"], "#22D3EE")

                # Restore all and verify original files are restored byte-for-byte
                res_restore = ctl_ns["ecosystem_restore"](
                    app_names=["all"],
                    dry_run=False,
                )
                self.assertEqual(res_restore["status"], "restored")
                self.assertEqual(starship_file.read_text(encoding="utf-8"), "# original user starship\n")
                self.assertEqual(fastfetch_file.read_text(encoding="utf-8"), "// original user fastfetch\n")
                self.assertEqual(discord_file.read_text(encoding="utf-8"), "/* original user discord */\n")
                self.assertEqual(ff_chrome.read_text(encoding="utf-8"), "/* original user firefox */\n")
                self.assertFalse((cfg_home / "starship.toml.noxforge.bak").exists())
                state_after = json.loads(state_path.read_text(encoding="utf-8"))
                self.assertEqual(state_after["apps"], {})
            finally:
                for key, val in (("HOME", old_home), ("XDG_CONFIG_HOME", old_cfg), ("XDG_DATA_HOME", old_data)):
                    if val is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = val

    def test_control_center_v3_self_theming_and_restore_controls(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PySide6.QtWidgets import QApplication
        from tools.control_center import ControlCenterWindow

        _app = QApplication.instance() or QApplication([])
        window = ControlCenterWindow(initial_tab="ecosystem")
        self.assertEqual(window.tabs.currentIndex(), 4)
        self.assertTrue(hasattr(window.tab_eco, "btn_restore_all"))
        self.assertTrue(hasattr(window.tab_eco, "btn_flatpak_enable"))
        self.assertTrue(hasattr(window.tab_eco, "btn_flatpak_disable"))
        self.assertEqual(window.tab_eco.table.columnCount(), 5)

        window.refresh_theme(profile="obsidian", accent_hex="#A78BFA")
        self.assertIn("#000000", window.styleSheet())
        self.assertIn("#A78BFA", window.styleSheet())
        window.close()

    def test_doctor_schema_11_and_packaging_parity(self) -> None:
        doctor = ROOT / "tools/noxforge-doctor"
        with tempfile.TemporaryDirectory(prefix="noxforge-v18-doctor-") as temp:
            result = subprocess.run(
                [sys.executable, str(doctor), "--root", temp, "--json"],
                capture_output=True,
                text=True,
                check=False,
                cwd=ROOT,
            )
        report = json.loads(result.stdout)
        self.assertEqual(report["schemaVersion"], 11)
        self.assertEqual(report["noxforgeCoreStatus"], "ok")
        self.assertEqual(report["gtkChainStatus"]["status"], "ok")
        self.assertTrue(report["ecosystemState"]["reversible"])
        self.assertEqual(report["ecosystemState"]["backupSuffix"], ".noxforge.bak")

        for rel_file in (
            "CMakeLists.txt",
            "packaging/noxforge.spec",
            "scripts/install.sh",
            "scripts/uninstall.sh",
            "scripts/uninstall-system.sh",
            "scripts/build_store_packages.py",
        ):
            text = (ROOT / rel_file).read_text(encoding="utf-8")
            self.assertIn("noxforge_core.py", text, f"Missing noxforge_core.py in {rel_file}")

    def test_ecosystem_backup_idempotency_without_preexisting_files(self) -> None:
        """Applying and re-syncing ecosystem configs when no user files existed must not create fake .noxforge.bak backups."""
        ctl_ns = runpy.run_path(str(ROOT / "tools/noxforge-ctl"), run_name="noxforge_ctl_idempotency_test")
        with tempfile.TemporaryDirectory(prefix="noxforge-v18-eco-clean-") as temp:
            temp_path = Path(temp)
            cfg_home = temp_path / ".config"
            data_home = temp_path / ".local/share"
            old_cfg = os.environ.get("XDG_CONFIG_HOME")
            old_data = os.environ.get("XDG_DATA_HOME")
            old_home = os.environ.get("HOME")
            try:
                os.environ["HOME"] = str(temp_path)
                os.environ["XDG_CONFIG_HOME"] = str(cfg_home)
                os.environ["XDG_DATA_HOME"] = str(data_home)

                # Apply when NO files exist beforehand
                res1 = ctl_ns["ecosystem_apply"](
                    app_names=["starship", "fastfetch", "discord"],
                    dry_run=False,
                    profile="graphite",
                    accent_hex="#A3FF47",
                )
                self.assertEqual(res1["status"], "applied")
                self.assertFalse((cfg_home / "starship.toml.noxforge.bak").exists())
                self.assertFalse((cfg_home / "Vencord/themes/noxforge.theme.css.noxforge.bak").exists())

                # Re-sync via sync_tracked_ecosystem and a second ecosystem_apply
                ctl_ns["sync_tracked_ecosystem"](
                    profile="obsidian",
                    accent_hex="#22D3EE",
                    dry_run=False,
                )
                self.assertFalse((cfg_home / "starship.toml.noxforge.bak").exists())
                self.assertFalse((cfg_home / "Vencord/themes/noxforge.theme.css.noxforge.bak").exists())
                self.assertIn("#22D3EE", (cfg_home / "starship.toml").read_text(encoding="utf-8"))

                # Restore must remove the NoxForge-created files cleanly
                res_restore = ctl_ns["ecosystem_restore"](app_names=["all"], dry_run=False)
                self.assertEqual(res_restore["status"], "restored")
                self.assertFalse((cfg_home / "starship.toml").exists())
                self.assertFalse((cfg_home / "fastfetch/config.jsonc").exists())
                self.assertFalse((cfg_home / "Vencord/themes/noxforge.theme.css").exists())
            finally:
                for key, val in (("HOME", old_home), ("XDG_CONFIG_HOME", old_cfg), ("XDG_DATA_HOME", old_data)):
                    if val is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = val

    def test_schedule_midnight_wraparound_and_safe_quoting(self) -> None:
        self.assertEqual(noxforge_core.evaluate_schedule_profile("12:00", "07:00", "20:00"), "graphite")
        self.assertEqual(noxforge_core.evaluate_schedule_profile("22:00", "07:00", "20:00"), "obsidian")
        self.assertEqual(noxforge_core.evaluate_schedule_profile("03:00", "07:00", "20:00"), "obsidian")
        # Wrap-around schedule (e.g. night shift day mode 22:00 -> 06:00)
        self.assertEqual(noxforge_core.evaluate_schedule_profile("23:00", "22:00", "06:00"), "graphite")
        self.assertEqual(noxforge_core.evaluate_schedule_profile("02:00", "22:00", "06:00"), "graphite")
        self.assertEqual(noxforge_core.evaluate_schedule_profile("14:00", "22:00", "06:00"), "obsidian")

        ctl_ns = runpy.run_path(str(ROOT / "tools/noxforge-ctl"), run_name="noxforge_ctl_sched_test")
        with tempfile.TemporaryDirectory(prefix="noxforge-v18-sched-") as temp:
            old_cfg = os.environ.get("XDG_CONFIG_HOME")
            try:
                os.environ["XDG_CONFIG_HOME"] = str(Path(temp) / ".config")
                res = ctl_ns["manage_schedule"](
                    action="enable",
                    day_time="07:30",
                    night_time="20:30",
                    dry_run=False,
                )
                self.assertEqual(res["status"], "enabled")
                svc_file = Path(temp) / ".config/systemd/user/noxforge-daynight.service"
                self.assertTrue(svc_file.is_file())
                svc_text = svc_file.read_text(encoding="utf-8")
                self.assertIn("--apply-now --day-time 07:30 --night-time 20:30", svc_text)
                self.assertIn('"', svc_text)
            finally:
                if old_cfg is None:
                    os.environ.pop("XDG_CONFIG_HOME", None)
                else:
                    os.environ["XDG_CONFIG_HOME"] = old_cfg

    def test_motion_wallpaper_and_preset_export_import(self) -> None:
        ctl_ns = runpy.run_path(str(ROOT / "tools/noxforge-ctl"), run_name="noxforge_ctl_features_test")
        with tempfile.TemporaryDirectory(prefix="noxforge-v18-feat-") as temp:
            temp_path = Path(temp)
            old_cfg = os.environ.get("XDG_CONFIG_HOME")
            old_data = os.environ.get("XDG_DATA_HOME")
            try:
                os.environ["XDG_CONFIG_HOME"] = str(temp_path / ".config")
                os.environ["XDG_DATA_HOME"] = str(temp_path / ".local/share")

                # Motion dry-run and status check
                st_motion = ctl_ns["manage_motion"](action="status", dry_run=True)
                self.assertIn("reducedMotion", st_motion)
                red_motion = ctl_ns["manage_motion"](action="reduced", dry_run=True)
                self.assertTrue(red_motion["reducedMotion"])
                std_motion = ctl_ns["manage_motion"](action="standard", dry_run=True)
                self.assertFalse(std_motion["reducedMotion"])

                # Wallpaper listing and dry-run apply
                wp_list = ctl_ns["manage_wallpaper"](variant="list", dry_run=True)
                self.assertEqual(wp_list["status"], "ok")
                self.assertIn("ultrawide", wp_list["variants"])
                wp_apply = ctl_ns["manage_wallpaper"](variant="obsidian", dry_run=True)
                self.assertEqual(wp_apply["status"], "dry-run")
                self.assertEqual(wp_apply["variant"], "obsidian")

                # Preset export and dry-run import
                preset_file = temp_path / "my-preset.json"
                exp = ctl_ns["export_preset"](file_path=str(preset_file))
                self.assertEqual(exp["schemaVersion"], 1)
                self.assertTrue(preset_file.is_file())

                imp = ctl_ns["import_preset"](file_path=str(preset_file), dry_run=True)
                self.assertEqual(imp["status"], "dry-run")
                self.assertIn(imp["profile"], ("graphite", "obsidian"))
            finally:
                for key, val in (("XDG_CONFIG_HOME", old_cfg), ("XDG_DATA_HOME", old_data)):
                    if val is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = val


if __name__ == "__main__":
    unittest.main()
