#!/usr/bin/env python3
"""Synchronize generated public version consumers with VERSION."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
VERSION_FILES = {
    "design/tokens.json": ((
        r'(?m)^(\s*"version":\s*)".*?"(,?)$',
        r'\g<1>"{version}"\g<2>',
    ),),
    "design/motion-contract.json": ((
        r'(?m)^(\s*"version":\s*)".*?"(,?)$',
        r'\g<1>"{version}"\g<2>',
    ),),
    "design/edge-polish-contract.json": ((
        r'(?m)^(\s*"version":\s*)".*?"(,?)$',
        r'\g<1>"{version}"\g<2>',
    ),),
    "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop/metadata.json": ((
        r'(?m)^(\s*"Version":\s*)".*?"(,?)$',
        r'\g<1>"{version}"\g<2>',
    ),),
    "look-and-feel/io.github.loofiboss.noxforge.desktop/metadata.json": ((
        r'(?m)^(\s*"Version":\s*)".*?"(,?)$',
        r'\g<1>"{version}"\g<2>',
    ),),
    "look-and-feel/io.github.loofiboss.noxforge.desktop/manifest.json": ((
        r'(?m)^(\s*"Version":\s*)".*?"(,?)$',
        r'\g<1>"{version}"\g<2>',
    ),),
    "kwin/tabbox/io.github.loofiboss.noxforge.desktop/metadata.json": ((
        r'(?m)^(\s*"Version":\s*)".*?"(,?)$',
        r'\g<1>"{version}"\g<2>',
    ),),
    "wallpapers/NoxForge/metadata.json": ((
        r'(?m)^(\s*"Version":\s*)".*?"(,?)$',
        r'\g<1>"{version}"\g<2>',
    ),),
    "docs/evidence/v7/qualification.json": ((
        r'(?m)^(\s*"version":\s*)".*?"(,?)$',
        r'\g<1>"{version}"\g<2>',
    ),),
    "aurorae/io.github.loofiboss.noxforge.desktop/metadata.desktop": ((
        r"(?m)^X-KDE-PluginInfo-Version=.*$",
        "X-KDE-PluginInfo-Version={version}",
    ),),
    "sddm/NoxForge/metadata.desktop": ((
        r"(?m)^Version=.*$",
        "Version={version}",
    ),),
    "packaging/noxforge.spec": (
        (
            r"(?m)^%global upstream_version\s+.*$",
            "%global upstream_version {version}",
        ),
        (
            r"(?m)^Version:\s+.*$",
            "Version:        {rpm_version}",
        ),
    ),
    "docs/man/noxforge-doctor.1": ((
        r'(?m)^\.TH NOXFORGE-DOCTOR 1 "July 2026" "NoxForge .*?" "User Commands"$',
        '.TH NOXFORGE-DOCTOR 1 "July 2026" "NoxForge {version}" "User Commands"',
    ),),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail on version drift")
    arguments = parser.parse_args()
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(version):
        raise RuntimeError(f"VERSION is not SemVer: {version!r}")
    rpm_version = version.replace("-", "~", 1)
    drift: list[Path] = []

    outputs: dict[Path, str] = {}
    replacement_count = 0
    for relative, replacements in VERSION_FILES.items():
        path = ROOT / relative
        output = path.read_text(encoding="utf-8")
        for pattern, replacement in replacements:
            output, count = re.subn(
                pattern,
                replacement.format(version=version, rpm_version=rpm_version),
                output,
                count=1,
            )
            if count != 1:
                raise RuntimeError(f"version field not found in {relative}")
            replacement_count += 1
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
    print(f"{action} {replacement_count} version fields across {len(outputs)} consumers at {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
