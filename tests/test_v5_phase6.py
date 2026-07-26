from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION = ROOT / "docs/evidence/v5/qualification.json"


class V5PhaseSixTests(unittest.TestCase):
    def test_accessibility_review_is_complete_and_source_bound(self) -> None:
        review = json.loads(
            (ROOT / "docs/evidence/v5/accessibility-review.json").read_text(encoding="utf-8")
        )
        self.assertEqual(review["phase"], 6)
        self.assertEqual(review["reviewStatus"], "passed")
        self.assertEqual(review["hardcodedRuntimeFontFamilies"], [])
        self.assertTrue(all(review["reviews"].values()))
        self.assertEqual(review["colorVisionReview"]["result"], "passed")
        self.assertGreaterEqual(len(review["contrastPairs"]), 13)

    def test_performance_medians_remain_within_phase_zero_budget(self) -> None:
        evidence = json.loads(
            (ROOT / "docs/evidence/v5/performance.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            evidence["baselineCommit"],
            "e3faefd481026cffafb9b48e11aa79987781fa78",
        )
        self.assertEqual(evidence["result"], "passed")
        self.assertEqual(
            set(evidence["metrics"]),
            {"galleryStartup", "controlRendering", "qmlFirstFrame"},
        )
        for metric in evidence["metrics"].values():
            self.assertLessEqual(metric["ratio"], 1.10)
            self.assertEqual(metric["result"], "passed")

    def test_live_matrix_has_no_failed_case_and_never_promotes_offscreen_evidence(self) -> None:
        manifest = json.loads(QUALIFICATION.read_text(encoding="utf-8"))
        self.assertNotIn("failed", {case["result"] for case in manifest["liveCases"]})
        automated = manifest["automatedEvidence"]
        if automated["result"] == "passed":
            self.assertTrue((QUALIFICATION.parent / automated["evidence"]).is_file())
        live_paths = {
            case["evidence"]
            for case in manifest["liveCases"]
            if case["result"] == "passed"
        }
        self.assertNotIn(automated["evidence"], live_paths)
        for case in manifest["liveCases"]:
            if case["result"] == "blocked":
                self.assertTrue(case["blocker"])

    def test_phase_plan_records_completed_gate(self) -> None:
        plan = (ROOT / "docs/NOXFORGE_V5_PLAN.md").read_text(encoding="utf-8")
        self.assertIn("Plan status:** Phase 6 complete; Phase 7 is not authorized", plan)
        phase = plan.split("## Phase 6", 1)[1].split("## Phase 7", 1)[0]
        self.assertIn("**Outcome (2026-07-26):**", phase)


if __name__ == "__main__":
    unittest.main()
