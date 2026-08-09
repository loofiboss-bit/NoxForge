from __future__ import annotations

import json
import hashlib
import importlib.util
import importlib.machinery
import shutil
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class V8ContractTests(unittest.TestCase):
    def test_manifest_and_wallpaper_ids_are_current(self) -> None:
        manifest = json.loads((ROOT / "distribution/release-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["release"]["version"], (ROOT / "VERSION").read_text().strip())
        self.assertEqual(manifest["packages"]["wallpapers"]["forge"]["id"], "NoxForge")
        forge_metadata = json.loads((ROOT / "wallpapers/NoxForge/metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(forge_metadata["KPlugin"]["Name"], "NoxForge Forge")
        self.assertEqual(
            {entry["id"] for entry in manifest["packages"]["wallpapers"].values()},
            {"NoxForge", "NoxForge-Quiet", "NoxForge-Ultrawide"},
        )

    def test_store_build_is_reproducible_and_validated(self) -> None:
        from scripts import build_store_packages as builder
        from scripts import validate_store_packages as validator

        manifest = builder.load_manifest()
        with tempfile.TemporaryDirectory(prefix="noxforge-v8-store-") as name:
            output = Path(name)
            first, digest_a = builder.build_package("global-theme", output, manifest)
            first_bytes = first.read_bytes()
            second, digest_b = builder.build_package("global-theme", output, manifest)
            self.assertEqual(digest_a, digest_b)
            self.assertEqual(first_bytes, second.read_bytes())
            result = validator.validate_archive(second, "global-theme", manifest)
            self.assertLess(result["bytes"], result["budgetBytes"])

    def test_store_and_portable_defaults_use_breeze(self) -> None:
        from scripts import build_store_packages as builder

        manifest = builder.load_manifest()
        with tempfile.TemporaryDirectory(prefix="noxforge-v8-defaults-") as name:
            output = Path(name)
            builder.build_package("global-theme", output, manifest)
            builder.build_all(output, manifest)
            archive = output / "noxforge-8.0.0-global-theme.tar.xz"
            portable = output / "noxforge-8.0.0-portable.tar.xz"
            with tarfile.open(archive, "r:*") as handle:
                store_defaults = handle.extractfile("global-theme/contents/defaults").read().decode()
            with tarfile.open(portable, "r:*") as handle:
                portable_defaults = handle.extractfile("noxforge/components/global-theme/contents/defaults").read().decode()
            self.assertIn("widgetStyle=Breeze", store_defaults)
            self.assertIn("widgetStyle=Breeze", portable_defaults)
        self.assertIn("widgetStyle=NoxForge", (ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/defaults").read_text())

    def test_wallpaper_store_variants_carry_distinct_payloads(self) -> None:
        from scripts import build_store_packages as builder

        manifest = builder.load_manifest()
        with tempfile.TemporaryDirectory(prefix="noxforge-v8-wallpapers-") as name:
            archive, _ = builder.build_package("wallpapers", Path(name), manifest)
            with tarfile.open(archive, "r:*") as handle:
                digests = {
                    wallpaper_id: hashlib.sha256(
                        handle.extractfile(
                            f"wallpapers/{wallpaper_id}/contents/images/2560x1440.png"
                        ).read()
                    ).hexdigest()
                    for wallpaper_id in ("NoxForge", "NoxForge-Quiet", "NoxForge-Ultrawide")
                }
        self.assertEqual(len(set(digests.values())), 3)

    def test_validator_rejects_absolute_member(self) -> None:
        from scripts import validate_store_packages as validator

        with tempfile.TemporaryDirectory(prefix="noxforge-v8-malicious-") as name:
            archive = Path(name) / "bad.tar.xz"
            with tarfile.open(archive, "w:xz") as handle:
                info = tarfile.TarInfo("/etc/passwd")
                info.size = 0
                handle.addfile(info)
            with self.assertRaises(ValueError):
                validator._members(archive)

    def test_validator_rejects_foreign_portable_member(self) -> None:
        from scripts import build_store_packages as builder
        from scripts import validate_store_packages as validator

        manifest = builder.load_manifest()
        with tempfile.TemporaryDirectory(prefix="noxforge-v8-foreign-") as name:
            archive = Path(name) / "foreign.tar.xz"
            with tarfile.open(archive, "w:xz") as handle:
                root = tarfile.TarInfo("noxforge")
                root.type = tarfile.DIRTYPE
                root.uid = root.gid = root.mtime = 0
                root.mode = 0o755
                handle.addfile(root)
                member = tarfile.TarInfo("noxforge/foreign.txt")
                member.uid = member.gid = member.mtime = 0
                member.mode = 0o644
                member.size = 0
                handle.addfile(member)
            with self.assertRaises(ValueError):
                validator.validate_archive(archive, "portable", manifest)

    def test_portable_doctor_does_not_require_qt_or_sddm(self) -> None:
        loader = importlib.machinery.SourceFileLoader("noxforge_doctor_v8", str(ROOT / "tools/noxforge-doctor"))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        self.assertIsNotNone(spec)
        assert spec and spec.loader
        doctor = importlib.util.module_from_spec(spec)
        loader.exec_module(doctor)

        with tempfile.TemporaryDirectory(prefix="noxforge-v8-doctor-") as name:
            root = Path(name)
            for source, target in (
                (ROOT / "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop", root / "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop"),
                (ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop", root / "plasma/look-and-feel/io.github.loofiboss.noxforge.desktop"),
                (ROOT / "aurorae/io.github.loofiboss.noxforge.desktop", root / "aurorae/themes/io.github.loofiboss.noxforge.desktop"),
                (ROOT / "icons/NoxForge", root / "icons/NoxForge"),
                (ROOT / "cursors/NoxForge-Cursors", root / "icons/NoxForge-Cursors"),
                (ROOT / "sounds/NoxForge", root / "sounds/NoxForge"),
                (ROOT / "wallpapers/NoxForge", root / "wallpapers/NoxForge"),
                (ROOT / "kwin/tabbox/io.github.loofiboss.noxforge.desktop", root / "kwin/tabbox/io.github.loofiboss.noxforge.desktop"),
            ):
                if source.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(source, target, dirs_exist_ok=True)
            (root / "color-schemes").mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / "color-schemes/NoxForgeDark.colors", root / "color-schemes/NoxForgeDark.colors")
            (root / "noxforge").mkdir(parents=True)
            shutil.copy2(ROOT / "VERSION", root / "noxforge/VERSION")
            shutil.copy2(ROOT / "distribution/release-manifest.json", root / "noxforge/manifest.json")
            report = doctor.build_report(root)
            self.assertEqual(report["edition"]["kind"], "portable")
            self.assertEqual(report["edition"]["status"], "ok")

    def test_user_docs_do_not_present_v6_or_v7_as_current(self) -> None:
        files = ("README.md", "docs/QUICKSTART.md", "docs/INSTALL_FEDORA.md", "docs/INSTALL_PORTABLE.md", "docs/INSTALL_ARCH.md", "docs/COMPATIBILITY.md", "docs/TROUBLESHOOTING.md", "docs/CONTRIBUTING.md", "docs/DOCTOR_MANUAL.md", "docs/MANUAL_TESTING.md")
        for relative in files:
            text = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("v6 is the current", text)
            self.assertNotIn("v7 is the current", text)
            self.assertNotIn("noxforge v6 uses", text)
            self.assertNotIn("noxforge v7 uses", text)


if __name__ == "__main__":
    unittest.main()
