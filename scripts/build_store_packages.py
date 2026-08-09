#!/usr/bin/env python3
"""Build deterministic Store component and portable archives.

The source directories are allowlisted here rather than copied wholesale.  A
package is assembled in a temporary tree, normalised to uid/gid 0 and mtime 0,
then emitted as a GNU tar.xz with stable member order.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "distribution/release-manifest.json"

PACKAGE_KEYS = (
    "global-theme",
    "plasma-style",
    "colors",
    "aurorae",
    "icons",
    "cursors",
    "kwin-switcher",
    "sounds",
    "wallpapers",
)


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def release_version(manifest: dict, *, stable: bool = False) -> str:
    return manifest["release"]["stableVersion"] if stable else manifest["release"]["version"]


def _copy_tree(source: Path, destination: Path) -> None:
    if source.is_symlink():
        raise ValueError(f"symlinks are not allowed in package inputs: {source}")
    if source.is_dir():
        _assert_safe_tree(source)
        shutil.copytree(source, destination, symlinks=False, dirs_exist_ok=True)
    elif source.is_file():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    else:
        raise FileNotFoundError(source)


def _assert_safe_tree(root: Path) -> None:
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"symlinks are not allowed: {path}")
        if not (path.is_file() or path.is_dir()):
            raise ValueError(f"special file is not allowed: {path}")
        if path.is_file() and path.stat().st_nlink > 1:
            raise ValueError(f"hardlinks are not allowed: {path}")
        relative = PurePosixPath(path.relative_to(root).as_posix())
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"unsafe package path: {relative}")


def _rewrite_edition_defaults(root: Path, manifest: dict, edition: str) -> None:
    defaults = root / "contents/defaults"
    if defaults.is_file():
        try:
            widget_style = manifest["editions"][edition]["widgetStyle"]
        except (KeyError, TypeError) as error:
            raise ValueError(f"edition {edition!r} has no widgetStyle contract") from error
        if widget_style not in {"Breeze", "NoxForge"}:
            raise ValueError(f"unsupported widgetStyle for {edition}: {widget_style}")
        text = defaults.read_text(encoding="utf-8")
        lines = text.splitlines()
        replaced = False
        for index, line in enumerate(lines):
            if line.startswith("widgetStyle="):
                lines[index] = f"widgetStyle={widget_style}"
                replaced = True
        if not replaced:
            lines.append(f"widgetStyle={widget_style}")
        defaults.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def _wallpaper_variant(source: Path, destination: Path, wallpaper_id: str, display_name: str) -> None:
    _copy_tree(source, destination)
    metadata = destination / "metadata.json"
    data = json.loads(metadata.read_text(encoding="utf-8"))
    plugin = data.setdefault("KPlugin", {})
    plugin["Id"] = wallpaper_id
    plugin["Name"] = display_name
    plugin["Description"] = f"Original angular graphite {display_name} wallpaper"
    metadata.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def assemble_package(package: str, staging: Path, manifest: dict, *, edition: str = "store") -> Path:
    """Populate *staging* and return the expected archive root."""

    if package not in PACKAGE_KEYS:
        raise ValueError(f"unknown Store package: {package}")
    staging.mkdir(parents=True, exist_ok=True)
    root_name = {
        "global-theme": "global-theme",
        "plasma-style": "plasma-style",
        "kwin-switcher": "kwin-switcher",
        "colors": "colors",
        "aurorae": "aurorae",
        "icons": "icons",
        "cursors": "cursors",
        "sounds": "sounds",
        "wallpapers": "wallpapers",
    }[package]
    if package == "global-theme":
        _copy_tree(ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop", staging)
        _rewrite_edition_defaults(staging, manifest, edition)
    elif package == "plasma-style":
        _copy_tree(ROOT / "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop", staging)
    elif package == "kwin-switcher":
        _copy_tree(ROOT / "kwin/tabbox/io.github.loofiboss.noxforge.desktop", staging)
    elif package == "colors":
        _copy_tree(ROOT / "color-schemes/NoxForgeDark.colors", staging / "NoxForgeDark.colors")
    elif package == "aurorae":
        _copy_tree(ROOT / "aurorae/io.github.loofiboss.noxforge.desktop", staging / "io.github.loofiboss.noxforge.desktop")
    elif package == "icons":
        _copy_tree(ROOT / "icons/NoxForge", staging / "NoxForge")
    elif package == "cursors":
        _copy_tree(ROOT / "cursors/NoxForge-Cursors", staging / "NoxForge-Cursors")
    elif package == "sounds":
        _copy_tree(ROOT / "sounds/NoxForge", staging / "NoxForge")
    elif package == "wallpapers":
        variants = (
            ("NoxForge", "NoxForge Forge"),
            ("NoxForge-Quiet", "NoxForge Quiet"),
            ("NoxForge-Ultrawide", "NoxForge Ultrawide"),
        )
        for wallpaper_id, display_name in variants:
            _wallpaper_variant(
                ROOT / "wallpapers" / wallpaper_id,
                staging / wallpaper_id,
                wallpaper_id,
                display_name,
            )
    _assert_safe_tree(staging)
    return staging / root_name


def _tar_info(path: Path, name: str) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name)
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    info.mtime = 0
    if path.is_dir():
        info.type = tarfile.DIRTYPE
        info.mode = 0o755
    else:
        info.mode = 0o755 if path.stat().st_mode & 0o111 else 0o644
        info.size = path.stat().st_size
    return info


def create_archive(source: Path, archive_path: Path, root_name: str | None = None) -> str:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        archive_path.unlink()
    root_name = root_name or source.name
    with tarfile.open(archive_path, "w:xz", format=tarfile.GNU_FORMAT, preset=9) as archive:
        root_info = _tar_info(source, root_name)
        archive.addfile(root_info)
        for path in sorted(source.rglob("*"), key=lambda item: item.relative_to(source).as_posix()):
            relative = path.relative_to(source).as_posix()
            info = _tar_info(path, f"{root_name}/{relative}")
            if path.is_dir():
                archive.addfile(info)
            else:
                with path.open("rb") as handle:
                    archive.addfile(info, handle)
    return hashlib.sha256(archive_path.read_bytes()).hexdigest()


def artifact_filename(manifest: dict, package: str) -> str:
    version = release_version(manifest, stable=True)
    stable = manifest["release"]["stableVersion"]
    return next(item["filename"] for item in manifest["artifacts"] if item["key"] == package).replace(stable, version)


def build_package(package: str, output_dir: Path, manifest: dict) -> tuple[Path, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"noxforge-{package}-") as name:
        staging = Path(name) / package
        root = assemble_package(package, staging, manifest, edition="store")
        archive = output_dir / artifact_filename(manifest, package)
        checksum = create_archive(staging, archive, root_name=root.name if package not in {"aurorae", "icons", "cursors", "sounds", "wallpapers", "colors"} else package)
    checksum_path = archive.with_suffix(archive.suffix + ".sha256")
    checksum_path.write_text(f"{checksum}  {archive.name}\n", encoding="utf-8", newline="\n")
    return archive, checksum


def build_all(output_dir: Path, manifest: dict) -> list[tuple[Path, str]]:
    built = [build_package(package, output_dir, manifest) for package in PACKAGE_KEYS]
    # Portable is assembled from the same source contract and embeds the
    # component archives, so callers can install without a network.
    portable = output_dir / artifact_filename(manifest, "portable")
    with tempfile.TemporaryDirectory(prefix="noxforge-portable-") as name:
        root = Path(name) / "noxforge"
        root.mkdir()
        (root / "VERSION").write_text(release_version(manifest) + "\n", encoding="utf-8")
        (root / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        for relative in ("scripts/install.sh", "scripts/uninstall.sh"):
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, destination)
        doctor = root / "bin/noxforge-doctor"
        doctor.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "tools/noxforge-doctor", doctor)
        component_root = root / "components"
        for package in PACKAGE_KEYS:
            with tempfile.TemporaryDirectory(prefix=f"noxforge-portable-{package}-") as package_name:
                package_staging = Path(package_name) / package
                assemble_package(package, package_staging, manifest, edition="portable")
                target = component_root / package
                target.mkdir(parents=True)
                source = package_staging
                shutil.copytree(source, target, dirs_exist_ok=True)
        _assert_safe_tree(root)
        checksum = create_archive(root, portable, root_name="noxforge")
    portable.with_suffix(portable.suffix + ".sha256").write_text(f"{checksum}  {portable.name}\n", encoding="utf-8", newline="\n")
    built.append((portable, checksum))
    sums = output_dir / "SHA256SUMS"
    sums.write_text("".join(f"{digest}  {path.name}\n" for path, digest in sorted(built, key=lambda item: item[0].name)), encoding="utf-8", newline="\n")
    return built


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--package", choices=["all", *PACKAGE_KEYS], default="all")
    args = parser.parse_args()
    manifest = load_manifest()
    if args.package == "all":
        built = build_all(args.output_dir, manifest)
    else:
        built = [build_package(args.package, args.output_dir, manifest)]
    for path, digest in built:
        print(f"{path} {path.stat().st_size} bytes {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
