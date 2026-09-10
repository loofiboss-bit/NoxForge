#!/usr/bin/env python3
"""Exercise isolated V10 lifecycle; actual V9 upgrade requires explicit baseline."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

from check_v9_migration import tree_digest, write

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], environment: dict[str, str], source: Path) -> None:
    result = subprocess.run(command, cwd=source, env=environment, capture_output=True, text=True, timeout=600)
    if result.returncode:
        raise RuntimeError(f"{' '.join(command)}: {(result.stderr or result.stdout)[-6000:]}")


def validate_build(build: Path, source: Path) -> None:
    cache = build / "CMakeCache.txt"
    if not (build / "cmake_install.cmake").is_file() or not cache.is_file():
        raise ValueError(f"Not a configured build: {build}")
    entries = dict(line.split("=", 1) for line in cache.read_text().splitlines() if "=" in line)
    if Path(entries.get("CMAKE_HOME_DIRECTORY:INTERNAL", "")).resolve() != source.resolve():
        raise ValueError(f"Build {build} does not belong to source {source}")
    if entries.get("CMAKE_INSTALL_PREFIX:PATH") != "/usr":
        raise ValueError("Lifecycle staging requires CMAKE_INSTALL_PREFIX=/usr")


def metadata_version(data: Path, expected: str) -> None:
    for relative in ("noxforge/VERSION", "plasma/look-and-feel/io.github.loofiboss.noxforge.desktop/metadata.json"):
        path = data / relative
        if not path.is_file():
            raise AssertionError(f"Missing installed version metadata: {relative}")
        actual = json.loads(path.read_text())["KPlugin"]["Version"] if path.suffix == ".json" else path.read_text().strip()
        if actual != expected:
            raise AssertionError(f"{relative}: expected {expected}, got {actual}")


def lifecycle(mode: str, current: Path, baseline: Path | None, baseline_build: Path | None) -> dict:
    with tempfile.TemporaryDirectory(prefix=f"noxforge-v10-{mode}-") as temporary:
        root = Path(temporary)
        home, stage = root / "home", root / "stage"
        config, data = home / ".config", home / ".local/share"
        environment = os.environ.copy()
        environment.update(HOME=str(home), XDG_CONFIG_HOME=str(config), XDG_DATA_HOME=str(data),
                           XDG_CACHE_HOME=str(home / ".cache"), XDG_STATE_HOME=str(home / ".local/state"),
                           NOXFORGE_SYSTEM_ROOT=str(stage), NOXFORGE_BUILD_ROOT=str(current))
        for relative in ("kdeglobals", "plasma-org.kde.plasma.desktop-appletsrc", "plasmawallpaperrc"):
            write(config / relative, f"[UserChoice]\nvalue={relative}\n")
        for relative in ("plasmalogin.conf", "sddm.conf.d/user.conf"):
            write(stage / "etc" / relative, "[Theme]\nCurrent=UserChoice\n")
        installed = data if mode == "user" else stage / "usr/share"
        unrelated = installed / "icons/NoxForge/user-unrelated.txt"
        write(unrelated, "Unrelated user file\n")
        initial = (tree_digest(config), tree_digest(stage / "etc"))
        phases = []
        owned: set[Path] = set()

        def check(phase: str) -> None:
            hashes = (tree_digest(config), tree_digest(stage / "etc"))
            if hashes != initial or unrelated.read_text() != "Unrelated user file\n":
                raise AssertionError(f"Configuration or unrelated file changed during {phase}")
            phases.append({"phase": phase, "status": "passed", "configurationHashes": list(hashes)})

        def install(source: Path, build: Path, phase: str) -> None:
            environment["NOXFORGE_BUILD_ROOT"] = str(build)
            script = "install.sh" if mode == "user" else "install-system.sh"
            run(["bash", str(source / "scripts" / script), f"--{mode}"], environment, source)
            metadata_version(installed, (source / "VERSION").read_text().strip())
            manifest = data / "noxforge/.owned-files" if mode == "user" else build / "install_manifest.txt"
            for entry in manifest.read_text().splitlines():
                path = data / entry if mode == "user" else stage / entry.lstrip("/")
                if not path.resolve().is_relative_to(root.resolve()):
                    raise AssertionError("Owned manifest escaped staging root")
                owned.add(path)
            check(phase)

        def remove(source: Path, build: Path, phase: str) -> None:
            environment["NOXFORGE_BUILD_ROOT"] = str(build)
            script = "uninstall.sh" if mode == "user" else "uninstall-system.sh"
            run(["bash", str(source / "scripts" / script), f"--{mode}"], environment, source)
            leftovers = [str(path.relative_to(root)) for path in owned if path.exists()]
            if leftovers:
                raise AssertionError(f"Owned files remain after {phase}: {leftovers[:10]}")
            owned.clear()
            check(phase)

        if baseline:
            install(baseline, baseline_build, "baseline-v9-install")
        install(ROOT, current, "v10-upgrade" if baseline else "v10-install")
        install(ROOT, current, "v10-reinstall")
        remove(ROOT, current, "v10-uninstall")
        remove(ROOT, current, "v10-repeat-uninstall") if mode == "system" else check("v10-removed")
        if baseline:
            install(baseline, baseline_build, "v9-rollback-install")
            remove(ROOT, baseline_build, "v9-rollback-uninstall-current-tool")
        return {"mode": mode, "status": "passed", "phases": phases}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-root", required=True, type=Path)
    parser.add_argument("--baseline-source", type=Path)
    parser.add_argument("--baseline-build", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    current = args.build_root.resolve()
    baseline = args.baseline_source.resolve() if args.baseline_source else None
    report = {"schemaVersion": 1, "version": (ROOT / "VERSION").read_text().strip(),
              "status": "failed", "actualUpgradeRollback": "pending", "hostMutated": False, "cycles": []}
    try:
        validate_build(current, ROOT)
        if args.baseline_build and not baseline:
            raise ValueError("--baseline-build requires --baseline-source")
        with tempfile.TemporaryDirectory(prefix="noxforge-v9-build-") as temporary:
            baseline_build = args.baseline_build.resolve() if args.baseline_build else Path(temporary) / "build"
            if baseline:
                if (baseline / "VERSION").read_text().strip() != "9.0.0":
                    raise ValueError("Actual baseline must be V9.0.0")
                if not args.baseline_build:
                    environment = os.environ.copy()
                    environment.update(HOME=temporary, XDG_CONFIG_HOME=temporary + "/config", XDG_DATA_HOME=temporary + "/data")
                    run(["cmake", "-S", str(baseline), "-B", str(baseline_build), "-DCMAKE_INSTALL_PREFIX=/usr"], environment, baseline)
                    run(["cmake", "--build", str(baseline_build), "-j2"], environment, baseline)
                validate_build(baseline_build, baseline)
            for mode in ("user", "system"):
                report["cycles"].append(lifecycle(mode, current, baseline, baseline_build if baseline else None))
        report["status"] = "passed"
        if baseline:
            report["actualUpgradeRollback"] = "passed"
            report["baselineVersion"] = "9.0.0"
        else:
            report["pendingReason"] = "Actual V9 source/build not supplied; current-version lifecycle only."
    except (OSError, ValueError, AssertionError, RuntimeError, subprocess.TimeoutExpired) as error:
        report["error"] = str(error)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
