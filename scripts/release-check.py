#!/usr/bin/env python3
"""Run the authoritative local and CI release-integrity gate."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR_CHECKS = (
    ("validate_release_manifest.py",),
    ("sync_version.py", "--check"),
    ("generate_design_system.py", "--check"),
    ("generate_plasma_svgs.py", "--check"),
    ("generate_visual_assets.py", "--check"),
    ("generate_cursors.py", "--check"),
    ("generate_sound_theme.py", "--check"),
    ("render_wallpaper.py", "--check"),
    ("render_artwork_evidence.py", "--check"),
    ("check_plasma_rasters.py",),
    ("build_store_packages.py", "--output-dir", "{STORE_DIR}"),
    ("validate_store_packages.py", "--archive-dir", "{STORE_DIR}"),
    ("check_store_kpackages.py", "--archive-dir", "{STORE_DIR}"),
)
V6_GENERATOR_CHECKS = (
    ("capture_v6_baseline.py", "--check"),
    ("render_v6_north_star.py", "--check"),
    ("render_v6_previews.py", "--check"),
    ("render_v6_motion_evidence.py", "--check"),
    ("measure_v6_phase3_performance.py", "--check"),
    ("render_v6_session_evidence.py", "--check"),
    ("measure_v6_phase5_performance.py", "--check"),
    ("render_v6_edge_evidence.py", "--check"),
    ("check_v6_accessibility.py", "--check"),
    ("measure_v6_phase7_performance.py", "--check"),
)
QML_SURFACES = (
    "sddm/NoxForge/Main.qml",
    "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/splash/Splash.qml",
    "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/logout/Logout.qml",
    "kwin/tabbox/io.github.loofiboss.noxforge.desktop/contents/ui/main.qml",
    "kwin/tabbox/io.github.loofiboss.noxforge.desktop/contents/ui/Switcher.qml",
)


def preflight(*, skip_rpm: bool) -> None:
    required = ["cmake", "ninja", "c++", "magick", "ffmpeg", "git", "xz", "rpm", "kpackagetool6"]
    if not skip_rpm:
        required.extend(("rpmbuild", "rpmlint"))
    missing = sorted(command for command in required if not shutil.which(command))
    try:
        find_qmllint()
    except RuntimeError:
        missing.append("qmllint")
    if missing:
        raise RuntimeError(
            "environment preflight failed; repository checks were not started; "
            "missing required tools: " + ", ".join(sorted(set(missing)))
        )
    print("Environment preflight passed: " + ", ".join(sorted(set(required + ["qmllint"]))))


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
    for mode in ("-bb", "-bs"):
        run(
            [
                "rpmbuild",
                mode,
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
    built_sha256 = hashlib.sha256(binary[0].read_bytes()).hexdigest()
    manifest = json.loads((ROOT / "distribution/release-manifest.json").read_text(encoding="utf-8"))
    budget = next(item["budgetBytes"] for item in manifest["artifacts"] if item["key"] == "rpm")
    if binary[0].stat().st_size > budget:
        raise RuntimeError(f"RPM exceeds the manifest budget: {binary[0].stat().st_size} > {budget}")
    baseline_rpm = manifest["release"]["baseline"].get("rpmBytes")
    if isinstance(baseline_rpm, int) and binary[0].stat().st_size > round(baseline_rpm * 1.25):
        print(
            "Warning: RPM exceeds the normal V7 growth bound: "
            f"{binary[0].stat().st_size} > {round(baseline_rpm * 1.25)}"
        )
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
    print(f"Fedora RPM contract passed: {binary[0].name} ({built_sha256})")


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

    preflight(skip_rpm=arguments.skip_rpm)

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    generator_checks = GENERATOR_CHECKS

    run([sys.executable, "scripts/validate.py"])
    with tempfile.TemporaryDirectory(prefix="noxforge-store-gate-") as store_temp:
        for command in generator_checks:
            expanded = [part.replace("{STORE_DIR}", store_temp) for part in command]
            run([sys.executable, f"scripts/{expanded[0]}", *expanded[1:]])
        # The package validator is intentionally run after the builder so the
        # Store/portable archive graph is exercised on every gate.
    with tempfile.TemporaryDirectory(prefix="noxforge-python-gate-") as test_temp:
        test_report = Path(test_temp) / "python-tests.json"
        run([sys.executable, "scripts/run_python_tests.py", "--report", str(test_report)])
        counts = json.loads(test_report.read_text(encoding="utf-8"))
        if not counts.get("successful"):
            raise RuntimeError("repository Python gate failed")
        print(
            "Derived Python gate counts: "
            f"{counts['passed']} passed, {counts['skipped']} skipped, "
            f"{counts['testsRun']} total"
        )
    run([sys.executable, "scripts/check_v6_phase3_sanitizers.py"])

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
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as error:
        print(
            "repository gate failed after environment preflight: "
            + " ".join(map(str, error.cmd)),
            file=sys.stderr,
        )
        raise SystemExit(1) from error
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from error
