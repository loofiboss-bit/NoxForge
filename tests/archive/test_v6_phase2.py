from __future__ import annotations

import hashlib
import json
import os
import subprocess
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if (ROOT / "VERSION").read_text(encoding="utf-8").strip() != "6.0.0":
    raise unittest.SkipTest("historical v6 source-bound tests")
SVG = "{http://www.w3.org/2000/svg}"


class V6PhaseTwoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(
            (ROOT / "design/artwork-contract.json").read_text(encoding="utf-8")
        )
        cls.evidence = json.loads(
            (ROOT / "docs/evidence/artwork-contact-sheets.json").read_text(
                encoding="utf-8"
            )
        )

    def test_brand_masters_and_physical_copies_are_consistent(self) -> None:
        brand = self.contract["brand"]
        self.assertEqual(self.contract["schemaVersion"], 2)
        self.assertEqual(brand["opticalSizes"], [16, 24, 48, 128, 512])
        semantic = ET.parse(ROOT / brand["source"]).getroot()
        monochrome = ET.parse(ROOT / brand["monochromeSource"]).getroot()
        lockup = ET.parse(ROOT / brand["lockupSource"]).getroot()
        self.assertEqual(semantic.get("viewBox"), brand["viewBox"])
        self.assertEqual(monochrome.get("viewBox"), brand["viewBox"])
        self.assertEqual(lockup.get("viewBox"), brand["lockupViewBox"])
        self.assertEqual(
            semantic.find(f".//{SVG}path").get("d"),
            monochrome.find(f".//{SVG}path").get("d"),
        )
        self.assertFalse(lockup.findall(f".//{SVG}text"))
        for kind, copies in brand["physicalCopies"].items():
            master = ROOT / (
                brand["source"] if kind == "mark" else brand["lockupSource"]
            )
            for relative in copies:
                self.assertEqual((ROOT / relative).read_bytes(), master.read_bytes())

    def test_wallpapers_are_independent_editable_compositions(self) -> None:
        wallpapers = self.contract["wallpapers"]
        self.assertEqual(set(wallpapers), {"16:9", "ultrawide"})
        sources = [ROOT / details["source"] for details in wallpapers.values()]
        self.assertEqual(len({source.read_bytes() for source in sources}), 2)
        for details in wallpapers.values():
            self.assertTrue(details["original"])
            self.assertTrue(details["editable"])
            quiet = details["quietWorkspace"]
            self.assertGreaterEqual(quiet["x"], 1000)
            self.assertGreaterEqual(quiet["width"], 1200)
            for output in details["outputs"]:
                self.assertTrue(
                    (
                        ROOT
                        / "wallpapers/NoxForge/contents/images"
                        / f"{output}.png"
                    ).is_file()
                )

    def test_optical_and_contact_sheet_evidence_is_source_bound(self) -> None:
        self.assertEqual(self.evidence["schemaVersion"], 2)
        self.assertEqual(self.evidence["phase"], 2)
        self.assertEqual(self.evidence["reviewStatus"], "reviewed-offscreen")
        self.assertFalse(self.evidence["liveEvidence"])
        self.assertEqual(
            set(self.evidence["brandOpticalRenders"]),
            {"16", "24", "48", "128", "512"},
        )
        self.assertEqual(len(self.evidence["sheets"]), 4)
        for relative, expected in {
            **self.evidence["sources"],
            **self.evidence["sheets"],
        }.items():
            self.assertEqual(
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
                expected,
            )

    def test_brand_and_wallpaper_generation_is_byte_stable(self) -> None:
        for command in (
            ["python3", "scripts/generate_design_system.py", "--check"],
            ["python3", "scripts/render_wallpaper.py", "--check"],
            ["python3", "scripts/render_artwork_evidence.py", "--check"],
            ["python3", "scripts/render_v6_previews.py", "--check"],
        ):
            subprocess.run(command, cwd=ROOT, check=True)

    def test_sddm_preview_is_timezone_independent(self) -> None:
        for timezone in ("UTC", "Europe/Stockholm"):
            environment = {**os.environ, "TZ": timezone}
            subprocess.run(
                ["python3", "scripts/render_v6_previews.py", "--check"],
                cwd=ROOT,
                env=environment,
                check=True,
            )

    def test_readme_and_session_brand_surfaces_use_v6_artwork(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        splash = (
            ROOT
            / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/splash/Splash.qml"
        ).read_text(encoding="utf-8")
        sddm = (ROOT / "sddm/NoxForge/Main.qml").read_text(encoding="utf-8")
        self.assertIn("Kinetic Precision", readme)
        self.assertIn(
            "wallpapers/NoxForge/contents/images/2560x1440.png",
            readme,
        )
        self.assertIn('source: "NoxForgeMark.svg"', splash)
        self.assertIn('text: "NOXFORGE"', splash)
        self.assertIn('source: "NoxForgeLockup.svg"', sddm)
        preview = json.loads(
            (ROOT / "docs/evidence/v6/brand/preview-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(preview["kind"], "authentic-offscreen-preview")
        self.assertFalse(preview["liveEvidence"])
        for details in preview["outputs"].values():
            path = ROOT / details["path"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), details["sha256"])


if __name__ == "__main__":
    unittest.main()
