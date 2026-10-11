from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if (ROOT / "VERSION").read_text(encoding="utf-8").strip() != "6.0.0":
    raise unittest.SkipTest("historical v6 source-bound tests")


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
        self.assertIn("virtual framebuffer", notes)
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

    def test_release_manifest_preserves_contract_and_exact_candidate_lineage(self) -> None:
        manifest = json.loads(
            (ROOT / "docs/evidence/v6/qualification.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["schemaVersion"], 2)
        self.assertEqual(manifest["releaseState"], "release")
        self.assertEqual(manifest["candidate"]["version"], "6.0.0")
        self.assertRegex(manifest["candidate"]["sourceCommit"], r"^[0-9a-f]{40}$")
        self.assertFalse(manifest["candidate"]["worktreeDirty"])
        self.assertEqual(manifest["releaseContract"]["assetCount"], 6)
        self.assertEqual(len(manifest["candidate"]["artifacts"]), 6)
        self.assertNotIn("releaseBlockers", manifest)

    def test_public_release_workflow_remains_exact_tag_and_six_asset_gated(self) -> None:
        workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        self.assertIn('test "${{ inputs.ref }}" = "v${version}"', workflow)
        self.assertIn("--verify-tag", workflow)
        self.assertGreaterEqual(workflow.count('test "${#assets[@]}" -eq 6'), 2)
        self.assertIn("candidate.get(\"sourceCommit\") != expected_commit", workflow)

    def test_phase_plan_records_public_release_and_copr_blocker(self) -> None:
        plan = (ROOT / "docs/NOXFORGE_V6_PLAN.md").read_text(encoding="utf-8")
        phase = plan.split("## Phase 8", 1)[1].split("## Cross-phase", 1)[0]
        self.assertIn("**Publication status (2026-08-01; COPR pending):**", phase)
        self.assertIn("141 Python tests", phase)
        for gate in ("v6.0.0", "30692016393", "10802161", "rpm -V"):
            self.assertIn(gate, phase)
        self.assertIn("final Phase 8 blocker", phase)

    def test_public_readback_records_every_release_surface(self) -> None:
        evidence = json.loads(
            (ROOT / "docs/evidence/v6/public-readback.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(evidence["schemaVersion"], 1)
        self.assertEqual(evidence["release"]["tag"], "v6.0.0")
        self.assertEqual(
            evidence["release"]["sourceCommit"],
            "d6c4e3c5584b9fdd61c7bb3ae9b3b693f03e67f6",
        )
        self.assertEqual(evidence["github"]["assetCount"], 6)
        self.assertTrue(evidence["github"]["checksumsVerified"])
        self.assertEqual(evidence["copr"]["state"], "pending")
        self.assertEqual(evidence["copr"]["buildId"], 10802161)
        self.assertEqual(evidence["copr"]["publicRepositoryReadback"], "blocked")
        self.assertEqual(evidence["installation"]["rpmVerify"], "passed")
        self.assertEqual(evidence["installation"]["doctorStatus"], "ok")
        self.assertEqual(evidence["installation"]["removal"], "passed")
        self.assertTrue(evidence["installation"]["settingsPreserved"])


if __name__ == "__main__":
    unittest.main()
