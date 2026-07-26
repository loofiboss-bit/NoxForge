from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/release.yml"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"


class ReleaseWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = WORKFLOW.read_text(encoding="utf-8")
        self.ci_workflow = CI_WORKFLOW.read_text(encoding="utf-8")

    def test_javascript_actions_use_node24_compatible_majors(self) -> None:
        combined = self.ci_workflow + self.workflow
        self.assertNotIn("actions/checkout@v4", combined)
        self.assertNotIn("actions/setup-python@v5", combined)
        self.assertEqual(combined.count("actions/checkout@v7"), 4)
        self.assertEqual(combined.count("actions/setup-python@v7"), 1)

    def test_release_metadata_is_selected_from_the_requested_version(self) -> None:
        self.assertNotIn("docs/evidence/v3/", self.workflow)
        self.assertNotIn("--notes-file docs/releases/v3.0.0.md", self.workflow)
        self.assertIn('evidence_dir="docs/evidence/v${major}"', self.workflow)
        self.assertIn('notes_file="docs/releases/v${version}.md"', self.workflow)
        self.assertIn('manifest.get("releaseState") != "release"', self.workflow)
        self.assertIn('candidate.get("sourceRef") != f"v{version}"', self.workflow)
        self.assertNotIn('candidate.get("sourceCommit") != os.environ["GITHUB_SHA"]', self.workflow)
        self.assertIn('re.fullmatch(r"[0-9a-f]{40}"', self.workflow)
        self.assertIn('candidate.get("worktreeDirty") is not False', self.workflow)
        self.assertIn('grep -Fqx "Version: ${version}"', self.workflow)
        self.assertIn('evidence["candidate"]["sourceCommit"] = os.environ["GITHUB_SHA"]', self.workflow)
        self.assertIn("Commit: {os.environ['GITHUB_SHA']}", self.workflow)

    def test_public_release_refuses_development_versions(self) -> None:
        self.assertIn("Public releases require a stable VERSION", self.workflow)
        self.assertRegex(
            self.workflow,
            re.compile(r"\^\[0-9\]\+\\\.\[0-9\]\+\\\.\[0-9\]\+\$"),
        )

    def test_build_and_publish_jobs_require_exactly_six_nonempty_assets(self) -> None:
        self.assertGreaterEqual(
            self.workflow.count('test "${#assets[@]}" -eq 6'),
            2,
        )
        for name in (
            "qualification.json",
            "automated-gate.md",
            "SHA256SUMS",
            "noxforge-${version}.tar.xz",
        ):
            self.assertIn(name, self.workflow)
        self.assertIn("sha256sum --check SHA256SUMS", self.workflow)

    def test_release_bundle_remains_available_to_the_publish_job(self) -> None:
        self.assertIn("uses: actions/upload-artifact@v4", self.workflow)
        self.assertIn("uses: actions/download-artifact@v4", self.workflow)
        self.assertIn("retention-days: 3", self.workflow)


if __name__ == "__main__":
    unittest.main()
