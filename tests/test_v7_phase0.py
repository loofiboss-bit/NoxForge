from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V7PhaseZeroTests(unittest.TestCase):
    def test_v7_is_the_single_active_authority(self) -> None:
        index = (ROOT / "docs/IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
        plan = (ROOT / "docs/NOXFORGE_V7_PLAN.md").read_text(encoding="utf-8")
        self.assertIn("NOXFORGE_V7_PLAN.md", index)
        self.assertIn("Active phase-gated implementation authority", plan)
        self.assertIn("Operational Precision", plan)
        self.assertIn("7.0.0-dev", plan)
        self.assertIn("pending P0", plan)

    def test_development_version_is_synchronized_without_rewriting_v6(self) -> None:
        self.assertEqual(
            (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
            "7.0.0-dev",
        )
        subprocess.run(
            ["python3", "scripts/sync_version.py", "--check"],
            cwd=ROOT,
            check=True,
        )
        v6 = json.loads(
            (ROOT / "docs/evidence/v6/qualification.json").read_text(
                encoding="utf-8"
            )
        )
        v7 = json.loads(
            (ROOT / "docs/evidence/v7/qualification.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(v6["candidate"]["version"], "6.0.0")
        self.assertEqual(v6["candidate"]["sourceRef"], "v6.0.0")
        self.assertEqual(v7["candidate"]["version"], "7.0.0-dev")
        self.assertEqual(v7["releaseState"], "development")
        self.assertFalse(v7["releaseReady"])

    def test_v6_public_closure_is_current_and_complete(self) -> None:
        evidence = json.loads(
            (ROOT / "docs/evidence/v6/public-readback.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(evidence["release"]["tag"], "v6.0.0")
        self.assertEqual(
            evidence["release"]["sourceCommit"],
            "d6c4e3c5584b9fdd61c7bb3ae9b3b693f03e67f6",
        )
        self.assertEqual(evidence["github"]["assetCount"], 6)
        self.assertTrue(evidence["github"]["checksumsVerified"])
        self.assertEqual(evidence["copr"]["buildId"], 10802161)
        self.assertEqual(evidence["copr"]["state"], "succeeded")
        self.assertEqual(evidence["copr"]["latestSucceededVersion"], "6.0.0-1")
        self.assertEqual(evidence["copr"]["publicRepositoryReadback"], "passed")

    def test_baseline_records_results_and_known_issue_classifications(self) -> None:
        baseline = json.loads(
            (ROOT / "docs/evidence/v7/phase0-baseline.json").read_text(
                encoding="utf-8"
            )
        )
        checks = {entry["command"]: entry for entry in baseline["baselineChecks"]}
        discovered = checks[
            "python3 -m unittest discover -s tests -p 'test_*.py' -v"
        ]
        self.assertEqual(discovered["testsDiscovered"], 147)
        self.assertEqual(discovered["testsFailed"], 0)
        self.assertEqual(
            checks["python3 scripts/generate_sound_theme.py --check"]["status"],
            "passed",
        )
        issues = {entry["id"]: entry for entry in baseline["issues"]}
        self.assertEqual(issues["aurorae-maximized-width"]["status"], "failing")
        self.assertEqual(issues["core-icon-resolution"]["status"], "failing")
        self.assertEqual(
            issues["ogg-cross-toolchain-reproducibility"]["status"],
            "uncertain",
        )
        self.assertEqual(issues["test-count-reporting"]["status"], "failing")

    def test_required_live_matrix_keeps_p0_failures_open(self) -> None:
        evidence = json.loads(
            (ROOT / "docs/evidence/v7/qualification.json").read_text(
                encoding="utf-8"
            )
        )
        live = {entry["id"]: entry for entry in evidence["liveCases"]}
        scaling = live["aurorae-maximized-scaling"]
        self.assertIn(scaling["status"], {"failed", "pending"})
        self.assertEqual(scaling["scales"], [100, 125, 140, 150, 175, 200])
        self.assertEqual(scaling["mixedOutputs"], ["100+140", "100+200"])
        self.assertIn(live["core-icon-visibility"]["status"], {"failed", "pending"})
        self.assertTrue(evidence["evidencePolicy"]["pendingP0BlocksReleaseReadiness"])

    def test_phase_zero_gate_preserves_the_live_boundary(self) -> None:
        gate = (ROOT / "docs/evidence/v7/phase0-gate.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Result: passed", gate)
        self.assertIn("106 passed", gate)
        self.assertIn("9 skipped", gate)
        self.assertIn("21 passed", gate)
        self.assertIn("V7 is not release-ready", " ".join(gate.split()))
        self.assertIn("no theme was installed or applied", gate)


if __name__ == "__main__":
    unittest.main()
