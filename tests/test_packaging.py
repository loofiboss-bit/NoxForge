from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME_ID = "io.github.loofiboss.noxforge.desktop"


class PackagingTests(unittest.TestCase):
    def test_cmake_stages_every_runtime_component_without_settings(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noxforge-cmake-stage-") as temp:
            root = Path(temp)
            build = root / "build"
            stage = root / "stage"
            subprocess.run(
                [
                    "cmake",
                    "-S",
                    str(ROOT),
                    "-B",
                    str(build),
                    "-G",
                    "Ninja",
                    "-DCMAKE_BUILD_TYPE=Release",
                    "-DCMAKE_INSTALL_PREFIX=/usr",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["cmake", "--build", str(build)],
                check=True,
                capture_output=True,
                text=True,
            )
            env = os.environ.copy()
            env["DESTDIR"] = str(stage)
            subprocess.run(
                ["cmake", "--install", str(build)],
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

            expected = (
                "usr/share/color-schemes/NoxForgeDark.colors",
                f"usr/share/plasma/desktoptheme/{THEME_ID}/metadata.json",
                f"usr/share/aurorae/themes/{THEME_ID}/metadata.desktop",
                "usr/share/icons/NoxForge/index.theme",
                "usr/share/icons/NoxForge-Cursors/index.theme",
                "usr/share/sounds/NoxForge/index.theme",
                f"usr/share/plasma/look-and-feel/{THEME_ID}/metadata.json",
                f"usr/share/kwin/tabbox/{THEME_ID}/metadata.json",
                "usr/share/wallpapers/NoxForge/metadata.json",
                "usr/share/sddm/themes/NoxForge/metadata.desktop",
                "usr/share/man/man1/noxforge-doctor.1",
            )
            for relative in expected:
                self.assertTrue((stage / relative).is_file(), relative)
            self.assertFalse((stage / "etc").exists())
            self.assertEqual(list(stage.rglob("plasmashellrc")), [])
            self.assertFalse(any(path.is_symlink() for path in stage.rglob("*")))
            plugins = list(stage.glob("usr/lib*/qt6/plugins/styles/libnoxforge6.so"))
            self.assertEqual(len(plugins), 1)

    def test_rpm_contract_has_no_scriptlets_or_desktop_mutations(self) -> None:
        spec = (ROOT / "packaging/noxforge.spec").read_text(encoding="utf-8")
        self.assertIn("%global use_source_date_epoch_as_buildtime 1", spec)
        self.assertIn("%global _buildhost fedora", spec)
        self.assertIn("%undefine _unique_build_ids", spec)
        self.assertIn("%global _no_recompute_build_ids 1", spec)
        sections = {
            line.strip().split(maxsplit=1)[0]
            for line in spec.splitlines()
            if line.strip().startswith("%")
        }
        self.assertTrue({"%prep", "%build", "%install", "%check", "%files"} <= sections)
        self.assertTrue({"%post", "%pre", "%trigger"}.isdisjoint(sections))
        for command in (
            "plasma-apply-",
            "kwriteconfig",
            "qdbus",
            "systemctl",
            "plasmashell",
        ):
            self.assertNotIn(command, spec)
        self.assertIn("%{_qt6_plugindir}/styles/libnoxforge6.so", spec)
        self.assertIn("%{_datadir}/sddm/themes/NoxForge/", spec)
        self.assertIn("BuildRequires:  kf6-kirigami", spec)
        self.assertIn("Requires:       breeze-icon-theme", spec)

    def test_source_archive_contains_packaging_contract(self) -> None:
        build_script = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        self.assertIn('Path("packaging")', build_script)

    def test_binary_and_source_rpms_are_built_separately(self) -> None:
        for relative in (
            "scripts/release-check.py",
            "scripts/prepare_v7_candidate.py",
            ".github/workflows/release.yml",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("-bb", source, relative)
            self.assertIn("-bs", source, relative)
            self.assertNotIn("-ba", source, relative)

    def test_native_binaries_do_not_embed_absolute_build_roots(self) -> None:
        cmake = (ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
        self.assertIn("-ffile-prefix-map=${CMAKE_SOURCE_DIR}", cmake)
        self.assertIn("-ffile-prefix-map=${CMAKE_BINARY_DIR}", cmake)
        self.assertIn("-frandom-seed=NoxForge-${NOXFORGE_PUBLIC_VERSION}", cmake)
        self.assertIn("string(SHA1 NOXFORGE_STYLE_BUILD_ID", cmake)
        self.assertIn("-Wl,--build-id=0x${NOXFORGE_STYLE_BUILD_ID}", cmake)


if __name__ == "__main__":
    unittest.main()
