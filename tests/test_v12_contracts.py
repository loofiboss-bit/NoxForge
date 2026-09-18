# SPDX-License-Identifier: MIT
"""Automated contracts and regression tests for NoxForge v12 Ecosystem Parity."""

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


def hex_to_rgb(hex_code: str) -> tuple[int, int, int]:
    clean = hex_code.lstrip("#")
    return int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16)


def relative_luminance(r: int, g: int, b: int) -> float:
    channels = [c / 255.0 for c in (r, g, b)]
    linear = [
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        for c in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
    l1 = relative_luminance(*c1)
    l2 = relative_luminance(*c2)
    light, dark = max(l1, l2), min(l1, l2)
    return (light + 0.05) / (dark + 0.05)


class NoxForgeV12ContractsTests(unittest.TestCase):
    def test_v12_plan_is_present_and_indexed(self) -> None:
        plan = ROOT / "docs/NOXFORGE_V12_PLAN.md"
        self.assertTrue(plan.is_file())
        text = plan.read_text(encoding="utf-8")
        self.assertIn("NoxForge 12", text)
        self.assertIn("Ecosystem & App Parity", text)

        impl_plan = (ROOT / "docs/IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
        self.assertIn("NOXFORGE_V12_PLAN.md", impl_plan)

    def test_system_uninstall_accepts_v12_manifest_entries(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noxforge-v12-uninstall-") as temp:
            root = Path(temp)
            build = root / "build"
            stage = root / "stage"
            entries = (
                "/usr/share/themes/NoxForge/gtk-3.0/gtk.css",
                "/usr/share/themes/NoxForgeObsidian/gtk-4.0/gtk.css",
                "/usr/share/org.kde.syntax-highlighting/themes/NoxForge.theme",
                "/usr/share/org.kde.syntax-highlighting/themes/NoxForgeObsidian.theme",
                "/usr/share/noxforge/terminals/ghostty/noxforge",
                "/usr/share/noxforge/editors/vscode/package.json",
            )
            manifest = build / "install_manifest.txt"
            manifest.parent.mkdir(parents=True)
            manifest.write_text("\n".join(entries) + "\n", encoding="utf-8")
            for entry in entries:
                target = stage / entry.lstrip("/")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("owned\n", encoding="utf-8")

            environment = dict(
                os.environ,
                NOXFORGE_BUILD_ROOT=str(build),
                NOXFORGE_SYSTEM_ROOT=str(stage),
            )
            result = subprocess.run(
                [str(ROOT / "scripts/uninstall-system.sh"), "--system"],
                cwd=ROOT,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for entry in entries:
                self.assertFalse((stage / entry.lstrip("/")).exists(), entry)

    def test_schema_8_tokens_and_syntax_contract(self) -> None:
        tokens = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))
        self.assertEqual(tokens["schemaVersion"], 8)
        self.assertEqual(tokens["version"], (ROOT / "VERSION").read_text(encoding="utf-8").strip())
        self.assertIn("syntax", tokens)
        self.assertEqual(set(tokens["syntax"]), {"standard", "obsidian"})

        required_syntax = {
            "keyword",
            "function",
            "string",
            "type",
            "number",
            "comment",
            "operator",
            "variable",
            "error",
        }
        for variant in ("standard", "obsidian"):
            self.assertEqual(set(tokens["syntax"][variant]), required_syntax)

    def test_syntax_tokens_wcag_contrast(self) -> None:
        tokens = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))
        standard_bg = hex_to_rgb(tokens["colors"]["background"])
        obsidian_bg = hex_to_rgb(tokens["variants"]["obsidian"]["background"])

        for variant, bg in (("standard", standard_bg), ("obsidian", obsidian_bg)):
            for role, color_hex in tokens["syntax"][variant].items():
                rgb = hex_to_rgb(color_hex)
                ratio = contrast(rgb, bg)
                self.assertGreaterEqual(
                    ratio,
                    4.5,
                    f"Syntax token {variant}.{role} ({color_hex}) failed WCAG AA against background {bg} (ratio: {ratio:.2f})",
                )

    def test_gtk_themes_structure_and_styling(self) -> None:
        for theme, bg_hex, text_hex in (
            ("NoxForge", "#0D1419", "#E8F0F2"),
            ("NoxForgeObsidian", "#000000", "#E8F0F2"),
        ):
            theme_dir = ROOT / "themes" / theme
            self.assertTrue(theme_dir.is_dir(), f"{theme} dir missing")

            index_theme = theme_dir / "index.theme"
            self.assertTrue(index_theme.is_file())
            index_content = index_theme.read_text(encoding="utf-8")
            self.assertIn(f"Name={theme}", index_content)
            self.assertIn("GtkTheme=", index_content)

            for gtk_ver in ("gtk-3.0", "gtk-4.0"):
                css_file = theme_dir / gtk_ver / "gtk.css"
                self.assertTrue(css_file.is_file(), f"{css_file} missing")
                css_content = css_file.read_text(encoding="utf-8")
                self.assertIn(f"@define-color window_bg_color {bg_hex};", css_content)
                self.assertIn(f"@define-color window_fg_color {text_hex};", css_content)
                self.assertIn("@define-color accent_color #A3FF47;", css_content)
                self.assertIn("headerbar", css_content)
                self.assertIn("button", css_content)
                self.assertIn("entry", css_content)

    def test_kate_syntax_themes(self) -> None:
        for name in ("NoxForge", "NoxForgeObsidian"):
            path = ROOT / "syntax/kate" / f"{name}.theme"
            self.assertTrue(path.is_file(), f"{path} missing")
            data = json.loads(path.read_text(encoding="utf-8"))

            self.assertIn("metadata", data)
            self.assertEqual(data["metadata"]["name"], name)
            self.assertEqual(data["metadata"]["revision"], 1)

            text_styles = data.get("text-styles", {})
            self.assertEqual(text_styles["Keyword"]["selected-text-color"], "#A3FF47")
            self.assertEqual(text_styles["String"]["selected-text-color"], "#22D3EE")
            self.assertEqual(text_styles["DataType"]["selected-text-color"], "#A78BFA")
            self.assertEqual(text_styles["DecVal"]["selected-text-color"], "#FBBF24")
            self.assertEqual(text_styles["Comment"]["selected-text-color"], "#748289")
            self.assertEqual(text_styles["Error"]["selected-text-color"], "#FF6B7A")

    def test_vscode_extension_and_themes(self) -> None:
        pkg_path = ROOT / "editors/vscode/package.json"
        self.assertTrue(pkg_path.is_file())
        pkg = json.loads(pkg_path.read_text(encoding="utf-8"))

        self.assertEqual(pkg["name"], "noxforge-theme")
        self.assertEqual(pkg["version"], (ROOT / "VERSION").read_text(encoding="utf-8").strip())
        themes = pkg.get("contributes", {}).get("themes", [])
        self.assertEqual(len(themes), 2)

        for entry in themes:
            theme_file = ROOT / "editors/vscode" / entry["path"].lstrip("./")
            self.assertTrue(theme_file.is_file(), f"{theme_file} missing")
            theme_data = json.loads(theme_file.read_text(encoding="utf-8"))
            self.assertEqual(theme_data["name"], entry["label"])
            self.assertIn("colors", theme_data)
            self.assertIn("tokenColors", theme_data)
            self.assertIn("editor.background", theme_data["colors"])
            self.assertIn("editor.foreground", theme_data["colors"])

    def test_vscode_generator_uses_token_version(self) -> None:
        generator = runpy.run_path(
            str(ROOT / "scripts/generate_design_system.py"),
            run_name="noxforge_generate_design_system_test",
        )
        package = json.loads(generator["vscode_package_json"]({"version": "99.1.2"}))
        self.assertEqual(package["version"], "99.1.2")

    def test_terminal_themes(self) -> None:
        # Ghostty
        for variant in ("noxforge", "noxforge-obsidian"):
            path = ROOT / f"terminals/ghostty/{variant}"
            self.assertTrue(path.is_file(), f"{path} missing")
            content = path.read_text(encoding="utf-8")
            self.assertIn("background = ", content)
            self.assertIn("foreground = #E8F0F2", content)
            self.assertIn("cursor-color = #A3FF47", content)

        # Alacritty
        for variant in ("noxforge", "noxforge-obsidian"):
            path = ROOT / f"terminals/alacritty/{variant}.toml"
            self.assertTrue(path.is_file(), f"{path} missing")
            content = path.read_text(encoding="utf-8")
            self.assertIn("[colors.primary]", content)
            self.assertIn("[colors.normal]", content)
            self.assertIn("[colors.bright]", content)

        # Kitty
        for variant in ("noxforge", "noxforge-obsidian"):
            path = ROOT / f"terminals/kitty/{variant}.conf"
            self.assertTrue(path.is_file(), f"{path} missing")
            content = path.read_text(encoding="utf-8")
            self.assertIn("foreground #E8F0F2", content)
            self.assertIn("cursor #A3FF47", content)

        # Foot
        for variant in ("noxforge", "noxforge-obsidian"):
            path = ROOT / f"terminals/foot/{variant}.ini"
            self.assertTrue(path.is_file(), f"{path} missing")
            content = path.read_text(encoding="utf-8")
            self.assertIn("[colors]", content)
            self.assertIn("foreground=E8F0F2", content)
            self.assertIn("regular2=A3FF47", content)

    def test_doctor_schema_5_and_ecosystem_inspection(self) -> None:
        doctor = ROOT / "tools/noxforge-doctor"
        with tempfile.TemporaryDirectory(prefix="noxforge-v12-doctor-") as temp:
            result = subprocess.run(
                [sys.executable, str(doctor), "--root", temp, "--json"],
                capture_output=True,
                text=True,
                check=False,
                cwd=ROOT,
            )
        report = json.loads(result.stdout)
        self.assertEqual(report["schemaVersion"], 5)
        self.assertIn("ecosystem", report)
        self.assertIn("flatpakThemesOverride", report["ecosystem"])
        self.assertIn("gtk-theme", report["missing"])
        self.assertIn("gtk-theme-obsidian", report["missing"])
        self.assertIn("syntax-theme", report["missing"])
        self.assertIn("syntax-theme-obsidian", report["missing"])

    def test_doctor_requires_all_v12_terminal_variants(self) -> None:
        doctor = runpy.run_path(
            str(ROOT / "tools/noxforge-doctor"),
            run_name="noxforge_doctor_v12_test",
        )
        with tempfile.TemporaryDirectory(prefix="noxforge-v12-terminals-") as temp:
            root = Path(temp)
            (root / "noxforge").mkdir()
            (root / "noxforge/manifest.json").write_text("{}\n", encoding="utf-8")
            for name in doctor["PORTABLE_REQUIRED"]:
                marker = doctor["component_path"](root, doctor["COMPONENTS"][name])
                marker.parent.mkdir(parents=True, exist_ok=True)
                marker.write_text("present\n", encoding="utf-8")

            complete = doctor["build_report"](root)
            self.assertEqual(complete["status"], "ok")
            for name in (
                "terminal-ghostty",
                "terminal-alacritty",
                "terminal-kitty",
                "terminal-foot",
            ):
                marker = doctor["component_path"](root, doctor["COMPONENTS"][name])
                marker.unlink()

            partial = doctor["build_report"](root)
        self.assertEqual(partial["status"], "incomplete")
        self.assertEqual(
            partial["missing"],
            [
                "terminal-alacritty",
                "terminal-foot",
                "terminal-ghostty",
                "terminal-kitty",
            ],
        )

    def test_doctor_remediation_plan_includes_flatpak_guidance(self) -> None:
        doctor = ROOT / "tools/noxforge-doctor"
        with tempfile.TemporaryDirectory(prefix="noxforge-v12-remediation-") as temp:
            result = subprocess.run(
                [sys.executable, str(doctor), "--root", temp, "--remediation-plan"],
                capture_output=True,
                text=True,
                check=False,
                cwd=ROOT,
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("#!/usr/bin/env bash", result.stdout)
        self.assertIn("flatpak override --user --filesystem=xdg-data/themes:ro", result.stdout)

    def test_build_system_installs_v12_assets(self) -> None:
        cmake = (ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
        self.assertIn("themes/NoxForge/", cmake)
        self.assertIn("themes/NoxForgeObsidian/", cmake)
        self.assertIn("syntax/kate/NoxForge.theme", cmake)
        self.assertIn("terminals/", cmake)
        self.assertIn("editors/vscode/", cmake)

        spec = (ROOT / "packaging/noxforge.spec").read_text(encoding="utf-8")
        self.assertIn("%{_datadir}/themes/NoxForge/", spec)
        self.assertIn("%{_datadir}/themes/NoxForgeObsidian/", spec)
        self.assertIn("%{_datadir}/org.kde.syntax-highlighting/themes/NoxForge.theme", spec)
        self.assertIn("%{_datadir}/noxforge/terminals/", spec)
        self.assertIn("%{_datadir}/noxforge/editors/", spec)

        pkgbuild = (ROOT / "packaging/arch/PKGBUILD").read_text(encoding="utf-8")
        self.assertIn(f"pkgver={(ROOT / 'VERSION').read_text().strip()}", pkgbuild)

    def test_install_and_uninstall_scripts_handle_v12_assets(self) -> None:
        install_sh = (ROOT / "scripts/install.sh").read_text(encoding="utf-8")
        uninstall_sh = (ROOT / "scripts/uninstall.sh").read_text(encoding="utf-8")

        for relative in (
            "themes/NoxForge",
            "themes/NoxForgeObsidian",
            "syntax/kate",
            "terminals",
            "editors/vscode",
        ):
            self.assertIn(relative, install_sh)

        for uninst_target in (
            "themes/NoxForge",
            "themes/NoxForgeObsidian",
            "org.kde.syntax-highlighting/themes/NoxForge.theme",
            "noxforge/terminals",
            "noxforge/editors",
        ):
            self.assertIn(uninst_target, uninstall_sh)

        # Confirm non-applying boundary
        for forbidden in ("plasma-apply-", "kwriteconfig", "gsettings set"):
            self.assertNotIn(forbidden, install_sh)

    def test_portable_archive_contains_all_v12_assets(self) -> None:
        import tarfile
        from scripts import build_store_packages as builder
        from scripts import validate_store_packages as validator

        manifest = builder.load_manifest()
        with tempfile.TemporaryDirectory(prefix="noxforge-v12-portable-") as temp:
            output = Path(temp)
            builder.build_all(output, manifest)
            archive = output / next(
                item["filename"] for item in manifest["artifacts"] if item["key"] == "portable"
            )
            validator.validate_archive(archive, "portable", manifest)
            with tarfile.open(archive, "r:*") as handle:
                names = {member.name for member in handle.getmembers()}
        for required in (
            "noxforge/components/themes/NoxForge/gtk-3.0/gtk.css",
            "noxforge/components/themes/NoxForgeObsidian/gtk-4.0/gtk.css",
            "noxforge/components/syntax/NoxForge.theme",
            "noxforge/components/syntax/NoxForgeObsidian.theme",
            "noxforge/components/terminals/ghostty/noxforge",
            "noxforge/components/terminals/alacritty/noxforge.toml",
            "noxforge/components/terminals/kitty/noxforge.conf",
            "noxforge/components/terminals/foot/noxforge.ini",
            "noxforge/components/editors/vscode/package.json",
        ):
            self.assertIn(required, names)


if __name__ == "__main__":
    unittest.main()
