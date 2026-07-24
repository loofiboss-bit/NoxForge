#!/usr/bin/env python3
"""Run the authoritative local and CI release-integrity gate."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR_CHECKS = (
    ("sync_version.py", "--check"),
    ("generate_design_system.py", "--check"),
    ("generate_plasma_svgs.py", "--check"),
    ("generate_visual_assets.py", "--check"),
    ("generate_cursors.py", "--check"),
    ("render_wallpaper.py", "--check"),
    ("check_plasma_rasters.py",),
)
QML_SURFACES = (
    "sddm/NoxForge/Main.qml",
    "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/splash/Splash.qml",
    "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/logout/Logout.qml",
    "kwin/tabbox/io.github.loofiboss.noxforge.desktop/contents/ui/main.qml",
)


def run(command: list[str], *, env: dict[str, str] | None = None) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def find_qmllint() -> str:
    direct = shutil.which("qmllint")
    if direct:
        return direct
    qmake = shutil.which("qmake6")
    if qmake:
        result = subprocess.run(
            [qmake, "-query", "QT_INSTALL_BINS"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        candidate = Path(result.stdout.strip()) / "qmllint"
        if candidate.is_file():
            return str(candidate)
    raise RuntimeError("qmllint was not found; install Qt 6 declarative development tools")


def load_build_module():
    spec = importlib.util.spec_from_file_location("noxforge_build", ROOT / "scripts/build.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load scripts/build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_reproducible_archive(temporary: Path) -> Path:
    build_module = load_build_module()
    first_archive, _, first_hash = build_module.build(
        temporary / "archive-a/build",
        temporary / "archive-a/dist",
    )
    second_archive, _, second_hash = build_module.build(
        temporary / "archive-b/build",
        temporary / "archive-b/dist",
    )
    if first_hash != second_hash or first_archive.read_bytes() != second_archive.read_bytes():
        raise RuntimeError("independent source archive builds are not byte-identical")
    if first_hash != hashlib.sha256(first_archive.read_bytes()).hexdigest():
        raise RuntimeError("source archive checksum does not match its contents")
    print(f"Reproducible source archive: {first_hash}")
    return first_archive


def check_rpm(temporary: Path, source_archive: Path) -> None:
    for command in ("rpmbuild", "rpmlint"):
        if not shutil.which(command):
            raise RuntimeError(f"{command} was not found; install Fedora RPM build tools")

    topdir = temporary / "rpmbuild"
    for directory in ("BUILD", "BUILDROOT", "RPMS", "SOURCES", "SPECS", "SRPMS"):
        (topdir / directory).mkdir(parents=True)
    packaged_source = topdir / "SOURCES" / source_archive.name
    shutil.copy2(source_archive, packaged_source)
    run(
        [
            "rpmbuild",
            "-ba",
            "--define",
            f"_topdir {topdir}",
            str(ROOT / "packaging/noxforge.spec"),
        ]
    )
    packages = sorted(topdir.glob("SRPMS/*.src.rpm")) + sorted(topdir.glob("RPMS/*/*.rpm"))
    if not packages:
        raise RuntimeError("rpmbuild produced no packages")
    run(["rpmlint", *[str(package) for package in packages]])
    binary = [
        package
        for package in packages
        if ".src.rpm" not in package.name
        and "-debuginfo-" not in package.name
        and "-debugsource-" not in package.name
    ]
    if len(binary) != 1:
        raise RuntimeError("expected exactly one installable NoxForge RPM")
    listing = subprocess.run(
        ["rpm", "-qlp", str(binary[0])],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    for expected in (
        "/usr/lib64/qt6/plugins/styles/libnoxforge6.so",
        "/usr/share/plasma/look-and-feel/io.github.loofiboss.noxforge.desktop",
        "/usr/share/sddm/themes/NoxForge",
    ):
        if expected not in listing:
            raise RuntimeError(f"RPM is missing expected path: {expected}")
    print(f"Fedora RPM contract passed: {binary[0].name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-archive",
        action="store_true",
        help="skip the independent archive comparison for focused local debugging",
    )
    parser.add_argument(
        "--skip-rpm",
        action="store_true",
        help="skip RPM build and rpmlint for focused local debugging",
    )
    arguments = parser.parse_args()

    run([sys.executable, "scripts/validate.py"])
    for command in GENERATOR_CHECKS:
        run([sys.executable, f"scripts/{command[0]}", *command[1:]])
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])

    with tempfile.TemporaryDirectory(prefix="noxforge-release-check-") as temp:
        temporary = Path(temp)
        build_dir = temporary / "cmake"
        run(
            [
                "cmake",
                "-S",
                str(ROOT),
                "-B",
                str(build_dir),
                "-G",
                "Ninja",
                "-DCMAKE_BUILD_TYPE=Release",
            ]
        )
        run(["cmake", "--build", str(build_dir)])
        run(["ctest", "--test-dir", str(build_dir), "--output-on-failure"])

        qmllint = find_qmllint()
        for surface in QML_SURFACES:
            run([qmllint, surface])

        isolated_home = temporary / "home"
        isolated_data = isolated_home / ".local/share"
        install_env = os.environ.copy()
        install_env.update(
            HOME=str(isolated_home),
            XDG_DATA_HOME=str(isolated_data),
            XDG_CONFIG_HOME=str(isolated_home / ".config"),
            NOXFORGE_SYSTEM_ROOT=str(temporary / "system-root"),
        )
        run(["scripts/install.sh", "--user", "--dry-run"], env=install_env)
        run(["scripts/uninstall.sh", "--user", "--dry-run"], env=install_env)
        run(["scripts/install-system.sh", "--system", "--dry-run"], env=install_env)
        run(["scripts/uninstall-system.sh", "--system", "--dry-run"], env=install_env)

        source_archive = None
        if not arguments.skip_archive:
            source_archive = check_reproducible_archive(temporary)
        if not arguments.skip_rpm:
            if source_archive is None:
                build_module = load_build_module()
                source_archive, _, _ = build_module.build(
                    temporary / "archive-for-rpm/build",
                    temporary / "archive-for-rpm/dist",
                )
            check_rpm(temporary, source_archive)

    if shutil.which("git") and (ROOT / ".git").exists():
        run(["git", "-c", f"safe.directory={ROOT}", "diff", "--check"])

    print("NoxForge release check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
