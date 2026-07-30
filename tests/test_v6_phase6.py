from __future__ import annotations

import gzip
import hashlib
import json
import struct
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME_ID = "io.github.loofiboss.noxforge.desktop"
CONTRACT = json.loads(
    (ROOT / "design/edge-polish-contract.json").read_text(encoding="utf-8")
)
EVIDENCE_ROOT = ROOT / "docs/evidence/v6/edge-polish"
MANIFEST = json.loads((EVIDENCE_ROOT / "manifest.json").read_text(encoding="utf-8"))


def ids(path: Path) -> set[str]:
    return {
        node.get("id")
        for node in ET.parse(path).iter()
        if node.get("id")
    }


def tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


class V6PhaseSixTests(unittest.TestCase):
    def test_aurorae_material_geometry_buttons_and_states_are_complete(self) -> None:
        self.assertEqual(CONTRACT["schemaVersion"], 1)
        self.assertEqual(CONTRACT["phase"], 6)
        aurorae = CONTRACT["aurorae"]
        self.assertEqual(aurorae["titleHeight"], 26)
        self.assertEqual(aurorae["buttonSize"], 26)
        self.assertEqual(aurorae["activeMaterial"], "surfaceRaised")
        self.assertEqual(aurorae["inactiveMaterial"], "surfaceSunken")
        self.assertFalse(aurorae["coloredGlow"])

        theme = ROOT / f"aurorae/{THEME_ID}"
        rc = (theme / f"{THEME_ID}rc").read_text(encoding="utf-8")
        for setting in (
            "TitleHeight=26",
            "ButtonWidth=26",
            "ButtonWidthMenu=26",
            "ButtonHeight=26",
        ):
            self.assertIn(setting, rc)

        decoration = (theme / "decoration.svg").read_text(encoding="utf-8")
        self.assertIn("ColorScheme-Raised", decoration)
        self.assertIn("ColorScheme-Sunken", decoration)
        self.assertIn("ColorScheme-Highlight", decoration)
        self.assertNotIn("filter=", decoration)
        self.assertIn(
            f'h{aurorae["activeRailLength"]}',
            decoration,
        )
        self.assertIn(
            f'stroke-width="{aurorae["activeRailThickness"]}"',
            decoration,
        )

        expected_states = {f"{state}-center" for state in aurorae["states"]}
        for button in aurorae["buttons"]:
            source = theme / f"{button}.svg"
            with self.subTest(button=button):
                self.assertTrue(expected_states.issubset(ids(source)))
                self.assertEqual(
                    gzip.decompress(source.with_suffix(".svgz").read_bytes()),
                    source.read_bytes(),
                )

    def test_priority_icon_fixture_is_ranked_and_coverage_is_frozen(self) -> None:
        icon_contract = CONTRACT["icons"]
        priority = [
            relative
            for group in ("panel", "systemSettings", "dolphin", "session")
            for relative in icon_contract["priority"][group]
        ]
        self.assertEqual(len(priority), 56)
        self.assertEqual(len(set(priority)), 56)
        coverage = json.loads(
            (ROOT / "icons/NoxForge/coverage.json").read_text(encoding="utf-8")
        )
        frozen = icon_contract["coverageFrozen"]
        self.assertEqual(coverage["iconCount"], frozen["scalable"])
        self.assertEqual(coverage["opticalCount"], frozen["optical"])
        self.assertEqual(len(coverage["runtimeFixture"]), frozen["runtimeFixture"])
        self.assertEqual(coverage["phase6Priority"], icon_contract["priority"])
        self.assertEqual(coverage["phase6ReviewSizes"], [16, 22, 24, 32, 48])
        self.assertTrue(set(priority).issubset(coverage["runtimeFixture"]))
        for relative in priority:
            self.assertTrue((ROOT / "icons/NoxForge/scalable" / relative).is_file())

    def test_cursor_hotspots_timing_and_sizes_are_preserved(self) -> None:
        theme = ROOT / "cursors/NoxForge-Cursors"
        coverage = json.loads((theme / "coverage.json").read_text(encoding="utf-8"))
        cursor_contract = CONTRACT["cursors"]
        self.assertEqual(coverage["sizes"], cursor_contract["physicalSizes"])
        self.assertEqual(coverage["animations"]["wait"], cursor_contract["animation"])
        self.assertEqual(coverage["animations"]["progress"], cursor_contract["animation"])

        for name in coverage["canonical"]:
            data = (theme / "cursors" / name).read_bytes()
            _, _, _, count = struct.unpack("<4I", data[:16])
            expected_count = len(coverage["sizes"]) * (
                cursor_contract["animation"]["frames"]
                if name in {"wait", "progress"}
                else 1
            )
            self.assertEqual(count, expected_count)
            observed: dict[str, set[tuple[int, int]]] = {}
            for index in range(count):
                position = struct.unpack("<3I", data[16 + index * 12 : 28 + index * 12])[2]
                _, _, size, _, _, _, xhot, yhot, delay = struct.unpack(
                    "<9I", data[position : position + 36]
                )
                observed.setdefault(str(size), set()).add((xhot, yhot))
                expected_delay = cursor_contract["animation"]["delayMs"] if name in {
                    "wait",
                    "progress",
                } else 0
                self.assertEqual(delay, expected_delay)
            self.assertEqual(
                {
                    size: [*next(iter(hotspots))]
                    for size, hotspots in observed.items()
                    if len(hotspots) == 1
                },
                coverage["hotspots"][name],
            )

        default_source = (theme / "source/default.svg").read_text(encoding="utf-8")
        self.assertIn(f'stroke-width="{cursor_contract["outlineWidth"]}"', default_source)
        self.assertIn("#0E1318", default_source)
        self.assertIn("#A3FF47", default_source)

    def test_sound_theme_is_byte_frozen(self) -> None:
        self.assertEqual(CONTRACT["sound"]["policy"], "unchanged")
        self.assertEqual(
            tree_sha256(ROOT / "sounds/NoxForge"),
            CONTRACT["sound"]["treeSha256"],
        )

    def test_edge_polish_evidence_is_reviewed_source_bound_and_non_live(self) -> None:
        self.assertEqual(MANIFEST["phase"], 6)
        self.assertEqual(MANIFEST["kind"], "deterministic-source-optical-review")
        self.assertEqual(MANIFEST["reviewStatus"], "reviewed-offscreen")
        self.assertFalse(MANIFEST["liveDecoration"])
        self.assertTrue(MANIFEST["liveDecorationRemainsPhase7"])
        self.assertEqual(MANIFEST["icons"]["priorityCount"], 56)
        self.assertEqual(MANIFEST["icons"]["reviewSizes"], [16, 22, 24, 32, 48])
        self.assertEqual(MANIFEST["cursors"]["physicalSizes"], [24, 32, 48])
        self.assertEqual(
            set(MANIFEST["outputs"]),
            set(CONTRACT["evidence"]["outputs"]),
        )
        for relative, details in MANIFEST["outputs"].items():
            path = ROOT / relative
            self.assertTrue(path.is_file())
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), details["sha256"])
        for relative, digest in MANIFEST["sourceHashes"].items():
            path = ROOT / relative
            self.assertTrue(path.is_file())
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)

    def test_live_decoration_and_cursor_cases_remain_blocked(self) -> None:
        qualification = json.loads(
            (ROOT / "docs/evidence/v6/qualification.json").read_text(encoding="utf-8")
        )
        live = {case["id"]: case for case in qualification["liveCases"]}
        for case_id in ("aurorae-composed-motion", "cursor-live-scale"):
            self.assertEqual(live[case_id]["status"], "blocked")
            self.assertIn("authorized", live[case_id]["reason"])


if __name__ == "__main__":
    unittest.main()
