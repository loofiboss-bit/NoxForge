#!/usr/bin/env python3
"""Verify that V9 install cycles preserve V8-era desktop and login settings."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run(command: list[str], environment: dict[str, str]) -> None:
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"{' '.join(command)} failed: {detail}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-root", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    arguments = parser.parse_args()
    build_root = arguments.build_root.resolve()
    if not (build_root / "cmake_install.cmake").is_file():
        raise SystemExit("--build-root must be a configured NoxForge CMake build")

    with tempfile.TemporaryDirectory(prefix="noxforge-v9-migration-") as name:
        temporary = Path(name)
        home = temporary / "home"
        config = home / ".config"
        data = home / ".local/share"
        stage = temporary / "stage"

        user_sentinels = {
            "kdeglobals": "[KDE]\nLookAndFeelPackage=org.kde.breeze.desktop\n",
            "plasma-org.kde.plasma.desktop-appletsrc": "[Containments][1]\nplugin=org.kde.plasma.folder\n",
            "plasmawallpaperrc": "[Wallpapers]\nusersWallpapers=file:///v8/user-choice.png\n",
        }
        system_sentinels = {
            "etc/plasmalogin.conf": (
                "[Greeter][Wallpaper][org.kde.image][General]\n"
                "Image=file:///v8/plm-user-choice.png\n"
            ),
            "etc/sddm.conf.d/99-user-choice.conf": "[Theme]\nCurrent=UserChoice\n",
        }
        for relative, content in user_sentinels.items():
            write(config / relative, content)
        for relative, content in system_sentinels.items():
            write(stage / relative, content)

        before_user = tree_digest(config)
        before_system = tree_digest(stage / "etc")
        environment = os.environ.copy()
        environment.update(
            HOME=str(home),
            XDG_DATA_HOME=str(data),
            XDG_CONFIG_HOME=str(config),
            NOXFORGE_BUILD_ROOT=str(build_root),
            NOXFORGE_SYSTEM_ROOT=str(stage),
        )

        for _ in range(2):
            run([str(ROOT / "scripts/install.sh"), "--user"], environment)
        for _ in range(2):
            run([str(ROOT / "scripts/install-system.sh"), "--system"], environment)
        after_install_user = tree_digest(config)
        after_install_system = tree_digest(stage / "etc")

        for _ in range(2):
            run([str(ROOT / "scripts/uninstall.sh"), "--user"], environment)
        for _ in range(2):
            run([str(ROOT / "scripts/uninstall-system.sh"), "--system"], environment)
        after_remove_user = tree_digest(config)
        after_remove_system = tree_digest(stage / "etc")

        passed = (
            before_user == after_install_user == after_remove_user
            and before_system == after_install_system == after_remove_system
        )
        report = {
            "schemaVersion": 1,
            "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
            "status": "passed" if passed else "failed",
            "sourceState": "v8-era user choices",
            "cycles": {"install": 2, "uninstall": 2},
            "configuration": ["Plasma", "panel", "wallpaper", "PLM", "SDDM"],
            "hashes": {
                "user": [before_user, after_install_user, after_remove_user],
                "system": [before_system, after_install_system, after_remove_system],
            },
            "hostMutated": False,
        }
        if arguments.report:
            report_path = arguments.report.resolve()
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
        if not passed:
            raise SystemExit("V8-to-V9 configuration preservation failed")
        print("V8-to-V9 configuration preservation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
