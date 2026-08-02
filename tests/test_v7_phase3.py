from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "design/v7-style-contract.json").read_text(encoding="utf-8"))


class V7PhaseThreeTests(unittest.TestCase):
    def test_kde_click_policy_and_base_mnemonics_are_respected(self) -> None:
        style = (ROOT / "src/style/noxforgestyle.cpp").read_text(encoding="utf-8")
        self.assertIn('settings.contains(QStringLiteral("SingleClick"))', style)
        self.assertIn("case SH_UnderlineShortcut:", style)
        self.assertIn("case SH_MenuBar_AltKeyNavigation:", style)
        self.assertNotIn("case SH_UnderlineShortcut: return 0;", style)
        self.assertNotIn("case SH_ItemView_ActivateItemOnSingleClick: return 0;", style)

    def test_scrollbar_separates_hit_target_from_visual_track(self) -> None:
        scrollbar = CONTRACT["scrollbar"]
        self.assertGreaterEqual(scrollbar["functionalExtent"], 16)
        self.assertLessEqual(scrollbar["visualTrackMaximum"], 6)
        self.assertGreater(scrollbar["functionalExtent"], scrollbar["visualTrackMaximum"])

    def test_selection_language_remains_neutral_and_rtl_aware(self) -> None:
        selection = CONTRACT["selection"]
        self.assertEqual(selection["surfaceRole"], "surfaceSelected")
        self.assertEqual(selection["markerRole"], "accent")
        self.assertTrue(selection["rtlMirrored"])

    def test_style_evidence_is_current(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/check_v7_style.py", "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
