from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V6PhaseThreeTests(unittest.TestCase):
    def test_motion_controller_uses_one_bounded_public_timer(self) -> None:
        header = (ROOT / "src/style/noxforgemotion.h").read_text(encoding="utf-8")
        source = (ROOT / "src/style/noxforgemotion.cpp").read_text(encoding="utf-8")
        style = (ROOT / "src/style/noxforgestyle.cpp").read_text(encoding="utf-8")
        self.assertIn("QBasicTimer m_timer", header)
        self.assertIn("void NoxForgeMotion::updateTimer()", source)
        self.assertIn("m_timer.stop()", source)
        self.assertIn("m_timer.start(16, Qt::PreciseTimer, this)", source)
        self.assertIn("QApplication::styleHints()->useHoverEffects()", style)
        self.assertIn("SH_Widget_Animation_Duration", style)
        self.assertNotIn("private/", header + source + style)
        self.assertNotIn("QStyleAnimation", header + source + style)

    def test_event_and_reduced_motion_probe_is_wired_into_ctest(self) -> None:
        probe = (ROOT / "tests/qt/motion_probe.cpp").read_text(encoding="utf-8")
        cmake = (ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
        for state in (
            "sendEnter",
            "FocusIn",
            "MouseButtonPress",
            "MouseButtonRelease",
            "setEnabled(false)",
            "delete button",
            "setDurationScale(0.0)",
            "timerActive()",
        ):
            self.assertIn(state, probe)
        self.assertIn("motion-controller-lifecycle", cmake)
        self.assertIn("NOXFORGE_ENABLE_SANITIZERS", cmake)
        self.assertIn("-fsanitize=address,undefined", cmake)

    def test_native_motion_honors_platform_policy_and_semantic_input(self) -> None:
        source = (ROOT / "src/style/noxforgemotion.cpp").read_text(encoding="utf-8")
        header = (ROOT / "src/style/noxforgemotion.h").read_text(encoding="utf-8")
        style = (ROOT / "src/style/noxforgestyle.cpp").read_text(encoding="utf-8")
        probe = (ROOT / "tests/qt/motion_probe.cpp").read_text(encoding="utf-8")
        self.assertIn('QStringLiteral("AnimationDurationFactor")', style)
        self.assertIn("QStandardPaths::GenericConfigLocation", style)
        self.assertIn("Qt::LeftButton", source)
        self.assertIn("Qt::Key_Space", source)
        self.assertIn("Qt::Key_Return", source)
        self.assertIn("busyIndicatorDelayMs = 150", header)
        self.assertIn("busyIndicatorMinimumVisibleMs = 300", header)
        self.assertIn("showsBusyIndicator", source + probe)

    def test_tab_hover_is_derived_per_painted_tab(self) -> None:
        style = (ROOT / "src/style/noxforgestyle.cpp").read_text(encoding="utf-8")
        tab_shape = style.split("case CE_TabBarTabShape:", 1)[1].split(
            "case CE_HeaderSection:", 1
        )[0]
        self.assertIn("State_MouseOver", tab_shape)
        self.assertNotIn("motionValue", tab_shape)

    def test_motion_evidence_is_source_bound_and_byte_stable(self) -> None:
        subprocess.run(
            ["python3", "scripts/render_v6_motion_evidence.py", "--check"],
            cwd=ROOT,
            check=True,
        )
        manifest = json.loads(
            (ROOT / "docs/evidence/v6/qt-motion/manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["phase"], 3)
        self.assertFalse(manifest["liveEvidence"])
        self.assertEqual(manifest["deterministicProgress"], [0, 50, 100])
        self.assertEqual([render["progressPercent"] for render in manifest["renders"]],
                         [0, 50, 100])
        hashes = set()
        for render in manifest["renders"]:
            path = ROOT / render["path"]
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest, render["sha256"])
            hashes.add(digest)
        self.assertEqual(len(hashes), 3)

    def test_motion_evidence_uses_an_isolated_render_environment(self) -> None:
        script = (ROOT / "scripts/render_v6_motion_evidence.py").read_text(
            encoding="utf-8"
        )
        for variable in ("HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "LC_ALL"):
            self.assertIn(f'"{variable}"', script)
        self.assertIn('"QT_QPA_PLATFORM": "offscreen"', script)

    def test_performance_medians_remain_within_v5_budget(self) -> None:
        subprocess.run(
            ["python3", "scripts/measure_v6_phase3_performance.py", "--check"],
            cwd=ROOT,
            check=True,
        )
        evidence = json.loads(
            (ROOT / "docs/evidence/v6/qt-motion/performance.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            evidence["baselineCommit"],
            "6a113e71980d106c38a2bbdece6df171c0ae9ed3",
        )
        self.assertFalse(evidence["idleTimerExpected"])
        for metric in evidence["metrics"].values():
            self.assertLessEqual(metric["ratio"], 1.10)
            self.assertEqual(metric["result"], "passed")

    def test_phase_gate_runs_motion_generation_and_sanitizers(self) -> None:
        gate = (ROOT / "scripts/release-check.py").read_text(encoding="utf-8")
        self.assertIn("render_v6_motion_evidence.py", gate)
        self.assertIn("measure_v6_phase3_performance.py", gate)
        self.assertIn("check_v6_phase3_sanitizers.py", gate)
        plan = (ROOT / "docs/NOXFORGE_V6_PLAN.md").read_text(encoding="utf-8")
        phase = plan.split("## Phase 3", 1)[1].split("## Phase 4", 1)[0]
        self.assertIn("**Outcome (2026-07-30):**", phase)
        self.assertIn("111 Python tests", phase)
        self.assertIn("19 CTest", phase)


if __name__ == "__main__":
    unittest.main()
