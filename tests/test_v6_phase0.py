from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V6PhaseZeroTests(unittest.TestCase):
    def test_v6_is_the_single_active_authority(self) -> None:
        index = (ROOT / "docs/IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
        plan = (ROOT / "docs/NOXFORGE_V6_PLAN.md").read_text(encoding="utf-8")
        pointer = (ROOT / "docs/NOXFORGE_V6_KINETIC_PRECISION_PLAN.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("NOXFORGE_V6_PLAN.md", index)
        self.assertIn("Active phase-gated implementation authority", plan)
        self.assertIn("6a113e71980d106c38a2bbdece6df171c0ae9ed3", plan)
        self.assertIn(
            "must not become a second, drifting plan copy",
            " ".join(pointer.split()),
        )

    def test_v6_development_version_does_not_relabel_v5_evidence(self) -> None:
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), "6.0.0-dev")
        v5 = json.loads(
            (ROOT / "docs/evidence/v5/qualification.json").read_text(encoding="utf-8")
        )
        v6 = json.loads(
            (ROOT / "docs/evidence/v6/qualification.json").read_text(encoding="utf-8")
        )
        self.assertEqual(v5["candidate"]["version"], "5.0.0")
        self.assertEqual(v6["version"], "6.0.0-dev")
        self.assertFalse(v6["evidencePolicy"]["v5ResultsPromoted"])

    def test_baseline_manifest_and_capture_matrix_are_current(self) -> None:
        subprocess.run(
            ["python3", "scripts/capture_v6_baseline.py", "--check"],
            cwd=ROOT,
            check=True,
        )
        manifest = json.loads(
            (ROOT / "docs/evidence/v6/baseline/manifest.json").read_text(
                encoding="utf-8"
            )
        )
        captures = manifest["captures"]
        self.assertEqual(len(captures), 19)
        self.assertEqual(
            {(entry["layer"], entry["scalePercent"]) for entry in captures},
            {
                ("artwork", 100),
                ("plasma", 100),
                ("plasma", 140),
                ("qt", 100),
                ("qt", 140),
                ("session", 100),
            },
        )
        for entry in captures:
            path = ROOT / "docs/evidence/v6/baseline" / entry["file"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry["sha256"])
            self.assertEqual(entry["v6Result"], "pending")

    def test_every_v6_result_starts_pending_or_blocked(self) -> None:
        qualification = json.loads(
            (ROOT / "docs/evidence/v6/qualification.json").read_text(encoding="utf-8")
        )
        statuses = {
            case["status"]
            for group in ("automatedCases", "liveCases")
            for case in qualification[group]
        }
        self.assertLessEqual(statuses, {"pending", "blocked"})
        self.assertIn("pending", statuses)
        self.assertIn("blocked", statuses)

    def test_visual_scorecard_covers_every_required_category(self) -> None:
        scorecard = json.loads(
            (ROOT / "docs/evidence/v6/visual-scorecard.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            set(scorecard["categories"]),
            {
                "hierarchy",
                "stateClarity",
                "cohesion",
                "branding",
                "density",
                "motion",
                "accessibility",
                "fallbackBehavior",
            },
        )
        for category in scorecard["categories"].values():
            self.assertGreaterEqual(category["v6Score"], 4)
            self.assertEqual(category["status"], "reviewed-prototype")
            self.assertEqual(category["evidence"], "north-star/manifest.json")


if __name__ == "__main__":
    unittest.main()
