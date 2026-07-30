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
POSITIONS = {"top", "topright", "right", "bottomright", "bottom", "bottomleft", "left", "topleft", "center"}


def elements(path: Path) -> dict[str, ET.Element]:
    return {element.get("id"): element for element in ET.parse(path).iter() if element.get("id")}


class V5PhaseThreeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_all_43_families_use_versioned_semantic_recipes(self) -> None:
        self.assertEqual(self.contract["schemaVersion"], 4)
        families = set(self.contract["widgetFamilies"])
        family_recipes = self.contract["familyRecipes"]
        recipes = self.contract["semanticRecipes"]
        self.assertEqual(len(families), 43)
        self.assertEqual(set(family_recipes), families)
        self.assertTrue(set(family_recipes.values()).issubset(recipes))
        generator = (ROOT / "scripts/generate_plasma_svgs.py").read_text(encoding="utf-8")
        self.assertIn('CONTRACT["semanticRecipes"]', generator)
        self.assertIn('CONTRACT["familyRecipes"]', generator)
        self.assertEqual(generator.count("Paint("), 1, "raw paints must only be constructed by recipe()")

    def test_surface_variants_have_complete_consistent_frames(self) -> None:
        for relative in self.contract["backgroundVariants"]:
            with self.subTest(relative=relative):
                found = elements(THEME / relative)
                self.assertTrue(POSITIONS.issubset(found))
                paints = set()
                for position in POSITIONS:
                    base = next(
                        node
                        for node in found[position].iter()
                        if node.tag.endswith(("path", "rect")) and node.get("class")
                    )
                    paints.add((base.get("class"), base.get("fill-opacity")))
                self.assertEqual(len(paints), 1, "one paint across a nine-slice prevents dark seams")

    def test_task_focus_markers_follow_every_panel_edge(self) -> None:
        found = elements(THEME / "widgets/tasks.svg")
        marker_positions = {
            "north": "bottom",
            "south": "top",
            "east": "left",
            "west": "right",
        }
        for orientation, position in marker_positions.items():
            for state in ("focus", "progress"):
                with self.subTest(orientation=orientation, state=state):
                    marker = found[f"{orientation}-{state}-{position}"]
                    highlights = [
                        node for node in marker.iter() if node.get("class") == "ColorScheme-Highlight"
                    ]
                    self.assertEqual(len(highlights), 1)

    def test_focused_frames_draw_one_indicator_without_stacking(self) -> None:
        cases = {
            "widgets/button.svg": ("focus", "toolbutton-focus"),
            "widgets/lineedit.svg": ("focus",),
            "widgets/tasks.svg": ("focus", "north-focus", "south-focus", "east-focus", "west-focus"),
        }
        for relative, states in cases.items():
            found = elements(THEME / relative)
            for state in states:
                with self.subTest(relative=relative, state=state):
                    nodes = [found[f"{state}-{position}"] for position in POSITIONS]
                    highlights = [
                        child
                        for node in nodes
                        for child in node.iter()
                        if child.get("class") == "ColorScheme-Highlight"
                    ]
                    self.assertEqual(len(highlights), 1)

    def test_complete_state_orientation_scale_atlas_is_current(self) -> None:
        manifest = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
        expected_assets = (
            [f"widgets/{name}.svg" for name in self.contract["widgetFamilies"]]
            + [f"weather/{name}.svg" for name in self.contract["weatherFamilies"]]
            + ["dialogs/background.svg"]
            + self.contract["backgroundVariants"]
        )
        self.assertEqual(manifest["assetCount"], 56)
        self.assertEqual([entry["path"] for entry in manifest["assets"]], expected_assets)
        self.assertEqual(manifest["qualifiedSurfaces"], self.contract["qualifiedSurfaces"])
        self.assertEqual(
            set(manifest["qualifiedSurfaces"]),
            {
                "panels",
                "popups",
                "notifications",
                "tooltips",
                "calendarWeather",
                "inputs",
                "osdContainment",
            },
        )
        self.assertEqual(manifest["stateFrames"], self.contract["stateFrames"])
        self.assertEqual(manifest["orientedTaskStates"], self.contract["orientedTaskStates"])
        self.assertEqual([entry["scale"] for entry in manifest["atlases"]], [1.0, 1.25, 1.4, 2.0])
        for entry in manifest["atlases"]:
            atlas = ATLAS_PATH.parent / entry["file"]
            self.assertTrue(atlas.is_file())
            self.assertEqual(hashlib.sha256(atlas.read_bytes()).hexdigest(), entry["sha256"])

    def test_phase_plan_records_completed_gate(self) -> None:
        plan = (ROOT / "docs/NOXFORGE_V5_PLAN.md").read_text(encoding="utf-8")
        phase = plan.split("## Phase 3", 1)[1].split("## Phase 4", 1)[0]
        self.assertIn("**Outcome (2026-07-26):**", phase)


if __name__ == "__main__":
    unittest.main()
