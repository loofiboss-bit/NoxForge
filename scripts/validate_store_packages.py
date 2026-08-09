#!/usr/bin/env python3
"""Validate NoxForge Store and portable archives against the release manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import tarfile
from pathlib import Path, PurePosixPath

try:
    from .build_store_packages import PACKAGE_KEYS, artifact_filename, load_manifest, release_version
except ImportError:
    from build_store_packages import PACKAGE_KEYS, artifact_filename, load_manifest, release_version

ROOT = Path(__file__).resolve().parents[1]


def _safe_name(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if path.is_absolute() or not path.parts or ".." in path.parts or "" in path.parts:
        raise ValueError(f"unsafe archive path: {name!r}")
    return path


def _members(archive: Path) -> list[tarfile.TarInfo]:
    with tarfile.open(archive, "r:*", errorlevel=2) as handle:
        members = handle.getmembers()
    for member in members:
        _safe_name(member.name)
        if member.issym() or member.islnk():
            raise ValueError(f"links are not allowed: {member.name}")
        if member.ischr() or member.isblk() or member.isfifo() or member.isdev():
            raise ValueError(f"special files are not allowed: {member.name}")
        if member.pax_headers or member.uname or member.gname or member.uid != 0 or member.gid != 0 or member.mtime != 0:
            raise ValueError(f"non-canonical metadata: {member.name}")
    return members


def _prefixes(package: str) -> tuple[str, ...]:
    if package == "portable":
        return (
            "VERSION",
            "manifest.json",
            "bin/",
            "scripts/",
            "components/",
        )
    if package in {"global-theme", "plasma-style", "kwin-switcher"}:
        if package == "global-theme":
            return ("metadata.json", "manifest.json", "contents/")
        if package == "kwin-switcher":
            return ("metadata.json", "contents/")
        return ("metadata.json", "colors", "plasmarc", "dialogs/", "weather/", "widgets/", "opaque/", "solid/", "translucent/")
    if package == "colors":
        return ("NoxForgeDark.colors",)
    if package == "aurorae":
        return ("io.github.loofiboss.noxforge.desktop/",)
    if package == "icons":
        return ("NoxForge/",)
    if package == "cursors":
        return ("NoxForge-Cursors/",)
    if package == "sounds":
        return ("NoxForge/",)
    if package == "wallpapers":
        return ("NoxForge/", "NoxForge-Quiet/", "NoxForge-Ultrawide/")
    return ()


def _archive_root(package: str) -> str:
    return {
        "global-theme": "global-theme",
        "plasma-style": "plasma-style",
        "colors": "colors",
        "aurorae": "aurorae",
        "icons": "icons",
        "cursors": "cursors",
        "kwin-switcher": "kwin-switcher",
        "sounds": "sounds",
        "wallpapers": "wallpapers",
        "portable": "noxforge",
    }[package]


def _metadata_fields(archive: Path, members: list[tarfile.TarInfo], suffix: str) -> dict[str, str]:
    member = next((item for item in members if item.name.endswith(suffix)), None)
    if member is None:
        raise ValueError(f"archive is missing {suffix}")
    with tarfile.open(archive, "r:*") as handle:
        stream = handle.extractfile(member)
        if stream is None:
            raise ValueError(f"cannot read {suffix}")
        text = stream.read().decode("utf-8")
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            fields[key.strip()] = value.strip()
    return fields


def _validate_metadata(archive: Path, package: str, members: list[tarfile.TarInfo], manifest: dict) -> None:
    version_values = {release_version(manifest), release_version(manifest, stable=True)}
    package_contract = {
        "global-theme": ("globalTheme", "io.github.loofiboss.noxforge.desktop"),
        "plasma-style": ("plasmaStyle", "io.github.loofiboss.noxforge.desktop"),
        "kwin-switcher": ("kwinSwitcher", "io.github.loofiboss.noxforge.desktop"),
    }
    if package in package_contract:
        _, expected_id = package_contract[package]
        metadata_member = next(member for member in members if member.name.endswith("/metadata.json"))
        with tarfile.open(archive, "r:*") as handle:
            stream = handle.extractfile(metadata_member)
            if stream is None:
                raise ValueError(f"{package} metadata cannot be read")
            metadata = json.load(stream)
        plugin = metadata.get("KPlugin", {})
        if plugin.get("License") != "MIT" or plugin.get("Id") != expected_id or plugin.get("Version") not in version_values:
            raise ValueError(f"{package} metadata version/license/ID drift")
    elif package == "aurorae":
        fields = _metadata_fields(archive, members, "/metadata.desktop")
        if (
            fields.get("X-KDE-PluginInfo-License") != "MIT"
            or fields.get("X-KDE-PluginInfo-Name") != manifest["packages"]["aurorae"]["id"]
            or fields.get("X-KDE-PluginInfo-Version") not in version_values
        ):
            raise ValueError("aurorae metadata version/license/ID drift")
    elif package == "wallpapers":
        expected = {
            "NoxForge": manifest["packages"]["wallpapers"]["forge"]["id"],
            "NoxForge-Quiet": manifest["packages"]["wallpapers"]["quiet"]["id"],
            "NoxForge-Ultrawide": manifest["packages"]["wallpapers"]["ultrawide"]["id"],
        }
        with tarfile.open(archive, "r:*") as handle:
            for directory, expected_id in expected.items():
                member = next((item for item in members if item.name == f"wallpapers/{directory}/metadata.json"), None)
                if member is None:
                    raise ValueError(f"wallpapers package is missing {directory} metadata")
                stream = handle.extractfile(member)
                if stream is None:
                    raise ValueError(f"cannot read {directory} metadata")
                plugin = json.load(stream).get("KPlugin", {})
                if plugin.get("License") != "MIT" or plugin.get("Id") != expected_id or plugin.get("Version") not in version_values:
                    raise ValueError(f"wallpaper metadata version/license/ID drift: {directory}")


def validate_archive(archive: Path, package: str, manifest: dict) -> dict:
    artifact = next(item for item in manifest["artifacts"] if item["key"] == package)
    if archive.stat().st_size > artifact["budgetBytes"]:
        raise ValueError(f"{archive.name} exceeds {artifact['budgetBytes']} bytes")
    members = _members(archive)
    prefixes = _prefixes(package)
    if not members:
        raise ValueError("archive is empty")
    root = _archive_root(package)
    top_level = {member.name.split("/", 1)[0] for member in members if member.name}
    if top_level != {root}:
        raise ValueError(f"archive root drift for {package}: {sorted(top_level)}")
    names = [member.name.rstrip("/") for member in members if member.name != "."]
    relative_names = []
    for name in names:
        # The single top-level directory is the archive root, not a payload
        # file.  Validate all descendants relative to that root.
        if "/" not in name:
            continue
        relative = name.split("/", 1)[1]
        relative_names.append(relative)
        if not any(
            (relative == prefix.rstrip("/") or relative.startswith(prefix))
            if prefix.endswith("/")
            else relative == prefix
            for prefix in prefixes
        ):
            raise ValueError(f"foreign file in {package}: {name}")
    if package in {"global-theme", "plasma-style", "kwin-switcher"}:
        if "metadata.json" not in relative_names:
            raise ValueError(f"{package} metadata must be at package root")
    if package in {"aurorae", "wallpapers"}:
        _validate_metadata(archive, package, members, manifest)
    elif package in {"global-theme", "plasma-style", "kwin-switcher"}:
        _validate_metadata(archive, package, members, manifest)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    return {"package": package, "path": archive.name, "bytes": archive.stat().st_size, "sha256": digest, "budgetBytes": artifact["budgetBytes"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("archives", nargs="*", type=Path)
    args = parser.parse_args()
    manifest = load_manifest()
    targets = args.archives
    if not targets:
        targets = [args.archive_dir / artifact_filename(manifest, package) for package in (*PACKAGE_KEYS, "portable")]
    for archive in targets:
        package = next((key for key in (*PACKAGE_KEYS, "portable") if artifact_filename(manifest, key) == archive.name), None)
        if package is None:
            raise SystemExit(f"cannot infer package for {archive}")
        print(json.dumps(validate_archive(archive, package, manifest), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
