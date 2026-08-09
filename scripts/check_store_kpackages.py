#!/usr/bin/env python3
"""Exercise Store package installation in isolated KDE resource roots.

KPackage-owned components are installed with ``kpackagetool6``.  The other
KNewStuff package types are emulated at their documented XDG target roots so
the check remains useful on a headless build host without mutating a user
profile.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

try:
    from .build_store_packages import PACKAGE_KEYS, artifact_filename, load_manifest
    from .validate_store_packages import validate_archive
except ImportError:
    from build_store_packages import PACKAGE_KEYS, artifact_filename, load_manifest
    from validate_store_packages import validate_archive

ROOT = Path(__file__).resolve().parents[1]
STORE_MANIFEST = ROOT / "distribution/kde-store/package-manifest.json"
KPACKAGE_TYPES = {
    "global-theme": "Plasma/LookAndFeel",
    "plasma-style": "Plasma/Theme",
    "kwin-switcher": "KWin/WindowSwitcher",
}


def _run(command: list[str], env: dict[str, str], *, capture: bool = True) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=capture,
        text=True,
    )
    return (result.stdout or "") + (result.stderr or "")


def _snapshot(root: Path) -> str:
    digest = hashlib.sha256()
    if not root.exists():
        return digest.hexdigest()
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        if path.is_file():
            digest.update(path.read_bytes())
        elif path.is_dir():
            digest.update(b"<dir>")
    return digest.hexdigest()


def _archive_payload(archive: Path, destination: Path) -> list[Path]:
    extracted: list[Path] = []
    with tarfile.open(archive, "r:*") as handle:
        members = handle.getmembers()
        roots = {member.name.split("/", 1)[0] for member in members if member.name}
        if len(roots) != 1:
            raise RuntimeError(f"archive has multiple roots: {archive}")
        root = next(iter(roots))
        for member in members:
            if member.name == root or not member.name.startswith(root + "/"):
                continue
            relative = Path(member.name[len(root) + 1 :])
            target = destination / relative
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if not member.isfile():
                raise RuntimeError(f"unexpected archive member: {member.name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            stream = handle.extractfile(member)
            if stream is None:
                raise RuntimeError(f"cannot extract archive member: {member.name}")
            target.write_bytes(stream.read())
            target.chmod(0o755 if member.mode & 0o111 else 0o644)
            extracted.append(target)
    return extracted


def _kpackage_install(package: str, archive: Path, manifest: dict, env: dict[str, str], data_home: Path) -> None:
    package_record = next(item for item in manifest["components"] if item["key"] == package)
    package_id = package_record["id"]
    package_type = KPACKAGE_TYPES[package]
    command = ["kpackagetool6", "--type", package_type, "--install", str(archive)]
    _run(command, env)
    _run(["kpackagetool6", "--type", package_type, "--list"], env)
    # A second install follows the real update path and must remain harmless.
    _run(["kpackagetool6", "--type", package_type, "--upgrade", str(archive)], env)
    _run(["kpackagetool6", "--type", package_type, "--list"], env)
    target = data_home / package_record["targetRoot"]
    if not (target / package_id).exists():
        raise RuntimeError(f"kpackagetool6 did not install {package} at {target / package_id}")
    _run(["kpackagetool6", "--type", package_type, "--remove", package_id], env)
    if (target / package_id).exists():
        raise RuntimeError(f"kpackagetool6 did not remove {package_id}")


def _knewstuff_install(package: str, archive: Path, manifest: dict, data_home: Path) -> None:
    package_record = next(item for item in manifest["components"] if item["key"] == package)
    target_root = data_home / package_record["targetRoot"]
    package_id = package_record["id"]
    package_stage = data_home / ".noxforge-store-stage" / package
    if package_stage.exists():
        shutil.rmtree(package_stage)
    package_stage.mkdir(parents=True)
    _archive_payload(archive, package_stage)
    target_root.mkdir(parents=True, exist_ok=True)
    payload_root = package_stage / next(path.name for path in package_stage.iterdir())
    # Archives have a package-specific top directory.  Copy its contents into
    # the KNewStuff target root while preserving the package ID directory.
    if package == "colors":
        payload_root = package_stage / "NoxForgeDark.colors"
        destination = target_root / payload_root.name
        shutil.copy2(payload_root, destination)
        owned = [destination]
    else:
        owned_root = target_root / package_id
        if package == "aurorae":
            owned_root = target_root / "io.github.loofiboss.noxforge.desktop"
        if package == "wallpapers":
            owned = []
            for variant in ("NoxForge", "NoxForge-Quiet", "NoxForge-Ultrawide"):
                source = package_stage / variant
                destination = target_root / variant
                shutil.copytree(source, destination, dirs_exist_ok=True)
                owned.append(destination)
        else:
            shutil.copytree(payload_root, owned_root, dirs_exist_ok=True)
            owned = [owned_root]
    # Repeating an install must update only the package payload.
    if package == "colors":
        shutil.copy2(payload_root, target_root / payload_root.name)
    elif package == "wallpapers":
        for variant in ("NoxForge", "NoxForge-Quiet", "NoxForge-Ultrawide"):
            shutil.copytree(package_stage / variant, target_root / variant, dirs_exist_ok=True)
    else:
        shutil.copytree(payload_root, owned[0], dirs_exist_ok=True)
    if package == "colors":
        target_root.joinpath("NoxForgeDark.colors").unlink(missing_ok=True)
    else:
        for path in owned:
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
    shutil.rmtree(package_stage)


def check(archive_dir: Path) -> None:
    if shutil.which("kpackagetool6") is None:
        print("kpackagetool6 unavailable; Store KPackage gate is unverified", file=sys.stderr)
        return
    manifest = json.loads(STORE_MANIFEST.read_text(encoding="utf-8"))
    release_manifest = load_manifest()
    with tempfile.TemporaryDirectory(prefix="noxforge-kpackage-gate-") as temporary:
        root = Path(temporary)
        home = root / "home"
        data_home = home / ".local/share"
        config_home = home / ".config"
        home.mkdir()
        data_home.mkdir(parents=True)
        config_home.mkdir()
        sentinel = data_home / "noxforge-store-sentinel"
        sentinel.write_text("preserve\n", encoding="utf-8")
        config_sentinel = config_home / "noxforge-preserved.conf"
        config_sentinel.write_text("Theme=UserChoice\n", encoding="utf-8")
        before = (_snapshot(data_home), _snapshot(config_home))
        env = os.environ.copy()
        env.update(
            HOME=str(home),
            KDEHOME=str(home / ".kde"),
            XDG_DATA_HOME=str(data_home),
            XDG_CONFIG_HOME=str(config_home),
        )
        for package in PACKAGE_KEYS:
            archive = archive_dir / artifact_filename(release_manifest, package)
            validate_archive(archive, package, release_manifest)
            if package in KPACKAGE_TYPES:
                _kpackage_install(package, archive, manifest, env, data_home)
            else:
                _knewstuff_install(package, archive, manifest, data_home)
            if not sentinel.is_file() or not config_sentinel.is_file():
                raise RuntimeError("Store installation removed an unrelated sentinel")
        after = (_snapshot(data_home), _snapshot(config_home))
        if before[1] != after[1]:
            raise RuntimeError("Store installation changed unrelated KDE configuration")
    print("Isolated Store KPackage/KNewStuff install-list-remove gate passed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive-dir", type=Path, default=ROOT / "dist")
    arguments = parser.parse_args()
    check(arguments.archive_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
