from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import tempfile
import unittest
import subprocess
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load_doctor():
    loader = importlib.machinery.SourceFileLoader(
        "noxforge_doctor_v9", str(ROOT / "tools/noxforge-doctor")
    )
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


DOCTOR = load_doctor()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class V9ContractTests(unittest.TestCase):
    def test_manifest_models_fedora_plm_and_arch_sddm(self) -> None:
        manifest = json.loads(
            (ROOT / "distribution/release-manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["schemaVersion"], 2)
        self.assertEqual(manifest["release"]["version"], "9.0.0")
        managers = manifest["compatibility"]["loginManagers"]
        self.assertEqual(managers["fedora44"]["default"], "plasmalogin")
        self.assertEqual(managers["fedora44"]["integrations"]["plasmalogin"], "wallpaper")
        self.assertEqual(managers["arch"]["qualified"], "sddm")

    def test_dolphin_and_system_settings_have_physical_optical_icons(self) -> None:
        coverage = json.loads(
            (ROOT / "icons/NoxForge/coverage.json").read_text(encoding="utf-8")
        )
        self.assertEqual(coverage["opticalStrokeWidths"], {"16": 1.9, "22": 1.75})
        for size in (16, 22):
            for relative in (
                "places/folder.svg",
                "places/user-home.svg",
                "preferences/preferences-desktop-theme.svg",
                "preferences/preferences-system-network.svg",
            ):
                path = ROOT / f"icons/NoxForge/{size}x{size}" / relative
                self.assertTrue(path.is_file(), path)
                self.assertIn(f'width="{size}" height="{size}"', path.read_text(encoding="utf-8"))

    def test_plm_configuration_uses_defaults_main_and_sorted_dropin_precedence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noxforge-v9-plm-config-") as name:
            root = Path(name)
            section = "[Greeter][Wallpaper][org.kde.image][General]\n"
            write(root / "usr/lib/plasmalogin/defaults.conf", section + "Image=file:///default\n")
            write(root / "etc/plasmalogin.conf", section + "Image=file:///main\n")
            write(root / "etc/plasmalogin.conf.d/10-site.conf", section + "Image=file:///site\n")
            write(
                root / "etc/plasmalogin.conf.d/90-noxforge.conf",
                section + "Image=file:///usr/share/wallpapers/NoxForge-Quiet/\n",
            )
            self.assertEqual(
                DOCTOR.configured_plm_wallpaper(root),
                "file:///usr/share/wallpapers/NoxForge-Quiet/",
            )

    def test_incomplete_plm_configuration_is_safe(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noxforge-v9-plm-incomplete-") as name:
            root = Path(name)
            write(root / "etc/plasmalogin.conf", "[Greeter]\nWallpaperPlugin=org.kde.image\n")
            self.assertIsNone(DOCTOR.configured_plm_wallpaper(root))

    def test_active_plm_does_not_promote_installed_sddm_theme(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noxforge-v9-plm-report-") as name:
            root = Path(name)
            write(root / "usr/share/wallpapers/NoxForge-Quiet/metadata.json", "{}\n")
            write(
                root / "etc/plasmalogin.conf",
                "[Greeter][Wallpaper][org.kde.image][General]\n"
                "Image=file:///usr/share/wallpapers/NoxForge-Quiet/\n",
            )
            components = {"sddm": {"found": True}}
            globals_dict = DOCTOR.login_surface_report.__globals__
            with mock.patch.dict(
                globals_dict,
                {"display_manager_state": lambda _root: ("plasmalogin", "active")},
            ):
                report = DOCTOR.login_surface_report(root, components)
            self.assertEqual(report["manager"], "plasmalogin")
            self.assertEqual(report["integration"], "wallpaper")
            self.assertEqual(report["asset"], "NoxForge-Quiet")
            self.assertTrue(report["selected"])
            self.assertEqual(report["status"], "selected")

    def test_active_sddm_reports_custom_theme_only_when_selected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noxforge-v9-sddm-report-") as name:
            root = Path(name)
            write(root / "etc/sddm.conf.d/90-theme.conf", "[Theme]\nCurrent=NoxForge\n")
            components = {"sddm": {"found": True}}
            globals_dict = DOCTOR.login_surface_report.__globals__
            with mock.patch.dict(
                globals_dict,
                {"display_manager_state": lambda _root: ("sddm", "active")},
            ):
                report = DOCTOR.login_surface_report(root, components)
            self.assertEqual(report["integration"], "custom-theme")
            self.assertTrue(report["available"])
            self.assertTrue(report["selected"])

    def test_other_absent_and_staged_manager_states_are_stable(self) -> None:
        components = {"sddm": {"found": False}}
        for state, expected_status in (
            (("other", "active"), "not-integrated"),
            (("not-detected", "inactive"), "not-integrated"),
            (("not-detected", "not-applicable"), "not-applicable"),
        ):
            globals_dict = DOCTOR.login_surface_report.__globals__
            with mock.patch.dict(globals_dict, {"display_manager_state": lambda _root, value=state: value}):
                report = DOCTOR.login_surface_report(Path("/staged"), components)
            self.assertEqual(report["status"], expected_status)

    def test_systemd_timeouts_return_unknown_without_blocking_report(self) -> None:
        with mock.patch.object(
            DOCTOR.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(["systemctl"], 2),
        ), mock.patch.object(Path, "resolve", side_effect=OSError):
            manager, state = DOCTOR.display_manager_state(Path("/"))
        self.assertEqual(manager, "not-detected")
        self.assertEqual(state, "unknown")

    def test_installers_do_not_mutate_login_or_desktop_configuration(self) -> None:
        combined = "\n".join(
            (ROOT / relative).read_text(encoding="utf-8")
            for relative in (
                "scripts/install.sh",
                "scripts/uninstall.sh",
                "scripts/install-system.sh",
                "scripts/uninstall-system.sh",
            )
        )
        for forbidden in (
            "systemctl enable",
            "systemctl disable",
            "plasmalogin.conf",
            "sddm.conf",
            "plasma-org.kde.plasma.desktop-appletsrc",
            "kwinrc",
            "kdeglobals",
        ):
            self.assertNotIn(forbidden, combined)

    def test_complete_scale_matrix_includes_150_and_175_percent(self) -> None:
        cmake = (ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
        renderer = (ROOT / "scripts/render_evidence.py").read_text(encoding="utf-8")
        self.assertIn("1.0 1.25 1.4 1.5 1.75 2.0", cmake)
        self.assertIn('(\"150\", \"1.5\")', renderer)
        self.assertIn('(\"175\", \"1.75\")', renderer)

    def test_migration_gate_covers_every_preserved_configuration(self) -> None:
        source = (ROOT / "scripts/check_v9_migration.py").read_text(encoding="utf-8")
        release_gate = (ROOT / "scripts/release-check.py").read_text(encoding="utf-8")
        for marker in (
            "kdeglobals",
            "plasma-org.kde.plasma.desktop-appletsrc",
            "plasmawallpaperrc",
            "plasmalogin.conf",
            "sddm.conf.d",
        ):
            self.assertIn(marker, source)
        self.assertIn("check_v9_migration.py", release_gate)
        self.assertIn('\"-DCMAKE_INSTALL_PREFIX=/usr\"', release_gate)


if __name__ == "__main__":
    unittest.main()
