from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/release.yml"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"
RELEASE_MANIFEST = ROOT / "distribution/release-manifest.json"


class ReleaseWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = WORKFLOW.read_text(encoding="utf-8")
        self.ci_workflow = CI_WORKFLOW.read_text(encoding="utf-8")
        self.manifest = json.loads(RELEASE_MANIFEST.read_text(encoding="utf-8"))

    def test_javascript_actions_use_node24_compatible_majors(self) -> None:
        combined = self.ci_workflow + self.workflow
        self.assertNotIn("actions/checkout@v4", combined)
        self.assertNotIn("actions/setup-python@v5", combined)
        self.assertEqual(combined.count("actions/checkout@v7"), 4)
        self.assertEqual(combined.count("actions/setup-python@v7"), 1)

    def test_release_metadata_is_selected_from_the_manifest_and_tag(self) -> None:
        self.assertNotIn("docs/evidence/v3/", self.workflow)
        self.assertNotIn("--notes-file docs/releases/v3.0.0.md", self.workflow)
        self.assertIn("distribution/release-manifest.json", self.workflow)
        self.assertIn("manifest['release']['stableVersion']", self.workflow)
        self.assertIn("manifest['evidence']['activeRoot']", self.workflow)
        self.assertIn("for artifact in manifest['artifacts']", self.workflow)
        self.assertIn("source_commit=subprocess.check_output", self.workflow)
        self.assertIn("qualification['releaseState']='release'", self.workflow)
        self.assertIn("'sourceCommit': source_commit", self.workflow)
        self.assertIn('git\', \'-c\', \'safe.directory=\' + str(Path.cwd()), \'describe\', \'--tags\', \'--exact-match\'', self.workflow)
        self.assertIn('docs/releases/v${version}.md', self.workflow)

    def test_public_release_refuses_development_versions(self) -> None:
        self.assertIn("public releases require stable VERSION", self.workflow)
        self.assertIn("re.fullmatch(r'[0-9]+\\.[0-9]+\\.[0-9]+'", self.workflow)

    def test_build_and_publish_jobs_follow_manifest_artifacts(self) -> None:
        self.assertNotIn('test "${#assets[@]}" -eq 6', self.workflow)
        self.assertIn("for artifact in manifest['artifacts']", self.workflow)
        self.assertIn("required={item['filename'] for item in m['artifacts']}", self.workflow)
        filenames = {item["filename"] for item in self.manifest["artifacts"]}
        self.assertGreater(len(filenames), 6)
        self.assertEqual(len(filenames), len(self.manifest["artifacts"]))
        for name in ("qualification.json", "automated-gate.md", "SHA256SUMS"):
            self.assertIn(name, filenames if name != "SHA256SUMS" else self.workflow)
        self.assertIn("sha256sum --check SHA256SUMS", self.workflow)

    def test_release_bundle_remains_available_to_the_publish_job(self) -> None:
        self.assertIn("uses: actions/upload-artifact@v4", self.workflow)
        self.assertIn("uses: actions/download-artifact@v4", self.workflow)
        self.assertIn("retention-days: 3", self.workflow)


if __name__ == "__main__":
    unittest.main()
