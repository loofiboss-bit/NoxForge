from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"
MANIFEST_FILE = ROOT / "distribution/release-manifest.json"
TOKENS_FILE = ROOT / "design/tokens.json"
QML_VARIANTS_FILE = ROOT / "design/qml-variants.json"


class RollingReleaseContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.version = VERSION_FILE.read_text(encoding="utf-8").strip()
        cls.manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
        cls.tokens = json.loads(TOKENS_FILE.read_text(encoding="utf-8"))

    def test_manifest_authority_and_version(self) -> None:
        self.assertEqual(
            self.manifest["release"]["version"],
            self.version,
            "manifest release version must match VERSION file",
        )
        plan_path = ROOT / self.manifest["release"]["activePlan"]
        self.assertTrue(plan_path.is_file(), f"active plan file must exist: {plan_path}")
        self.assertTrue(
            self.manifest["evidence"]["activeRoot"].startswith("docs/evidence/"),
            "evidence activeRoot must be under docs/evidence/",
        )
        baseline = self.manifest["release"]["baseline"]
        self.assertTrue(baseline["version"], "baseline version must be set")
        self.assertTrue(baseline["commit"], "baseline commit must be set")

    def test_tokens_schema_and_reduced_motion(self) -> None:
        self.assertGreaterEqual(self.tokens["schemaVersion"], 12)
        self.assertEqual(self.tokens["version"], self.version)

        motion = self.tokens.get("motion", {})
        reduced = motion.get("reducedMotion", {})
        self.assertEqual(reduced.get("policy"), "respect-system")
        self.assertEqual(reduced.get("shakeReplacement"), "edge-flash")

        accents = self.tokens.get("accents", {})
        custom = accents.get("custom", {})
        self.assertTrue(custom.get("enabled"))
        self.assertGreaterEqual(custom.get("minContrastOnSurface", 0), 4.5)
        self.assertGreaterEqual(custom.get("minContrastOnObsidian", 0), 4.5)

    def test_qml_variants_contract(self) -> None:
        self.assertTrue(QML_VARIANTS_FILE.is_file())
        qml_cfg = json.loads(QML_VARIANTS_FILE.read_text(encoding="utf-8"))
        targets = qml_cfg.get("targets", [])
        self.assertGreaterEqual(len(targets), 3)

        for target in targets:
            source = ROOT / target["source"]
            self.assertTrue(source.is_file(), f"source missing: {source}")
            header = f"// GENERATED from {target['source']} — do not edit directly\n"
            source_content = source.read_text(encoding="utf-8")
            for out_rel in target["outputs"]:
                out_path = ROOT / out_rel
                self.assertTrue(out_path.is_file(), f"variant output missing: {out_path}")
                out_content = out_path.read_text(encoding="utf-8")
                self.assertEqual(
                    out_content,
                    header + source_content if not source_content.startswith(header) else source_content,
                    f"variant output {out_rel} drifted from {target['source']}",
                )

    def test_packaging_version_coherence(self) -> None:
        rpm_ver = self.version.replace("-", "~", 1)
        spec = (ROOT / "packaging/noxforge.spec").read_text(encoding="utf-8")
        self.assertIn(f"Version:        {rpm_ver}", spec)

        pkgbuild = (ROOT / "packaging/arch/PKGBUILD").read_text(encoding="utf-8")
        self.assertIn(f"pkgver={self.version}", pkgbuild)

        srcinfo = (ROOT / "packaging/arch/.SRCINFO").read_text(encoding="utf-8")
        self.assertIn(f"pkgver = {self.version}", srcinfo)

    def test_no_package_symlinks(self) -> None:
        package_dirs = [
            ROOT / "plasma/desktoptheme",
            ROOT / "look-and-feel",
            ROOT / "kwin/tabbox",
            ROOT / "aurorae",
            ROOT / "sddm",
            ROOT / "color-schemes",
            ROOT / "konsole",
        ]
        for pdir in package_dirs:
            if not pdir.exists():
                continue
            for item in pdir.rglob("*"):
                self.assertFalse(item.is_symlink(), f"Forbidden symlink in package: {item}")

    def test_doctor_schema_9_contract(self) -> None:
        import subprocess
        import sys

        doctor = ROOT / "tools/noxforge-doctor"
        res = subprocess.run(
            [sys.executable, str(doctor), "--root", str(ROOT), "--json"],
            capture_output=True,
            text=True,
            check=False,
            cwd=ROOT,
        )
        self.assertEqual(res.returncode, 0, f"doctor failed: {res.stderr}")
        report = json.loads(res.stdout)
        self.assertIn(report["schemaVersion"], (9, 10))
        self.assertIn("qmlVariantDrift", report)
        self.assertIn("reducedMotion", report)
        self.assertIn("customAccentContrast", report)
        self.assertIn("faceAuthApi", report)
        self.assertIn("versionCoherence", report)

        qml = report["qmlVariantDrift"]
        self.assertEqual(qml["status"], "ok")
        self.assertIn(qml["checked"], (6, 12))
        self.assertEqual(qml["drift"], [])

        motion = report["reducedMotion"]
        self.assertEqual(motion["status"], "ok")
        self.assertIn(motion["effective"], ("standard", "reduced"))

        coherence = report["versionCoherence"]
        self.assertEqual(coherence["status"], "coherent")


if __name__ == "__main__":
    unittest.main()
