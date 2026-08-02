from __future__ import annotations

import gzip
import json
import subprocess
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "aurorae/io.github.loofiboss.noxforge.desktop"
POSITIONS = {
    "topleft",
    "top",
    "topright",
    "left",
    "center",
    "right",
    "bottomleft",
    "bottom",
    "bottomright",
}


def ids(path: Path) -> set[str]:
    return {
        identifier
        for element in ET.parse(path).iter()
        if (identifier := element.get("id")) is not None
    }


class V7PhaseOneTests(unittest.TestCase):
    def test_maximized_decoration_uses_documented_normal_frame_fallback(self) -> None:
        decoration = ids(THEME / "decoration.svg")
        for prefix in ("decoration", "decoration-inactive"):
            self.assertTrue(
                {f"{prefix}-{position}" for position in POSITIONS}.issubset(
                    decoration
                )
            )
        self.assertFalse(
            {identifier for identifier in decoration if identifier.startswith("decoration-maximized")}
        )
        contract = json.loads(
            (ROOT / "design/edge-polish-contract.json").read_text(encoding="utf-8")
        )["aurorae"]
        self.assertEqual(contract["maximizedStrategy"], "normal-frame-fallback")
        self.assertFalse(contract["specialMaximizedElements"])

    def test_fallback_centers_are_simple_opaque_stretchable_rectangles(self) -> None:
        root = ET.parse(THEME / "decoration.svg").getroot()
        self.assertEqual(root.get("viewBox"), "0 0 92 40")
        elements = {
            element.get("id"): element
            for element in root.iter()
            if element.get("id")
        }
        for identifier, material, minimum_opacity in (
            ("decoration-center", "ColorScheme-Raised", 1.0),
            ("decoration-inactive-center", "ColorScheme-Sunken", 0.9),
        ):
            center = elements[identifier]
            self.assertTrue(center.tag.endswith("rect"))
            self.assertEqual(center.get("class"), material)
            self.assertEqual(center.get("fill"), "currentColor")
            self.assertGreaterEqual(float(center.get("fill-opacity", "1")), minimum_opacity)
            self.assertGreater(float(center.get("width", "0")), 0)
            self.assertGreater(float(center.get("height", "0")), 0)

    def test_source_and_canonical_compressed_output_match(self) -> None:
        source = (THEME / "decoration.svg").read_bytes()
        compressed = (THEME / "decoration.svgz").read_bytes()
        self.assertEqual(gzip.decompress(compressed), source)
        self.assertEqual(compressed[:8], b"\x1f\x8b\x08\x00\x00\x00\x00\x00")

    def test_phase_one_evidence_is_current_and_keeps_live_matrix_pending(self) -> None:
        subprocess.run(
            ["python3", "scripts/check_v7_aurorae.py", "--check"],
            cwd=ROOT,
            check=True,
        )
        evidence = json.loads(
            (ROOT / "docs/evidence/v7/aurorae/phase1.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(evidence["strategy"], "normal-frame-fallback")
        self.assertEqual(len(evidence["staticMatrix"]), 48)
        self.assertEqual(
            {entry["scalePercent"] for entry in evidence["staticMatrix"]},
            {100, 125, 140, 150, 175, 200},
        )
        self.assertTrue(
            all(entry["status"] == "passed-static" for entry in evidence["staticMatrix"])
        )
        self.assertEqual(evidence["liveMatrix"]["status"], "pending")
        self.assertFalse(evidence["releaseReady"])

    def test_maximized_edge_and_button_targets_remain_zero_and_aligned(self) -> None:
        config = (THEME / "io.github.loofiboss.noxforge.desktoprc").read_text(
            encoding="utf-8"
        )
        for edge in ("Top", "Bottom", "Left", "Right"):
            self.assertIn(f"TitleEdge{edge}Maximized=0", config)
        self.assertIn("ButtonWidth=26", config)
        self.assertIn("ButtonHeight=26", config)
        for name in ("minimize", "maximize", "restore", "close"):
            self.assertTrue((THEME / f"{name}.svg").is_file())
            self.assertTrue((THEME / f"{name}.svgz").is_file())


if __name__ == "__main__":
    unittest.main()
