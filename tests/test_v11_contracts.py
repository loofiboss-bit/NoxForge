# SPDX-License-Identifier: MIT
"""Automated contracts and regression tests for NoxForge v11."""

from __future__ import annotations

import configparser
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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


def parse_rgb(text: str) -> tuple[int, int, int]:
    parts = [int(p.strip()) for p in text.split(",")]
    assert len(parts) == 3
    return parts[0], parts[1], parts[2]


class NoxForgeV11ContractsTests(unittest.TestCase):
    def test_v11_plan_is_present(self) -> None:
        plan = ROOT / "docs/NOXFORGE_V11_PLAN.md"
        self.assertTrue(plan.is_file())
        text = plan.read_text(encoding="utf-8")
        self.assertIn("NoxForge 11", text)
        self.assertIn("Deep Focus & System Completeness", text)

    def test_qt6_style_implements_v11_primitives(self) -> None:
        source = (ROOT / "src/style/noxforgestyle.cpp").read_text(encoding="utf-8")
        for symbol in (
            "PE_IndicatorBranch",
            "PE_FrameTabWidget",
            "PE_FrameDockWidget",
            "PE_PanelStatusBar",
            "PE_FrameStatusBarItem",
            "CE_Splitter",
        ):
            self.assertIn(symbol, source)

    def test_obsidian_color_scheme_passes_contrast(self) -> None:
        path = ROOT / "color-schemes/NoxForgeObsidian.colors"
        self.assertTrue(path.is_file())
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(path, encoding="utf-8")

        self.assertEqual(parser["General"]["ColorScheme"], "NoxForgeObsidian")
        canvas_bg = parse_rgb(parser["Colors:View"]["BackgroundNormal"])
        self.assertEqual(canvas_bg, (0, 0, 0))  # True black OLED canvas

        text_primary = parse_rgb(parser["Colors:View"]["ForegroundNormal"])
        accent = parse_rgb(parser["Colors:View"]["DecorationFocus"])
        text_secondary = parse_rgb(parser["Colors:View"]["ForegroundInactive"])

        # Contrast requirements
        self.assertGreaterEqual(contrast(text_primary, canvas_bg), 7.0)
        self.assertGreaterEqual(contrast(accent, canvas_bg), 7.0)
        self.assertGreaterEqual(contrast(text_secondary, canvas_bg), 4.5)

    def test_v11_tokens_are_the_authority_for_variants_and_terminal_colors(self) -> None:
        tokens = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))
        self.assertEqual(tokens["schemaVersion"], 7)
        self.assertEqual(tokens["variants"]["obsidian"]["background"], "#000000")
        self.assertEqual(tokens["terminal"]["ansi"]["black"]["normal"], "#A6B4B9")
        self.assertEqual(
            set(tokens["terminal"]["ansi"]),
            {"black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"},
        )

    def test_konsole_color_schemes(self) -> None:
        for name in ("NoxForge", "NoxForgeObsidian"):
            path = ROOT / f"konsole/{name}.colorscheme"
            self.assertTrue(path.is_file(), f"{path} is missing")
            parser = configparser.ConfigParser(interpolation=None)
            parser.read(path, encoding="utf-8")

            self.assertIn("General", parser)
            self.assertIn("Background", parser)
            self.assertIn("Foreground", parser)

            bg = parse_rgb(parser["Background"]["Color"])
            fg = parse_rgb(parser["Foreground"]["Color"])
            self.assertGreaterEqual(contrast(fg, bg), 7.0)

            # Check all ANSI normal, faint, and intense definitions.
            for i in range(8):
                for suffix in ("", "Faint", "Intense"):
                    section = f"Color{i}{suffix}"
                    self.assertIn(section, parser)
                    color = parse_rgb(parser[section]["Color"])
                    self.assertGreaterEqual(contrast(color, bg), 4.5, section)

    def test_doctor_remediation_plan(self) -> None:
        doctor = ROOT / "tools/noxforge-doctor"
        with tempfile.TemporaryDirectory(prefix="noxforge-v11-remediation-") as temp:
            result = subprocess.run(
                [sys.executable, str(doctor), "--root", temp, "--remediation-plan"],
                capture_output=True,
                text=True,
                check=False,
                cwd=ROOT,
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("#!/usr/bin/env bash", result.stdout)
        self.assertIn("remediation plan", result.stdout.lower())

    def test_doctor_reports_schema_four_and_terminal_completeness(self) -> None:
        doctor = ROOT / "tools/noxforge-doctor"
        with tempfile.TemporaryDirectory(prefix="noxforge-v11-doctor-") as temp:
            result = subprocess.run(
                [sys.executable, str(doctor), "--root", temp, "--json"],
                capture_output=True,
                text=True,
                check=False,
                cwd=ROOT,
            )
        report = json.loads(result.stdout)
        self.assertEqual(report["schemaVersion"], 4)
        self.assertIn("terminal-theme", report["missing"])
        self.assertIn("terminal-theme-obsidian", report["missing"])

    def test_build_system_installs_v11_assets(self) -> None:
        cmake = (ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
        self.assertIn("color-schemes/NoxForgeObsidian.colors", cmake)
        self.assertIn("konsole/NoxForge.colorscheme", cmake)
        self.assertIn("konsole/NoxForgeObsidian.colorscheme", cmake)

        spec = (ROOT / "packaging/noxforge.spec").read_text(encoding="utf-8")
        self.assertIn("color-schemes/NoxForgeObsidian.colors", spec)
        self.assertIn("konsole/NoxForge.colorscheme", spec)
        self.assertIn("konsole/NoxForgeObsidian.colorscheme", spec)

    def test_portable_archive_contains_all_v11_assets(self) -> None:
        from scripts import build_store_packages as builder
        from scripts import validate_store_packages as validator

        manifest = builder.load_manifest()
        with tempfile.TemporaryDirectory(prefix="noxforge-v11-portable-") as temp:
            output = Path(temp)
            builder.build_all(output, manifest)
            archive = output / next(
                item["filename"] for item in manifest["artifacts"] if item["key"] == "portable"
            )
            validator.validate_archive(archive, "portable", manifest)
            with tarfile.open(archive, "r:*") as handle:
                names = {member.name for member in handle.getmembers()}
        for required in (
            "noxforge/components/colors/NoxForgeObsidian.colors",
            "noxforge/components/konsole/NoxForge.colorscheme",
            "noxforge/components/konsole/NoxForgeObsidian.colorscheme",
        ):
            self.assertIn(required, names)


if __name__ == "__main__":
    unittest.main()
