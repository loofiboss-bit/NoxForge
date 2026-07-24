from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCTOR = ROOT / "tools/noxforge-doctor"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
THEME_ID = "io.github.loofiboss.noxforge.desktop"


def write(path: Path, content: str = "present\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def stage_complete(root: Path, *, alternate_version: str | None = None) -> None:
    version = alternate_version or VERSION
    metadata = json.dumps({"KPlugin": {"Version": version}}) + "\n"
    desktop = (
        "[Desktop Entry]\n"
        f"X-KDE-PluginInfo-Version={version}\n"
    )
    sddm = f"[SddmGreeterTheme]\nVersion={version}\n"
    share = root / "usr/share"
    write(share / "noxforge/VERSION", VERSION + "\n")
    write(share / f"plasma/look-and-feel/{THEME_ID}/metadata.json", metadata)
    write(share / f"plasma/desktoptheme/{THEME_ID}/metadata.json", metadata)
    write(share / "color-schemes/NoxForgeDark.colors")
    write(share / f"aurorae/themes/{THEME_ID}/metadata.desktop", desktop)
    write(share / "icons/NoxForge/index.theme")
    write(share / "icons/NoxForge-Cursors/index.theme")
    write(share / "sounds/NoxForge/index.theme")
    write(share / "wallpapers/NoxForge/metadata.json", metadata)
    write(share / f"kwin/tabbox/{THEME_ID}/metadata.json", metadata)
    write(share / "sddm/themes/NoxForge/metadata.desktop", sddm)
    write(root / "usr/lib64/qt6/plugins/styles/libnoxforge6.so", "plugin\n")


def run_doctor(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(DOCTOR), "--root", str(root), "--json"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


class DoctorTests(unittest.TestCase):
    def test_complete_staged_installation_is_successful_and_read_only(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noxforge-doctor-complete-") as temp:
            root = Path(temp)
            stage_complete(root)
            before = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in root.rglob("*")
                if path.is_file()
            }
            result = run_doctor(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "ok")
            self.assertEqual(report["missing"], [])
            self.assertFalse(report["mixedVersions"])
            after = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in root.rglob("*")
                if path.is_file()
            }
            self.assertEqual(before, after)

    def test_partial_installation_is_actionable(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noxforge-doctor-partial-") as temp:
            root = Path(temp)
            stage_complete(root)
            (root / "usr/share/icons/NoxForge/index.theme").unlink()
            result = run_doctor(root)
            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            self.assertEqual(report["missing"], ["icons"])
            self.assertIn("reinstall", report["nextAction"].lower())

    def test_absent_installation_is_actionable(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noxforge-doctor-absent-") as temp:
            result = run_doctor(Path(temp))
            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "incomplete")
            self.assertGreaterEqual(len(report["missing"]), 10)

    def test_mixed_versions_fail(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noxforge-doctor-mixed-") as temp:
            root = Path(temp)
            stage_complete(root)
            write(
                root / f"usr/share/kwin/tabbox/{THEME_ID}/metadata.json",
                json.dumps({"KPlugin": {"Version": "99.0.0"}}) + "\n",
            )
            result = run_doctor(root)
            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            self.assertTrue(report["mixedVersions"])
            self.assertIn("mixed", report["nextAction"].lower())


if __name__ == "__main__":
    unittest.main()
