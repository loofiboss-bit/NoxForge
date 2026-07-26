from __future__ import annotations

import configparser
import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME_ID = "io.github.loofiboss.noxforge.desktop"
SPEC = importlib.util.spec_from_file_location("noxforge_validate", ROOT / "scripts/validate.py")
assert SPEC and SPEC.loader
VALIDATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATE)

QML_TOKEN_CONSUMERS = (
    ROOT / f"look-and-feel/{THEME_ID}/contents/splash/Tokens.qml",
    ROOT / f"look-and-feel/{THEME_ID}/contents/logout/Tokens.qml",
    ROOT / f"kwin/tabbox/{THEME_ID}/contents/ui/Tokens.qml",
    ROOT / "sddm/NoxForge/Tokens.qml",
)


def relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(first: str, second: str) -> float:
    light, dark = sorted(
        (relative_luminance(first), relative_luminance(second)),
        reverse=True,
    )
    return (light + 0.05) / (dark + 0.05)


class PhaseOneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tokens = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))

    def test_repository_validation(self) -> None:
        VALIDATE.validate()

    def test_schema_v4_preserves_anchors_and_grid(self) -> None:
        self.assertEqual(self.tokens["schemaVersion"], 4)
        self.assertEqual(self.tokens["colors"]["background"], "#0E1318")
        self.assertEqual(self.tokens["colors"]["accent"], "#A3FF47")
        geometry = self.tokens["geometry"]
        self.assertEqual(geometry["forgeNotch"], 4)
        self.assertEqual(geometry["compactSpacing"], 4)
        self.assertEqual(geometry["standardSpacing"], 8)
        self.assertEqual(geometry["controlHeight"] % 4, 0)
        self.assertEqual(geometry["largeControlHeight"] % 4, 0)

    def test_complete_interaction_hierarchy_and_references(self) -> None:
        hierarchy = self.tokens["states"]["hierarchy"]
        self.assertEqual(
            set(hierarchy),
            {
                "default",
                "hover",
                "focus",
                "pressed",
                "checked",
                "selected",
                "disabled",
                "busy",
                "error",
                "success",
            },
        )
        for state in hierarchy.values():
            self.assertIn(state["role"], self.tokens["semanticRoles"])
            self.assertIn(state["opacity"], self.tokens["opacity"])
            self.assertIn(state["elevation"], self.tokens["elevation"])
            self.assertIn(state["overlay"], self.tokens["overlay"])
        self.assertEqual(hierarchy["focus"]["indicator"], "singleFocusRing")
        self.assertEqual(hierarchy["selected"]["indicator"], "leadingMarker")
        self.assertEqual(self.tokens["motion"]["reducedMotion"]["durationMs"], 0)
        self.assertFalse(self.tokens["motion"]["reducedMotion"]["spatialMotion"])

    def test_every_semantic_pair_is_documented_and_passes_contrast(self) -> None:
        colors = self.tokens["colors"]
        documented = {
            (pair["foreground"], pair["background"]): pair
            for pair in self.tokens["contrastPairs"]
        }
        design = (ROOT / "DESIGN.md").read_text(encoding="utf-8")
        for role in self.tokens["semanticRoles"].values():
            key = (role["foreground"], role["background"])
            self.assertIn(key, documented)
        for pair in self.tokens["contrastPairs"]:
            self.assertIn(f"`{pair['name']}`", design)
            self.assertGreaterEqual(
                contrast(colors[pair["foreground"]], colors[pair["background"]]),
                pair["minimumRatio"],
                pair["name"],
            )

    def test_generated_token_consumers_have_exact_schema_parity(self) -> None:
        expected = self.tokens
        cpp = (ROOT / "src/style/noxforgepalette.h").read_text(encoding="utf-8")
        cpp_match = re.search(r'R"noxforge\((\{.*\})\)noxforge"', cpp)
        self.assertIsNotNone(cpp_match)
        assert cpp_match
        self.assertEqual(json.loads(cpp_match.group(1)), expected)
        for path in QML_TOKEN_CONSUMERS:
            qml = path.read_text(encoding="utf-8")
            qml_match = re.search(r"canonicalTokensJson: '(\{.*\})'", qml)
            self.assertIsNotNone(qml_match, path)
            assert qml_match
            self.assertEqual(json.loads(qml_match.group(1)), expected, path)

    def test_generator_has_zero_drift(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/generate_design_system.py", "--check"],
            cwd=ROOT,
            check=True,
        )

    def test_hallmark_scores_meet_phase_floor(self) -> None:
        scores = self.tokens["hallmark"]
        self.assertEqual(
            set(scores),
            {
                "philosophy",
                "hierarchy",
                "execution",
                "specificity",
                "restraint",
                "variety",
            },
        )
        self.assertTrue(all(score >= 4 for score in scores.values()))
        design = (ROOT / "DESIGN.md").read_text(encoding="utf-8")
        stamp = re.search(
            r"Hallmark · pre-emit critique: P(\d) H(\d) E(\d) S(\d) R(\d) V(\d)",
            design,
        )
        self.assertIsNotNone(stamp)
        assert stamp
        self.assertEqual(
            tuple(map(int, stamp.groups())),
            tuple(
                scores[name]
                for name in (
                    "philosophy",
                    "hierarchy",
                    "execution",
                    "specificity",
                    "restraint",
                    "variety",
                )
            ),
        )

    def test_color_scheme_is_complete_and_consistent(self) -> None:
        standalone = ROOT / "color-schemes/NoxForgeDark.colors"
        embedded = ROOT / f"plasma/desktoptheme/{THEME_ID}/colors"
        self.assertEqual(standalone.read_bytes(), embedded.read_bytes())
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(standalone, encoding="utf-8")
        self.assertEqual(parser["General"]["ColorScheme"], "NoxForgeDark")
        self.assertEqual(parser["Colors:Selection"]["BackgroundNormal"], "38,54,29")
        self.assertEqual(parser["Colors:Selection"]["BackgroundAlternate"], "38,54,29")
        self.assertEqual(parser["Colors:Selection"]["DecorationFocus"], "163,255,71")


if __name__ == "__main__":
    unittest.main()
