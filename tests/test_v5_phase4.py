from __future__ import annotations

import hashlib
import json
import math
import struct
import subprocess
import sys
import unittest
import wave
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "design/artwork-contract.json").read_text(encoding="utf-8"))


class V5PhaseFourTests(unittest.TestCase):
    def test_brand_mark_is_optically_refined_and_physical_copies_match(self) -> None:
        paths = (
            ROOT / "design/brand/noxforge-mark.svg",
            ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/splash/NoxForgeMark.svg",
            ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/logout/NoxForgeMark.svg",
            ROOT / "kwin/tabbox/io.github.loofiboss.noxforge.desktop/contents/ui/NoxForgeMark.svg",
            ROOT / "sddm/NoxForge/NoxForgeMark.svg",
        )
        self.assertEqual(CONTRACT["brand"]["opticalSizes"], [48, 96, 192])
        self.assertEqual(CONTRACT["brand"]["minimumClearSpace"], 12)
        self.assertEqual(len({path.read_bytes() for path in paths}), 1)
        self.assertEqual(ET.parse(paths[0]).getroot().get("viewBox"), CONTRACT["brand"]["viewBox"])

    def test_wallpaper_compositions_are_separate_and_deterministic(self) -> None:
        compositions = CONTRACT["wallpapers"]
        self.assertEqual(set(compositions), {"16:9", "ultrawide"})
        sources = [ROOT / details["source"] for details in compositions.values()]
        self.assertEqual(len({path.read_bytes() for path in sources}), 2)
        result = subprocess.run(
            [sys.executable, "scripts/render_wallpaper.py", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_fixed_runtime_icon_fixture_and_optical_policy_are_complete(self) -> None:
        coverage = json.loads((ROOT / "icons/NoxForge/coverage.json").read_text(encoding="utf-8"))
        fixture = sorted(CONTRACT["runtimeIconFixture"]["required"])
        self.assertEqual(coverage["runtimeFixture"], fixture)
        self.assertEqual(coverage["runtimeFixtureSource"], CONTRACT["runtimeIconFixture"]["source"])
        for relative in fixture:
            self.assertTrue((ROOT / "icons/NoxForge/scalable" / relative).is_file(), relative)
        optical_contexts = set(CONTRACT["runtimeIconFixture"]["opticalContexts"])
        for size in CONTRACT["runtimeIconFixture"]["opticalSizes"]:
            optical = list((ROOT / f"icons/NoxForge/{size}x{size}").glob("*/*.svg"))
            self.assertTrue(optical)
            self.assertEqual({path.parent.name for path in optical}, optical_contexts)

    def test_cursor_hotspots_sizes_and_animation_timing_match_manifest(self) -> None:
        theme = ROOT / "cursors/NoxForge-Cursors"
        coverage = json.loads((theme / "coverage.json").read_text(encoding="utf-8"))
        self.assertEqual(coverage["sizes"], CONTRACT["cursors"]["physicalSizes"])
        for name in coverage["canonical"]:
            data = (theme / "cursors" / name).read_bytes()
            _, _, _, count = struct.unpack("<4I", data[:16])
            observed = {}
            for index in range(count):
                position = struct.unpack("<3I", data[16 + index * 12 : 28 + index * 12])[2]
                _, _, size, _, _, _, xhot, yhot, delay = struct.unpack("<9I", data[position : position + 36])
                observed[str(size)] = [xhot, yhot]
                expected_delay = CONTRACT["cursors"]["animation"]["delayMs"] if name in {"wait", "progress"} else 0
                self.assertEqual(delay, expected_delay)
            self.assertEqual(observed, coverage["hotspots"][name])

    def test_sound_sources_are_normalized_and_semantically_distinct(self) -> None:
        theme = ROOT / "sounds/NoxForge"
        coverage = json.loads((theme / "coverage.json").read_text(encoding="utf-8"))
        normalization = coverage["normalization"]
        signatures = set()
        for name, details in coverage["sources"].items():
            with wave.open(str(theme / "source" / f"{name}.wav"), "rb") as source:
                frames = source.readframes(source.getnframes())
            samples = struct.unpack(f"<{len(frames) // 2}h", frames)
            rms = math.sqrt(sum(sample * sample for sample in samples) / len(samples)) / 32767
            actual = 20 * math.log10(rms)
            target = normalization["alarmTargetRmsDbfs"] if name == "alarm" else normalization["targetRmsDbfs"]
            self.assertLessEqual(abs(actual - target), normalization["toleranceDb"])
            signature = (details["durationMs"], tuple(details["frequenciesHz"]))
            self.assertNotIn(signature, signatures)
            signatures.add(signature)

    def test_reviewed_contact_sheets_are_current(self) -> None:
        manifest = json.loads((ROOT / CONTRACT["evidence"]["manifest"]).read_text(encoding="utf-8"))
        self.assertEqual(manifest["reviewStatus"], "reviewed")
        self.assertEqual(set(manifest["sheets"]), set(CONTRACT["evidence"]["sheets"]))
        for relative, expected in {**manifest["sources"], **manifest["sheets"]}.items():
            self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), expected)
        result = subprocess.run(
            [sys.executable, "scripts/render_artwork_evidence.py", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_phase_plan_records_completed_gate(self) -> None:
        plan = (ROOT / "docs/NOXFORGE_V5_PLAN.md").read_text(encoding="utf-8")
        phase = plan.split("## Phase 4", 1)[1].split("## Phase 5", 1)[0]
        self.assertIn("**Outcome (2026-07-26):**", phase)


if __name__ == "__main__":
    unittest.main()
