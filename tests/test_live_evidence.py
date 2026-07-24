from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/evidence/v3/qualification.json"
REQUIRED_CASES = {
    "global-theme-discovery-apply",
    "existing-panel-preservation",
    "compact-layout-all-panel-edges",
    "plasma-popups-blur-on-off",
    "qt-controls-100-140",
    "keyboard-navigation-focus",
    "rtl-shell",
    "no-visible-fallback-artwork",
    "aurorae-window-states",
    "alt-tab-long-multiple-empty",
    "icon-required-sizes",
    "cursor-100-140-200",
    "sound-routing-volume",
    "splash-logout-lock",
    "multi-monitor-placement",
    "sddm-login-flows",
}


class LiveEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_records_candidate_and_environment(self) -> None:
        self.assertEqual(self.manifest["schemaVersion"], 1)
        candidate = self.manifest["candidate"]
        self.assertEqual(
            candidate["version"],
            (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        )
        self.assertRegex(candidate["sourceCommit"], r"^[0-9a-f]{40}$")
        for field in (
            "fedora",
            "plasma",
            "kwin",
            "frameworks",
            "qt",
            "kernel",
            "session",
            "displayScale",
            "layout",
            "panelEdge",
            "blur",
            "rtl",
        ):
            self.assertTrue(self.manifest["environment"][field])

    def test_every_live_case_has_an_honest_result(self) -> None:
        cases = self.manifest["liveCases"]
        self.assertEqual({case["id"] for case in cases}, REQUIRED_CASES)
        self.assertEqual(len(cases), len(REQUIRED_CASES))
        allowed = {"passed", "failed", "blocked", "not-applicable"}
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertIn(case["result"], allowed)
                self.assertTrue(case["observation"])
                if case["result"] == "passed":
                    self.assertTrue(case["evidence"])
                    self.assertTrue((MANIFEST.parent / case["evidence"]).is_file())
                elif case["result"] == "blocked":
                    self.assertTrue(case["blocker"])
                elif case["result"] == "failed":
                    self.assertTrue(case["evidence"])

    def test_automated_evidence_is_not_used_as_live_evidence(self) -> None:
        automated = self.manifest["automatedEvidence"]
        self.assertEqual(automated["result"], "passed")
        self.assertTrue((MANIFEST.parent / automated["evidence"]).is_file())
        self.assertTrue(
            all(case["evidence"] != automated["evidence"] for case in self.manifest["liveCases"])
        )


if __name__ == "__main__":
    unittest.main()
