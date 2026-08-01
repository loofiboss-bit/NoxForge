from __future__ import annotations

import hashlib
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop"
CONTRACT_PATH = ROOT / "design/plasma-semantic-contract.json"
ATLAS_PATH = ROOT / "docs/evidence/v6/plasma-shell/atlas-manifest.json"


def elements(relative: str) -> dict[str, ET.Element]:
    return {
        element.get("id"): element
        for element in ET.parse(THEME / relative).iter()
        if element.get("id")
    }


class V6PhaseFourTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_material_contract_is_complete_and_filter_free(self) -> None:
        self.assertEqual(self.contract["schemaVersion"], 4)
        self.assertEqual(
            self.contract["materialPolicy"]["hierarchy"],
            ["canvas", "sunken", "surface", "raised", "overlay"],
        )
        self.assertFalse(self.contract["materialPolicy"]["coloredShadows"])
        self.assertFalse(self.contract["materialPolicy"]["runtimeSvgFilters"])
        self.assertFalse(self.contract["materialPolicy"]["blurRequiredForReadability"])
        generator = (ROOT / "scripts/generate_plasma_svgs.py").read_text(encoding="utf-8")
        self.assertIn('COLORS = TOKENS["colors"]', generator)
        self.assertNotIn("assetGenerationPalette", generator)

    def test_overlays_have_one_neutral_highlight_and_shadow_recipe(self) -> None:
        for relative in (
            "dialogs/background.svg",
            "widgets/background.svg",
            "widgets/tooltip.svg",
            "solid/dialogs/background.svg",
            "translucent/widgets/background.svg",
        ):
            with self.subTest(relative=relative):
                text = (THEME / relative).read_text(encoding="utf-8")
                self.assertIn("NoxForge-EdgeHighlight", text)
                self.assertIn("NoxForge-OverlayShadow", text)
                self.assertNotIn("filter=", text)

    def test_active_task_and_tab_markers_follow_the_panel_edge(self) -> None:
        marker_positions = {
            "north": "bottom",
            "south": "top",
            "east": "left",
            "west": "right",
        }
        task_parts = elements("widgets/tasks.svg")
        tab_parts = elements("widgets/tabbar.svg")
        for orientation, position in marker_positions.items():
            with self.subTest(orientation=orientation):
                for state in ("focus", "progress"):
                    task_marker = task_parts[f"{orientation}-{state}-{position}"]
                    self.assertTrue(
                        any(node.get("class") == "ColorScheme-Highlight" for node in task_marker.iter())
                    )
                tab_marker = tab_parts[f"{orientation}-active-tab-{position}"]
                self.assertTrue(
                    any(node.get("class") == "ColorScheme-Highlight" for node in tab_marker.iter())
                )

    def test_static_source_matrix_is_complete_and_truthful(self) -> None:
        manifest = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schemaVersion"], 2)
        self.assertEqual(manifest["assetCount"], 56)
        self.assertEqual(manifest["staticScenarioCount"], 128)
        self.assertEqual(manifest["evidenceClass"], "deterministic-static-svg-source")
        self.assertFalse(manifest["qualifiesLivePlasma"])
        self.assertEqual(
            {(entry["scale"], entry["blur"]) for entry in manifest["materialAtlases"]},
            {
                (1.0, "on"),
                (1.0, "off"),
                (1.25, "on"),
                (1.25, "off"),
                (1.4, "on"),
                (1.4, "off"),
                (2.0, "on"),
                (2.0, "off"),
            },
        )
        for entry in [*manifest["atlases"], *manifest["materialAtlases"]]:
            path = ATLAS_PATH.parent / entry["file"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry["sha256"])

    def test_live_plasma_results_keep_blur_blocked_and_record_layout_pass(self) -> None:
        qualification = json.loads(
            (ROOT / "docs/evidence/v6/qualification.json").read_text(encoding="utf-8")
        )
        live = {case["id"]: case for case in qualification["liveCases"]}
        self.assertEqual(live["plasma-blur-on-off"]["status"], "blocked")
        self.assertIn("virtual framebuffer", live["plasma-blur-on-off"]["reason"])
        self.assertEqual(live["plasma-layout-and-fallback"]["status"], "passed")
        self.assertTrue(
            (ROOT / "docs/evidence/v6" / live["plasma-layout-and-fallback"]["evidence"]).is_file()
        )


if __name__ == "__main__":
    unittest.main()
