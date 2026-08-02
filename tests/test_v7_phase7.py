from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads(
    (ROOT / "design/v7-diagnostics-contract.json").read_text(encoding="utf-8")
)
EVIDENCE = json.loads(
    (ROOT / "docs/evidence/v7/diagnostics/phase7.json").read_text(encoding="utf-8")
)


class V7PhaseSevenTests(unittest.TestCase):
    def test_doctor_covers_complete_active_state_and_provenance(self) -> None:
        source = (ROOT / "tools/noxforge-doctor").read_text(encoding="utf-8")
        for key in (
            "qtStyle",
            "colorScheme",
            "icons",
            "soundTheme",
            "plasmaStyle",
            "aurorae",
            "kwinSwitcher",
            "wallpaper",
            "criticalIcons",
            "provenance",
        ):
            self.assertIn(key, source)
        self.assertIn("mixedVersions", source)
        self.assertTrue(CONTRACT["doctor"]["readOnly"])

    def test_doctor_uses_kscreen_runtime_and_never_qt_scale_factor(self) -> None:
        source = (ROOT / "tools/noxforge-doctor").read_text(encoding="utf-8")
        self.assertIn("kscreen-doctor", source)
        self.assertIn(CONTRACT["doctor"]["displayScaleSource"], source)
        self.assertNotIn(CONTRACT["doctor"]["forbiddenScaleSource"], source)

    def test_sound_check_uses_the_documented_pinned_policy(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/generate_sound_theme.py", "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("pinned FFmpeg byte equality", result.stdout)
        self.assertIn(CONTRACT["soundReproducibility"]["pinnedFfmpegVersion"], result.stdout)
        self.assertFalse(CONTRACT["soundReproducibility"]["blindHostRegenerationAllowed"])

    def test_release_gate_separates_environment_and_repository_failures(self) -> None:
        source = (ROOT / "scripts/release-check.py").read_text(encoding="utf-8")
        self.assertIn("environment preflight failed", source)
        self.assertIn("repository gate failed after environment preflight", source)
        self.assertIn("scripts/run_python_tests.py", source)

    def test_python_gate_counts_come_from_actual_runner_result(self) -> None:
        runner = (ROOT / "scripts/run_python_tests.py").read_text(encoding="utf-8")
        for fragment in ("result.testsRun", "len(result.skipped)", "result.wasSuccessful()"):
            self.assertIn(fragment, runner)
        for stale_total in ("106 active", "120 active", "124 active", "130 active", "136 active"):
            self.assertNotIn(stale_total, runner)

    def test_phase_seven_evidence_keeps_live_checks_pending(self) -> None:
        self.assertEqual(EVIDENCE["result"], "passed")
        self.assertFalse(EVIDENCE["liveQualification"]["qualifiesLiveSession"])
        self.assertEqual(EVIDENCE["liveQualification"]["status"], "pending")


if __name__ == "__main__":
    unittest.main()
