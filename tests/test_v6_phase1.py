from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V6PhaseOneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tokens = json.loads(
            (ROOT / "design/tokens.json").read_text(encoding="utf-8")
        )
        cls.motion = json.loads(
            (ROOT / "design/motion-contract.json").read_text(encoding="utf-8")
        )
        cls.manifest = json.loads(
            (ROOT / "docs/evidence/v6/north-star/manifest.json").read_text(
                encoding="utf-8"
            )
        )

    def test_kinetic_precision_tokens_remove_broad_olive_selection(self) -> None:
        colors = self.tokens["colors"]
        self.assertEqual(self.tokens["schemaVersion"], 5)
        self.assertEqual(colors["background"], "#0E1318")
        self.assertEqual(colors["accent"], "#A3FF47")
        self.assertEqual(colors["surfaceSelected"], "#1E2B31")
        self.assertNotEqual(colors["surfaceSelected"], "#26361D")
        self.assertEqual(self.tokens["states"]["activeMarkerWidth"], 3)
        self.assertEqual(self.tokens["semanticRoles"]["focus"]["border"], "accent")
        self.assertEqual(
            self.tokens["semanticRoles"]["primaryAction"]["background"], "accent"
        )

    def test_surface_and_typography_hierarchies_are_complete(self) -> None:
        self.assertLessEqual(
            {"canvas", "sunken", "surface", "raised", "overlay"},
            set(self.tokens["semanticRoles"]),
        )
        self.assertEqual(
            set(self.tokens["typography"]["roles"]),
            {
                "displayClock",
                "surfaceTitle",
                "sectionTitle",
                "body",
                "controlLabel",
                "metadata",
                "microLabel",
            },
        )
        self.assertEqual(self.tokens["typography"]["family"], "system-ui")
        self.assertEqual(self.tokens["iconography"]["accentCoveragePercentMax"], 8)

    def test_motion_has_bounded_animated_and_reduced_outcomes(self) -> None:
        states = set(self.tokens["states"]["hierarchy"])
        self.assertLessEqual(states, set(self.motion["transitions"]))
        self.assertEqual(states, set(self.motion["reducedMotion"]["stateOutcomes"]))
        self.assertEqual(self.tokens["motion"]["busyCycleMs"], 900)
        self.assertEqual(self.motion["performance"]["maximumTravelPx"], 8)
        self.assertFalse(self.motion["policy"]["springAllowed"])
        self.assertFalse(self.motion["policy"]["focusIndicatorAnimated"])

    def test_north_star_lineage_and_scores_are_complete(self) -> None:
        self.assertTrue(self.manifest["prototype"])
        self.assertFalse(self.manifest["productionRuntime"])
        self.assertFalse(self.manifest["liveEvidence"])
        self.assertEqual(len(self.manifest["comparisons"]), 6)
        for comparison in self.manifest["comparisons"]:
            target = ROOT / "docs/evidence/v6/north-star" / comparison["file"]
            baseline = (
                ROOT / "docs/evidence/v6/north-star" / comparison["baseline"]
            ).resolve()
            self.assertEqual(
                hashlib.sha256(target.read_bytes()).hexdigest(),
                comparison["sha256"],
            )
            self.assertEqual(
                hashlib.sha256(baseline.read_bytes()).hexdigest(),
                comparison["baselineSha256"],
            )
            self.assertGreater(comparison["rootMeanSquareDifference"], 0)
        self.assertTrue(
            all(
                score >= 4
                for score in self.manifest["scorecard"]["scores"].values()
            )
        )

    def test_north_star_generation_is_byte_stable(self) -> None:
        subprocess.run(
            ["python3", "scripts/render_v6_north_star.py", "--check"],
            cwd=ROOT,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
