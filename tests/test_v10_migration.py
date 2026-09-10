"""Behavioral checks for migration evidence validation."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_v10_migration import metadata_version, validate_build


class MigrationEvidenceTests(unittest.TestCase):
    def test_system_uninstall_handles_manifest_without_final_newline(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            build, stage = root / "build", root / "stage"
            build.mkdir()
            target = stage / "usr/share/man/man1/noxforge-doctor.1"
            target.parent.mkdir(parents=True)
            target.write_text("manual")
            (build / "install_manifest.txt").write_text("/usr/share/man/man1/noxforge-doctor.1")
            script = Path(__file__).resolve().parents[1] / "scripts/uninstall-system.sh"
            env = dict(os.environ, NOXFORGE_BUILD_ROOT=str(build), NOXFORGE_SYSTEM_ROOT=str(stage))
            subprocess.run(["bash", str(script), "--system"], env=env, check=True, capture_output=True)
            self.assertFalse(target.exists())

    def test_metadata_must_match_installed_version(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "noxforge").mkdir()
            (root / "noxforge/VERSION").write_text("10.0.0\n")
            metadata = root / "plasma/look-and-feel/io.github.loofiboss.noxforge.desktop/metadata.json"
            metadata.parent.mkdir(parents=True)
            metadata.write_text(json.dumps({"KPlugin": {"Version": "9.0.0"}}))
            with self.assertRaises(AssertionError):
                metadata_version(root, "10.0.0")
            metadata.write_text(json.dumps({"KPlugin": {"Version": "10.0.0"}}))
            metadata_version(root, "10.0.0")

    def test_rejects_build_from_different_source(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "cmake_install.cmake").touch()
            (root / "CMakeCache.txt").write_text("CMAKE_HOME_DIRECTORY:INTERNAL=/other/source\nCMAKE_INSTALL_PREFIX:PATH=/usr\n")
            with self.assertRaises(ValueError):
                validate_build(root, root / "expected")


if __name__ == "__main__":
    unittest.main()
