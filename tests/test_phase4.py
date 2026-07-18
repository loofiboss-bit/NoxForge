from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("noxforge_build", ROOT / "scripts/build.py")
assert SPEC and SPEC.loader
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class PhaseFourTests(unittest.TestCase):
    def test_build_archive_is_deterministic_and_safe(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noxforge-build-test-") as temp:
            root = Path(temp)
            archive, _, first = BUILD.build(root / "build", root / "dist")
            first_bytes = archive.read_bytes()
            archive, _, second = BUILD.build(root / "build", root / "dist")
            self.assertEqual(first, second)
            self.assertEqual(first_bytes, archive.read_bytes())
            self.assertEqual(first, hashlib.sha256(archive.read_bytes()).hexdigest())
            with tarfile.open(archive, "r:xz") as package:
                members = package.getmembers()
                self.assertTrue(all(not member.issym() and not member.islnk() for member in members))
                self.assertTrue(all(member.uid == 0 and member.gid == 0 and member.mtime == 0 for member in members))
                names = {member.name for member in members}
                self.assertFalse(any("__pycache__" in name or name.endswith(".pyc") for name in names))
                self.assertIn("NoxForge-0.1.0/scripts/install.sh", names)
                self.assertIn("NoxForge-0.1.0/wallpapers/NoxForge/contents/images/2560x1440.png", names)

    def test_repeated_install_and_uninstall_are_reversible(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noxforge-install-test-") as temp:
            home = Path(temp)
            data = home / ".local/share"
            unrelated = data / "unrelated/sentinel.txt"
            unrelated.parent.mkdir(parents=True)
            unrelated.write_text("keep\n", encoding="utf-8")
            env = os.environ.copy()
            env.update(HOME=str(home), XDG_DATA_HOME=str(data), XDG_CONFIG_HOME=str(home / ".config"))
            install = [str(ROOT / "scripts/install.sh"), "--user"]
            uninstall = [str(ROOT / "scripts/uninstall.sh"), "--user"]
            subprocess.run(install, cwd=ROOT, env=env, check=True, capture_output=True, text=True)
            subprocess.run(install, cwd=ROOT, env=env, check=True, capture_output=True, text=True)
            self.assertTrue((data / "color-schemes/NoxForgeDark.colors").is_file())
            self.assertTrue((data / "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop/metadata.json").is_file())
            self.assertTrue((data / "aurorae/themes/io.github.loofiboss.noxforge.desktop/decoration.svgz").is_file())
            self.assertTrue((data / "icons/NoxForge/index.theme").is_file())
            self.assertTrue((data / "wallpapers/NoxForge/metadata.json").is_file())
            subprocess.run(uninstall, cwd=ROOT, env=env, check=True, capture_output=True, text=True)
            subprocess.run(uninstall, cwd=ROOT, env=env, check=True, capture_output=True, text=True)
            self.assertTrue(unrelated.is_file())
            self.assertFalse((data / "icons/NoxForge").exists())
            self.assertFalse((data / "wallpapers/NoxForge").exists())

    def test_dry_runs_do_not_create_component_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noxforge-dry-run-test-") as temp:
            home = Path(temp)
            data = home / ".local/share"
            env = os.environ.copy()
            env.update(HOME=str(home), XDG_DATA_HOME=str(data), XDG_CONFIG_HOME=str(home / ".config"))
            for script in ("install.sh", "uninstall.sh"):
                result = subprocess.run(
                    [str(ROOT / "scripts" / script), "--user", "--dry-run"],
                    cwd=ROOT,
                    env=env,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertIn("Dry run complete", result.stdout)
            self.assertFalse(data.exists())

    def test_live_graphical_checks_are_pending(self) -> None:
        checklist = (ROOT / "docs/MANUAL_TESTING.md").read_text(encoding="utf-8")
        self.assertGreaterEqual(checklist.count("Pending"), 9)
        self.assertNotIn("Passed", checklist)


if __name__ == "__main__":
    unittest.main()
