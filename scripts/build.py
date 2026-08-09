#!/usr/bin/env python3
"""Build manifest-driven NoxForge source, portable, and complete artifacts."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import shutil
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "distribution/release-manifest.json"
MANIFEST = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
VERSION = MANIFEST["release"]["version"]
ARTIFACT_VERSION = MANIFEST["release"]["stableVersion"]
RELEASE_NAME = f"NoxForge-{ARTIFACT_VERSION}"
SOURCE_PATHS = tuple(Path(item) for item in MANIFEST["source"]["include"])
SOURCE_EXCLUDES = tuple(MANIFEST["source"]["exclude"])
# The manifest's packaging entry is intentionally equivalent to Path("packaging")
# for callers that inspect the source contract without executing the builder.
COPY_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", "*~")


def excluded(relative: Path) -> bool:
    value = relative.as_posix()
    for pattern in SOURCE_EXCLUDES:
        if fnmatch.fnmatch(value, pattern) or value == pattern or value.startswith(pattern.rstrip("/") + "/"):
            return True
    return False


def copy_release_tree(staging: Path, mode: str = "source") -> None:
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    if mode not in {"source", "all"}:
        raise ValueError(f"source tree is not available in mode {mode}")
    for relative in SOURCE_PATHS:
        source = ROOT / relative
        if not source.exists() or excluded(relative):
            continue
        target = staging / relative
        if source.is_dir():
            for path in source.rglob("*"):
                if path.is_symlink():
                    raise RuntimeError(f"source archive cannot contain symlinks: {path.relative_to(ROOT)}")
                if path.is_file() and path.stat().st_nlink > 1:
                    raise RuntimeError(f"source archive cannot contain hardlinks: {path.relative_to(ROOT)}")
            shutil.copytree(
                source,
                target,
                ignore=lambda path, names: [
                    name
                    for name in names
                    if excluded(Path(path).relative_to(ROOT) / name)
                    or name == "__pycache__"
                    or name.endswith((".pyc", ".pyo", "~"))
                ],
            )
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


def create_archive(staging: Path, archive_path: Path, release_name: str = RELEASE_NAME) -> str:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        archive_path.unlink()
    with tarfile.open(archive_path, "w:xz", format=tarfile.GNU_FORMAT, preset=9) as archive:
        add_directory(archive, release_name)
        for path in sorted(staging.rglob("*"), key=lambda item: item.relative_to(staging).as_posix()):
            relative = path.relative_to(staging).as_posix()
            name = f"{release_name}/{relative}"
            if path.is_dir():
                add_directory(archive, name)
            elif path.is_file():
                add_file(archive, path, name)
            else:
                raise RuntimeError(f"unsupported build input: {path}")
    return hashlib.sha256(archive_path.read_bytes()).hexdigest()


def source_artifact_path(dist_root: Path) -> Path:
    filename = next(item["filename"] for item in MANIFEST["artifacts"] if item["key"] == "source")
    return dist_root / filename


def build_source(build_root: Path, dist_root: Path) -> tuple[Path, Path, str]:
    staging = build_root / "source" / RELEASE_NAME
    archive = source_artifact_path(dist_root)
    copy_release_tree(staging)
    checksum = create_archive(staging, archive)
    checksum_path = archive.with_suffix(archive.suffix + ".sha256")
    checksum_path.write_text(f"{checksum}  {archive.name}\n", encoding="utf-8", newline="\n")
    return archive, checksum_path, checksum


def build_portable(dist_root: Path) -> tuple[Path, str]:
    from build_store_packages import build_all, load_manifest

    outputs = build_all(dist_root, load_manifest())
    path, checksum = next(item for item in outputs if "-portable." in item[0].name)
    return path, checksum


def build(build_root: Path, dist_root: Path, mode: str = "source"):
    if mode == "source":
        return build_source(build_root, dist_root)
    if mode == "portable":
        return build_portable(dist_root)
    if mode == "all":
        source = build_source(build_root, dist_root)
        build_portable(dist_root)
        return source
    raise ValueError(f"unknown build mode: {mode}")


def run_validation() -> None:
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("source", "portable", "all"), default="source")
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()
    if not args.skip_tests:
        run_validation()
    result = build(ROOT / "build", ROOT / "dist", args.mode)
    if args.mode in {"source", "all"}:
        archive, checksum_path, checksum = result
        print(f"Built {archive.relative_to(ROOT)}")
        print(f"Wrote {checksum_path.relative_to(ROOT)}")
        print(f"SHA256 {checksum}")
        if args.mode == "all":
            portable = next(path for path in (ROOT / "dist").glob("*.tar.xz") if "-portable." in path.name)
            print(f"Built {portable.relative_to(ROOT)}")
    else:
        print(f"Built {result[0].relative_to(ROOT)}")
        print(f"SHA256 {result[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
