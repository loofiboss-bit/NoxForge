from __future__ import annotations

import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop"
CONTRACT = json.loads((ROOT / "design/plasma-semantic-contract.json").read_text(encoding="utf-8"))
V6_MANIFEST = json.loads(
    (ROOT / "docs/evidence/v6/plasma-shell/atlas-manifest.json").read_text(encoding="utf-8")
)
V7_MANIFEST = json.loads(
    (ROOT / "docs/evidence/v7/plasma-shell/atlas-manifest.json").read_text(encoding="utf-8")
)


def margin_size(relative: str, hint: str = "hint-top-margin") -> int:
    elements = {
        element.get("id"): element for element in ET.parse(THEME / relative).iter()
        if element.get("id")
    }
    element = elements[hint]
    return max(int(element.get("width", "0")), int(element.get("height", "0")))


class V7PhaseFourTests(unittest.TestCase):
    def test_shell_metrics_follow_compact_and_standard_four_pixel_rhythm(self) -> None:
        metrics = CONTRACT["shellMetrics"]
        self.assertEqual(metrics["gridUnit"], 4)
        self.assertTrue(all(value % 4 == 0 for value in metrics["surfaceMargins"].values()))
        self.assertEqual(margin_size("widgets/panel-background.svg"), 4)
        self.assertEqual(margin_size("widgets/toolbar.svg"), 4)
        self.assertEqual(margin_size("widgets/background.svg"), 8)
        self.assertEqual(margin_size("dialogs/background.svg"), 8)
        self.assertEqual(margin_size("widgets/tooltip.svg"), 8)

    def test_all_panel_edges_keep_distinct_focus_and_progress_markers(self) -> None:
        ids = {
            element.get("id") for element in ET.parse(THEME / "widgets/tasks.svg").iter()
            if element.get("id")
        }
        marker_edges = {"north": "bottom", "south": "top", "east": "left", "west": "right"}
        for orientation, edge in marker_edges.items():
            for state in ("focus", "progress"):
                self.assertIn(f"{orientation}-{state}-{edge}", ids)

    def test_v7_before_after_evidence_uses_identical_viewports(self) -> None:
        self.assertEqual(V7_MANIFEST["version"], "7.0.0-dev")
        self.assertFalse(V7_MANIFEST["qualifiesLivePlasma"])
        self.assertEqual(V7_MANIFEST["staticScenarioCount"], 128)
        before = {(entry["scale"], entry["width"], entry["height"]) for entry in V6_MANIFEST["atlases"]}
        after = {(entry["scale"], entry["width"], entry["height"]) for entry in V7_MANIFEST["atlases"]}
        self.assertEqual(before, after)
        before_sources = {entry["path"]: entry["sha256"] for entry in V6_MANIFEST["assets"]}
        after_sources = {entry["path"]: entry["sha256"] for entry in V7_MANIFEST["assets"]}
        for relative in (
            "dialogs/background.svg",
            "widgets/background.svg",
            "widgets/panel-background.svg",
            "widgets/tooltip.svg",
        ):
            self.assertNotEqual(before_sources[relative], after_sources[relative])

    def test_shell_work_does_not_apply_or_reset_configuration(self) -> None:
        generator = (ROOT / "scripts/generate_plasma_svgs.py").read_text(encoding="utf-8")
        for forbidden in ("plasma-apply-lookandfeel", "resetLayout", "kwriteconfig"):
            self.assertNotIn(forbidden, generator)


if __name__ == "__main__":
    unittest.main()
