#!/usr/bin/env python3
"""Qualify the public v6 to exact v7 RPM lifecycle in disposable Fedora 44."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "localhost/noxforge-v7-live:fedora44"
PUBLIC_V6 = "6.0.0-1.fc44"


def run(command: list[str], *, timeout: int = 900) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lifecycle_script(candidate_nevra: str) -> str:
    return f"""set -euo pipefail
export LC_ALL=C.UTF-8
mkdir -p /root/.config /etc/sddm.conf.d
printf '%s\n' '[General]' 'ColorScheme=UserSentinel' > /root/.config/kdeglobals
printf '%s\n' '[Windows]' 'Placement=Smart' > /root/.config/kwinrc
printf '%s\n' '[Containments][1]' 'plugin=org.kde.plasma.folder' > /root/.config/plasma-org.kde.plasma.desktop-appletsrc
printf '%s\n' '[Theme]' 'Current=UserSentinel' > /etc/sddm.conf.d/99-user-sentinel.conf
sentinel_hash() {{ sha256sum /root/.config/kdeglobals /root/.config/kwinrc /root/.config/plasma-org.kde.plasma.desktop-appletsrc /etc/sddm.conf.d/99-user-sentinel.conf; }}
before_hash=$(sentinel_hash)

dnf -y install dnf5-plugins >/dev/null
dnf -y copr enable loofitheboss/noxforge >/dev/null
dnf -y install noxforge-6.0.0 >/dev/null
test "$(rpm -q --qf '%{{VERSION}}-%{{RELEASE}}' noxforge)" = "{PUBLIC_V6}"
rpm -V noxforge
noxforge-doctor --json > /tmp/doctor-v6.json

dnf -y upgrade /candidate.rpm >/dev/null
test "$(rpm -q noxforge)" = "{candidate_nevra}"
rpm -V noxforge
noxforge-doctor --json > /tmp/doctor-upgrade.json
test "$(sentinel_hash)" = "$before_hash"

dnf -y reinstall /candidate.rpm >/dev/null
test "$(rpm -q noxforge)" = "{candidate_nevra}"
rpm -V noxforge
test "$(sentinel_hash)" = "$before_hash"

dnf -y downgrade noxforge-6.0.0 >/dev/null
test "$(rpm -q --qf '%{{VERSION}}-%{{RELEASE}}' noxforge)" = "{PUBLIC_V6}"
rpm -V noxforge
test "$(sentinel_hash)" = "$before_hash"

dnf -y upgrade /candidate.rpm >/dev/null
test "$(rpm -q noxforge)" = "{candidate_nevra}"
rpm -V noxforge
test "$(sentinel_hash)" = "$before_hash"

dnf -y remove --no-autoremove noxforge >/dev/null
test "$(rpm -q noxforge 2>/dev/null || true)" = 'package noxforge is not installed'
test ! -e /usr/share/noxforge/VERSION
test ! -e /usr/share/plasma/look-and-feel/io.github.loofiboss.noxforge.desktop
test ! -e /usr/lib64/qt6/plugins/styles/libnoxforge6.so
test "$(sentinel_hash)" = "$before_hash"

dnf -y install /candidate.rpm >/dev/null
test "$(rpm -q noxforge)" = "{candidate_nevra}"
rpm -V noxforge
noxforge-doctor --json > /tmp/doctor-fresh.json
test "$(sentinel_hash)" = "$before_hash"
dnf -y remove --no-autoremove noxforge >/dev/null
test "$(sentinel_hash)" = "$before_hash"

python3 - <<'PY'
import json
from pathlib import Path

doctors = {{
    name: json.loads(Path(path).read_text())
    for name, path in (
        ("publicV6", "/tmp/doctor-v6.json"),
        ("upgradeV7", "/tmp/doctor-upgrade.json"),
        ("freshV7", "/tmp/doctor-fresh.json"),
    )
}}
for name, report in doctors.items():
    if report.get("status") != "ok" or report.get("missing"):
        raise SystemExit(f"doctor failed for {{name}}: {{report}}")
print("NOXFORGE_LIFECYCLE_JSON=" + json.dumps({{
    "publicV6Nevra": "noxforge-{PUBLIC_V6}.x86_64",
    "candidateNevra": "{candidate_nevra}",
    "steps": [
        "public-v6-install",
        "v6-to-v7-upgrade",
        "v7-repeated-install",
        "v7-to-v6-rollback",
        "second-v6-to-v7-upgrade",
        "v7-uninstall",
        "fresh-v7-install",
        "final-v7-uninstall",
    ],
    "rpmVerify": "passed-at-every-installed-state",
    "configurationPreservation": "passed",
    "themeApplied": False,
    "hostMutated": False,
    "doctor": {{name: {{
        "status": report["status"],
        "expectedVersion": report.get("expectedVersion"),
        "packageVersion": report.get("packageVersion"),
        "mixedVersions": report.get("mixedVersions"),
        "missing": report.get("missing"),
    }} for name, report in doctors.items()}},
}}, sort_keys=True))
PY
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rpm", type=Path, required=True, help="exact v7 binary RPM")
    parser.add_argument("--image", default=IMAGE, help="prepared Fedora 44 KDE image")
    parser.add_argument(
        "--evidence",
        type=Path,
        default=ROOT / "docs/evidence/v7/upgrade-matrix.json",
    )
    args = parser.parse_args()
    rpm = args.rpm.resolve()
    evidence = args.evidence.resolve()
    if not rpm.is_file() or rpm.suffix != ".rpm" or rpm.name.endswith(".src.rpm"):
        raise RuntimeError("--rpm must identify an existing binary RPM")
    if shutil.which("podman") is None:
        raise RuntimeError("podman is required for the disposable Fedora 44 lifecycle")
    candidate_nevra = run(["rpm", "-qp", "--qf", "%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}", str(rpm)]).stdout
    if not candidate_nevra.startswith("noxforge-7.0.0"):
        raise RuntimeError(f"candidate is not a NoxForge v7 RPM: {candidate_nevra}")
    image_id = run(
        ["podman", "image", "inspect", args.image, "--format", "{{.Id}}"]
    ).stdout.strip()
    result = run(
        [
            "podman",
            "run",
            "--rm",
            "--network=host",
            "--name",
            "noxforge-v7-upgrade-matrix",
            "-v",
            f"{rpm}:/candidate.rpm:ro,Z",
            args.image,
            "bash",
            "-lc",
            lifecycle_script(candidate_nevra),
        ]
    )
    marker = "NOXFORGE_LIFECYCLE_JSON="
    payload_line = next((line for line in result.stdout.splitlines() if line.startswith(marker)), None)
    if payload_line is None:
        raise RuntimeError("disposable lifecycle completed without a structured result")
    lifecycle = json.loads(payload_line.removeprefix(marker))
    payload = {
        "schemaVersion": 1,
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "status": "passed",
        "environment": {
            "distribution": "Fedora 44",
            "containerImage": args.image,
            "containerImageId": image_id,
            "publicV6Repository": "copr:copr.fedorainfracloud.org:loofitheboss:noxforge",
            "networkPurpose": "resolve the already-public v6 package and Fedora dependencies",
        },
        "candidate": {
            "path": rpm.name,
            "nevra": candidate_nevra,
            "sha256": sha256(rpm),
        },
        "result": lifecycle,
        "evidenceBoundary": {
            "disposableContainer": True,
            "hostPackageChanged": False,
            "hostThemeChanged": False,
            "configurationSentinels": [
                "/root/.config/kdeglobals",
                "/root/.config/kwinrc",
                "/root/.config/plasma-org.kde.plasma.desktop-appletsrc",
                "/etc/sddm.conf.d/99-user-sentinel.conf",
            ],
        },
    }
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"NoxForge v7 disposable Fedora 44 lifecycle passed: {candidate_nevra}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        print(f"NoxForge v7 upgrade matrix failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
