from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V6PhaseEightTests(unittest.TestCase):
    def test_stable_version_is_synchronized_across_all_consumers(self) -> None:
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), "6.0.0")
        subprocess.run(
            ["python3", "scripts/sync_version.py", "--check"],
            cwd=ROOT,
            check=True,
        )
        spec = (ROOT / "packaging/noxforge.spec").read_text(encoding="utf-8")
        self.assertIn("%global upstream_version 6.0.0", spec)
        self.assertIn("Version:        6.0.0", spec)

    def test_readme_uses_exact_v6_outputs_without_live_overclaim(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        images = (
            "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/previews/fullscreenpreview.png",
            "docs/evidence/v6/qt-motion/state-100.png",
            "docs/evidence/v6/plasma-shell/plasma-style-atlas-100pct.png",
            "docs/evidence/v6/session/sddm-resolution-2560x1440.png",
            "docs/evidence/v6/edge-polish/icon-priority.png",
        )
        for relative in images:
            self.assertIn(relative, readme)
            self.assertTrue((ROOT / relative).is_file())
        self.assertIn("not live desktop or compositor evidence", readme)
        self.assertIn("not relabeled as a live Plasma", readme)

    def test_release_notes_and_user_guides_cover_v6_and_reduced_motion(self) -> None:
        notes = (ROOT / "docs/releases/v6.0.0.md").read_text(encoding="utf-8")
        self.assertIn("# NoxForge 6.0.0", notes)
        self.assertIn("Kinetic Precision", notes)
        self.assertIn("141 Python tests", notes)
        self.assertIn("no authorized v6 tag", notes)
        for relative in (
            "docs/QUICKSTART.md",
            "docs/INSTALL_FEDORA.md",
            "docs/COMPATIBILITY.md",
            "docs/TROUBLESHOOTING.md",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("v6" if relative != "docs/QUICKSTART.md" else "6.0", text)
        self.assertIn(
            "zero duration",
            (ROOT / "docs/INSTALL_FEDORA.md").read_text(encoding="utf-8"),
        )

    def test_candidate_manifest_preserves_release_contract_and_blockers(self) -> None:
        manifest = json.loads(
            (ROOT / "docs/evidence/v6/qualification.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["schemaVersion"], 2)
        self.assertEqual(manifest["releaseState"], "candidate")
        self.assertEqual(manifest["candidate"]["version"], "6.0.0")
        self.assertIsNone(manifest["candidate"]["sourceCommit"])
        self.assertIsNone(manifest["candidate"]["worktreeDirty"])
        self.assertEqual(manifest["releaseContract"]["assetCount"], 6)
        self.assertEqual(len(manifest["candidate"]["artifacts"]), 6)
        self.assertGreaterEqual(len(manifest["releaseBlockers"]), 4)

    def test_public_release_workflow_remains_exact_tag_and_six_asset_gated(self) -> None:
        workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        self.assertIn('test "${{ inputs.ref }}" = "v${version}"', workflow)
        self.assertIn("--verify-tag", workflow)
        self.assertGreaterEqual(workflow.count('test "${#assets[@]}" -eq 6'), 2)
        self.assertIn("candidate.get(\"sourceCommit\") != expected_commit", workflow)

    def test_phase_plan_records_local_completion_and_public_blockers(self) -> None:
        plan = (ROOT / "docs/NOXFORGE_V6_PLAN.md").read_text(encoding="utf-8")
        phase = plan.split("## Phase 8", 1)[1].split("## Cross-phase", 1)[0]
        self.assertIn("**Local outcome (2026-07-30; Phase 8 remains incomplete):**", phase)
        self.assertIn("141 Python tests", phase)
        self.assertIn("no public release is claimed", phase)
        for blocker in ("tag", "GitHub Release", "COPR", "installation"):
            self.assertIn(blocker, phase)


if __name__ == "__main__":
    unittest.main()
