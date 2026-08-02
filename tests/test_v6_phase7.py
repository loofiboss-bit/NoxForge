from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if (ROOT / "VERSION").read_text(encoding="utf-8").strip() != "6.0.0":
    raise unittest.SkipTest("historical v6 source-bound tests")
EVIDENCE_ROOT = ROOT / "docs/evidence/v6"


class V6PhaseSevenTests(unittest.TestCase):
    def test_accessibility_review_is_complete_source_bound_and_non_live(self) -> None:
        subprocess.run(
            ["python3", "scripts/check_v6_accessibility.py", "--check"],
            cwd=ROOT,
            check=True,
        )
        review = json.loads(
            (EVIDENCE_ROOT / "accessibility-review.json").read_text(encoding="utf-8")
        )
        self.assertEqual(review["phase"], 7)
        self.assertEqual(review["reviewStatus"], "passed")
        self.assertFalse(review["liveInteraction"])
        self.assertEqual(review["hardcodedRuntimeFontFamilies"], [])
        self.assertTrue(all(review["reviews"].values()))
        self.assertGreaterEqual(len(review["contrastPairs"]), 15)
        reduced_probe = review["reducedMotionProbe"]
        self.assertEqual(reduced_probe["result"], "passed")
        self.assertEqual(set(reduced_probe["surfaces"]), {"sddm", "splash", "logout", "tabbox"})
        for surface in reduced_probe["surfaces"].values():
            self.assertTrue(surface["reducedMotion"])
            self.assertEqual(surface["testProgress"], -1)
            self.assertGreater(surface["animationObjectsObserved"], 0)
            self.assertEqual(surface["runningAnimationCountAfterTransition"], 0)
        for relative, digest in review["sources"].items():
            self.assertEqual(
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
                digest,
            )

    def test_high_contrast_preference_is_observed_without_overclaim(self) -> None:
        review = json.loads(
            (EVIDENCE_ROOT / "accessibility-review.json").read_text(encoding="utf-8")
        )
        preference = review["highContrastPreference"]
        self.assertIn(preference["preference"], {"NoPreference", "HighContrast"})
        if preference["preference"] == "NoPreference":
            self.assertFalse(preference["exposed"])
            self.assertEqual(preference["result"], "not-exposed")
            self.assertIn("not claimed", preference["observation"])
        else:
            self.assertTrue(preference["exposed"])
            self.assertEqual(preference["result"], "passed")

    def test_complete_performance_matrix_remains_within_v5_budget(self) -> None:
        subprocess.run(
            ["python3", "scripts/measure_v6_phase7_performance.py", "--check"],
            cwd=ROOT,
            check=True,
        )
        evidence = json.loads(
            (EVIDENCE_ROOT / "performance.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            evidence["baselineCommit"],
            "6a113e71980d106c38a2bbdece6df171c0ae9ed3",
        )
        self.assertEqual(
            set(evidence["metrics"]),
            {"galleryStartup", "controlRendering", "qmlFirstFrame"},
        )
        for metric in evidence["metrics"].values():
            self.assertEqual(metric["result"], "passed")
            self.assertLessEqual(metric["ratio"], 1.10)

    def test_motion_stress_covers_500_cycles_memory_idle_and_cleanup(self) -> None:
        evidence = json.loads(
            (EVIDENCE_ROOT / "performance.json").read_text(encoding="utf-8")
        )
        stress = evidence["motionStress"]
        self.assertEqual(stress["result"], "passed")
        self.assertEqual(stress["cycles"], 500)
        self.assertEqual(stress["failedCases"], 0)
        self.assertFalse(stress["idleTimerActive"])
        self.assertEqual(stress["trackedWidgetsAfterCleanup"], 0)
        self.assertLessEqual(
            stress["heapGrowthBytes"],
            stress["heapGrowthLimitBytes"],
        )
        cmake = (ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
        sanitizer = (ROOT / "scripts/check_v6_phase3_sanitizers.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("motion-qualification-500-cycles", cmake)
        self.assertIn("noxforge_motion_qualification_probe", sanitizer)

    def test_automated_cases_pass_and_live_results_remain_truthful(self) -> None:
        qualification = json.loads(
            (EVIDENCE_ROOT / "qualification.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            {case["status"] for case in qualification["automatedCases"]},
            {"passed"},
        )
        for case in qualification["automatedCases"]:
            self.assertTrue((EVIDENCE_ROOT / case["evidence"]).is_file())
        live_statuses = {case["status"] for case in qualification["liveCases"]}
        self.assertEqual(live_statuses, {"blocked", "passed"})
        self.assertTrue(all(case["reason"] for case in qualification["liveCases"]))
        for case in qualification["liveCases"]:
            if case["status"] == "passed":
                self.assertTrue((EVIDENCE_ROOT / case["evidence"]).is_file())
        self.assertFalse(qualification["evidencePolicy"]["offscreenIsLiveEvidence"])

    def test_phase_gate_and_plan_record_the_truthful_boundary(self) -> None:
        gate = (ROOT / "scripts/release-check.py").read_text(encoding="utf-8")
        self.assertIn("check_v6_accessibility.py", gate)
        self.assertIn("measure_v6_phase7_performance.py", gate)
        plan = (ROOT / "docs/NOXFORGE_V6_PLAN.md").read_text(encoding="utf-8")
        phase = plan.split("## Phase 7", 1)[1].split("## Phase 8", 1)[0]
        self.assertIn("**Outcome (2026-07-30):**", phase)
        self.assertIn("135 Python tests", phase)
        self.assertIn("21 CTest", phase)
        self.assertIn("remain `blocked`", phase)


if __name__ == "__main__":
    unittest.main()
