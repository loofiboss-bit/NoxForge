from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads(
    (ROOT / "design/v7-asset-contract.json").read_text(encoding="utf-8")
)
EVIDENCE = json.loads(
    (ROOT / "docs/evidence/v7/assets/phase6.json").read_text(encoding="utf-8")
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class V7PhaseSixTests(unittest.TestCase):
    def test_priority_is_ranked_bounded_and_derived_from_runtime_fixture(self) -> None:
        ranked = CONTRACT["rankedPriority"]
        self.assertEqual(len(ranked), 48)
        self.assertEqual(len(ranked), len(set(ranked)))
        coverage = json.loads(
            (ROOT / "icons/NoxForge/coverage.json").read_text(encoding="utf-8")
        )
        self.assertTrue(set(ranked) <= set(coverage["runtimeFixture"]))
        self.assertEqual(set(CONTRACT["evidenceBasis"]), {"panel", "systemSettings", "dolphin", "session"})

    def test_priority_icons_remain_visible_and_distinct_at_small_sizes(self) -> None:
        self.assertEqual(CONTRACT["reviewSizes"], [16, 22, 24])
        qualification = EVIDENCE["renderQualification"]
        for size in (16, 22, 24):
            result = qualification[str(size)]
            self.assertEqual(result["iconCount"], 48)
            self.assertEqual(result["uniqueRasterCount"], 48)
            self.assertGreater(result["minimumVisiblePixels"], 0)
            self.assertEqual(len(result["rasterHashes"]), 48)

    def test_keyboard_settings_and_hardware_semantics_are_distinct(self) -> None:
        hardware = ROOT / "icons/NoxForge/scalable/devices/input-keyboard.svg"
        settings = ROOT / "icons/NoxForge/scalable/preferences/preferences-desktop-keyboard.svg"
        self.assertNotEqual(hardware.read_bytes(), settings.read_bytes())
        self.assertTrue(EVIDENCE["semanticCorrection"]["distinctAtAllReviewSizes"])

    def test_cursor_identity_stays_byte_identical_to_v6_evidence(self) -> None:
        historical = json.loads(
            (ROOT / "docs/evidence/v6/edge-polish/manifest.json").read_text(encoding="utf-8")
        )
        relative = "cursors/NoxForge-Cursors/coverage.json"
        self.assertEqual(sha256(ROOT / relative), historical["sourceHashes"][relative])
        self.assertEqual(CONTRACT["cursorDecision"]["status"], "unchanged")

    def test_brand_wallpaper_and_palette_identity_remain_unchanged(self) -> None:
        contact = json.loads(
            (ROOT / "docs/evidence/artwork-contact-sheets.json").read_text(encoding="utf-8")
        )
        for relative in (
            "design/brand/noxforge-mark.svg",
            "design/brand/noxforge-mark-mono.svg",
            "design/brand/noxforge-lockup.svg",
            "wallpapers/NoxForge/contents/source/NoxForge.svg",
            "wallpapers/NoxForge/contents/source/NoxForge-Ultrawide.svg",
        ):
            self.assertEqual(sha256(ROOT / relative), contact["sources"][relative])
        self.assertEqual(CONTRACT["brandDecision"]["status"], "unchanged")

    def test_contact_sheet_is_current_and_live_evidence_remains_pending(self) -> None:
        sheet = ROOT / EVIDENCE["contactSheetComparison"]["v7"]
        self.assertEqual(sha256(sheet), EVIDENCE["contactSheetComparison"]["v7Sha256"])
        self.assertNotEqual(
            EVIDENCE["contactSheetComparison"]["historicalV6Sha256"],
            EVIDENCE["contactSheetComparison"]["v7Sha256"],
        )
        self.assertFalse(CONTRACT["liveQualification"]["qualifiesLiveSession"])
        self.assertEqual(CONTRACT["liveQualification"]["status"], "pending")


if __name__ == "__main__":
    unittest.main()
