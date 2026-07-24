#!/usr/bin/env python3
"""Synchronize generated public version consumers with VERSION."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILES = {
    "design/tokens.json": (
        r'(?m)^(\s*"version":\s*)".*?"(,?)$',
        r'\g<1>"{version}"\g<2>',
    ),
    "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop/metadata.json": (
        r'(?m)^(\s*"Version":\s*)".*?"(,?)$',
        r'\g<1>"{version}"\g<2>',
    ),
    "look-and-feel/io.github.loofiboss.noxforge.desktop/metadata.json": (
        r'(?m)^(\s*"Version":\s*)".*?"(,?)$',
        r'\g<1>"{version}"\g<2>',
    ),
    "look-and-feel/io.github.loofiboss.noxforge.desktop/manifest.json": (
        r'(?m)^(\s*"Version":\s*)".*?"(,?)$',
        r'\g<1>"{version}"\g<2>',
    ),
    "kwin/tabbox/io.github.loofiboss.noxforge.desktop/metadata.json": (
        r'(?m)^(\s*"Version":\s*)".*?"(,?)$',
        r'\g<1>"{version}"\g<2>',
    ),
    "wallpapers/NoxForge/metadata.json": (
        r'(?m)^(\s*"Version":\s*)".*?"(,?)$',
        r'\g<1>"{version}"\g<2>',
    ),
    "docs/evidence/v3/qualification.json": (
        r'(?m)^(\s*"version":\s*)".*?"(,?)$',
        r'\g<1>"{version}"\g<2>',
    ),
    "aurorae/io.github.loofiboss.noxforge.desktop/metadata.desktop": (
        r"(?m)^X-KDE-PluginInfo-Version=.*$",
        "X-KDE-PluginInfo-Version={version}",
    ),
    "sddm/NoxForge/metadata.desktop": (
        r"(?m)^Version=.*$",
        "Version={version}",
    ),
    "packaging/noxforge.spec": (
        r"(?m)^Version:\s+.*$",
        "Version:        {version}",
    ),
    "docs/man/noxforge-doctor.1": (
        r'(?m)^\.TH NOXFORGE-DOCTOR 1 "July 2026" "NoxForge .*?" "User Commands"$',
        '.TH NOXFORGE-DOCTOR 1 "July 2026" "NoxForge {version}" "User Commands"',
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail on version drift")
    arguments = parser.parse_args()
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    drift: list[Path] = []

    outputs: dict[Path, str] = {}
    for relative, (pattern, replacement) in VERSION_FILES.items():
        path = ROOT / relative
        source = path.read_text(encoding="utf-8")
        output, count = re.subn(pattern, replacement.format(version=version), source, count=1)
        if count != 1:
            raise RuntimeError(f"version field not found in {relative}")
        outputs[path] = output

    for path, output in outputs.items():
        if path.read_text(encoding="utf-8") != output:
            drift.append(path)
            if not arguments.check:
                path.write_text(output, encoding="utf-8", newline="\n")

    if arguments.check and drift:
        print(
            "Version drift: "
            + ", ".join(path.relative_to(ROOT).as_posix() for path in drift),
            file=sys.stderr,
        )
        return 1
    action = "Verified" if arguments.check else "Synchronized"
    print(f"{action} {len(outputs)} version consumers at {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
