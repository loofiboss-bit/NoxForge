#!/usr/bin/env python3
"""Create deterministic local NoxForge source artifacts."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
RELEASE_NAME = f"NoxForge-{VERSION}"
SOURCE_PATHS = (
    Path("LICENSE"),
    Path("LICENSES.md"),
    Path("README.md"),
    Path("VERSION"),
    Path("AGENTS.md"),
    Path("CMakeLists.txt"),
    Path("DESIGN.md"),
    Path("packaging"),
    Path("docs"),
    Path("design"),
    Path("color-schemes"),
    Path("plasma"),
    Path("aurorae"),
    Path("icons"),
    Path("cursors"),
    Path("sounds"),
    Path("look-and-feel"),
    Path("kwin"),
    Path("sddm"),
    Path("src"),
    Path("tools"),
    Path("wallpapers"),
    Path("scripts"),
    Path("tests"),
)
COPY_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", "*~")


def copy_release_tree(staging: Path) -> None:
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    for relative in SOURCE_PATHS:
        source = ROOT / relative
        target = staging / relative
        if source.is_dir():
            shutil.copytree(source, target, ignore=COPY_IGNORE)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def add_directory(archive: tarfile.TarFile, name: str, mode: int = 0o755) -> None:
    info = tarfile.TarInfo(name.rstrip("/") + "/")
    info.type = tarfile.DIRTYPE
    info.mode = mode
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    info.mtime = 0
    archive.addfile(info)


def add_file(archive: tarfile.TarFile, path: Path, name: str) -> None:
    info = tarfile.TarInfo(name)
    info.size = path.stat().st_size
    info.mode = 0o755 if path.stat().st_mode & 0o111 else 0o644
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    info.mtime = 0
    with path.open("rb") as handle:
        archive.addfile(info, handle)


def create_archive(staging: Path, archive_path: Path) -> str:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        archive_path.unlink()
    with tarfile.open(archive_path, "w:xz", format=tarfile.GNU_FORMAT) as archive:
        add_directory(archive, RELEASE_NAME)
        for path in sorted(staging.rglob("*"), key=lambda item: item.as_posix()):
            relative = path.relative_to(staging).as_posix()
            name = f"{RELEASE_NAME}/{relative}"
            if path.is_dir():
                add_directory(archive, name)
            elif path.is_file():
                add_file(archive, path, name)
            else:
                raise RuntimeError(f"unsupported build input: {path}")
    return hashlib.sha256(archive_path.read_bytes()).hexdigest()


def build(build_root: Path, dist_root: Path) -> tuple[Path, Path, str]:
    staging = build_root / RELEASE_NAME
    archive = dist_root / f"noxforge-{VERSION}.tar.xz"
    checksum_path = dist_root / f"noxforge-{VERSION}.tar.xz.sha256"
    copy_release_tree(staging)
    checksum = create_archive(staging, archive)
    checksum_path.write_text(f"{checksum}  {archive.name}\n", encoding="utf-8", newline="\n")
    return archive, checksum_path, checksum


def main() -> int:
    subprocess.run(["python3", str(ROOT / "scripts/validate.py")], cwd=ROOT, check=True)
    subprocess.run(
        [
            "cmake",
            "-S",
            str(ROOT),
            "-B",
            str(ROOT / "build/cmake"),
            "-G",
            "Ninja",
            "-DCMAKE_BUILD_TYPE=Release",
            "-DCMAKE_INSTALL_PREFIX=/usr",
        ],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(["cmake", "--build", str(ROOT / "build/cmake")], cwd=ROOT, check=True)
    subprocess.run(["ctest", "--test-dir", str(ROOT / "build/cmake"), "--output-on-failure"], cwd=ROOT, check=True)
    archive, checksum_path, checksum = build(ROOT / "build", ROOT / "dist")
    print(f"Built {archive.relative_to(ROOT)}")
    print(f"Wrote {checksum_path.relative_to(ROOT)}")
    print(f"SHA256 {checksum}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
