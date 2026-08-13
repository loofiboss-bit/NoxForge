#!/usr/bin/env python3
"""Synchronize generated consumers with the active release manifest.

Historical v6/v7 evidence is deliberately not a version consumer.  The active
version comes from ``VERSION`` and is checked against
``distribution/release-manifest.json`` so a stale release line cannot silently
be published.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "distribution/release-manifest.json"
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)

VERSION_FILES = {
    "design/tokens.json": ((r'(?m)^(\s*"version":\s*)".*?"(,?)$', r'\g<1>"{version}"\g<2>'),),
    "design/motion-contract.json": ((r'(?m)^(\s*"version":\s*)".*?"(,?)$', r'\g<1>"{version}"\g<2>'),),
    "design/edge-polish-contract.json": ((r'(?m)^(\s*"version":\s*)".*?"(,?)$', r'\g<1>"{version}"\g<2>'),),
    "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop/metadata.json": ((r'(?m)^(\s*"Version":\s*)".*?"(,?)$', r'\g<1>"{version}"\g<2>'),),
    "look-and-feel/io.github.loofiboss.noxforge.desktop/metadata.json": ((r'(?m)^(\s*"Version":\s*)".*?"(,?)$', r'\g<1>"{version}"\g<2>'),),
    "look-and-feel/io.github.loofiboss.noxforge.desktop/manifest.json": ((r'(?m)^(\s*"Version":\s*)".*?"(,?)$', r'\g<1>"{version}"\g<2>'),),
    "kwin/tabbox/io.github.loofiboss.noxforge.desktop/metadata.json": ((r'(?m)^(\s*"Version":\s*)".*?"(,?)$', r'\g<1>"{version}"\g<2>'),),
    "wallpapers/NoxForge/metadata.json": ((r'(?m)^(\s*"Version":\s*)".*?"(,?)$', r'\g<1>"{version}"\g<2>'),),
    "wallpapers/NoxForge-Quiet/metadata.json": ((r'(?m)^(\s*"Version":\s*)".*?"(,?)$', r'\g<1>"{version}"\g<2>'),),
    "wallpapers/NoxForge-Ultrawide/metadata.json": ((r'(?m)^(\s*"Version":\s*)".*?"(,?)$', r'\g<1>"{version}"\g<2>'),),
    "aurorae/io.github.loofiboss.noxforge.desktop/metadata.desktop": ((r"(?m)^X-KDE-PluginInfo-Version=.*$", "X-KDE-PluginInfo-Version={version}"),),
    "sddm/NoxForge/metadata.desktop": ((r"(?m)^Version=.*$", "Version={version}"),),
    "media/manifest.json": ((r'(?m)^(\s*"release":\s*)".*?"(,?)$', r'\g<1>"{version}"\g<2>'),),
    "docs/evidence/v9/qualification.json": ((r'(?m)^(\s*"version":\s*)".*?"(,?)$', r'\g<1>"{version}"\g<2>'),),
    "docs/evidence/v9/automated-gate.md": ((r'(?m)^Version:\s+.*$', "Version: {version}"),),
    "packaging/noxforge.spec": (
        (r"(?m)^%global upstream_version\s+.*$", "%global upstream_version {release_version}"),
        (r"(?m)^Version:\s+.*$", "Version:        {rpm_version}"),
    ),
    "docs/man/noxforge-doctor.1": ((r'(?m)^\.TH NOXFORGE-DOCTOR 1 "[^"]+" "NoxForge .*?" "User Commands"$', '.TH NOXFORGE-DOCTOR 1 "August 2026" "NoxForge {version}" "User Commands"'),),
}


def load_manifest() -> dict:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 2:
        raise RuntimeError("unsupported release manifest schema")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail on version drift")
    arguments = parser.parse_args()
    manifest = load_manifest()
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(version):
        raise RuntimeError(f"VERSION is not SemVer: {version!r}")
    declared = manifest["release"]["version"]
    if declared != version:
        raise RuntimeError(f"manifest release version {declared!r} does not match VERSION {version!r}")
    rpm_version = version.replace("-", "~", 1)
    drift: list[Path] = []
    outputs: dict[Path, str] = {}
    replacement_count = 0
    for relative, replacements in VERSION_FILES.items():
        path = ROOT / relative
        if not path.exists():
            raise RuntimeError(f"version consumer is missing: {relative}")
        output = path.read_text(encoding="utf-8")
        for pattern, replacement in replacements:
            output, count = re.subn(
                pattern,
                replacement.format(
                    version=version,
                    rpm_version=rpm_version,
                    release_version=manifest["release"]["stableVersion"],
                ),
                output,
                count=1,
            )
            if count != 1:
                raise RuntimeError(f"version field not found in {relative}")
            replacement_count += count
        outputs[path] = output
    for path, output in outputs.items():
        if path.read_text(encoding="utf-8") != output:
            drift.append(path)
            if not arguments.check:
                path.write_text(output, encoding="utf-8", newline="\n")
    if arguments.check and drift:
        print("Version drift: " + ", ".join(path.relative_to(ROOT).as_posix() for path in drift), file=sys.stderr)
        return 1
    action = "Verified" if arguments.check else "Synchronized"
    print(f"{action} {replacement_count} version fields across {len(outputs)} consumers at {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
