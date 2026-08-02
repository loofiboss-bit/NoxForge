#!/usr/bin/env python3
"""Stage an unqualified v7 development artifact set without host mutation."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "dist/v7-local-candidate"
QUALIFICATION = ROOT / "docs/evidence/v7/qualification.json"
GATE = ROOT / "docs/evidence/v7/candidate/phase8-gate.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(command), flush=True)
    return subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        capture_output=capture,
        text=True,
    )


def load_build_module():
    spec = importlib.util.spec_from_file_location("noxforge_build", ROOT / "scripts/build.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load scripts/build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_unqualified_development_state() -> tuple[str, dict[str, object]]:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    qualification = json.loads(QUALIFICATION.read_text(encoding="utf-8"))
    if not version.endswith("-dev"):
        raise RuntimeError("local v7 staging requires a development VERSION")
    if (
        qualification.get("releaseState") != "development"
        or qualification.get("releaseReady") is not False
        or qualification.get("candidate", {}).get("sourceCommit") is not None
    ):
        raise RuntimeError("qualification must remain unqualified development evidence")
    blocking = [
        case["id"]
        for case in qualification.get("liveCases", [])
        if case.get("priority") in {"P0", "P1"}
        and case.get("status") in {"pending", "blocked", "failed"}
    ]
    if not any(
        case.get("priority") == "P0" and case.get("status") in {"pending", "blocked", "failed"}
        for case in qualification.get("liveCases", [])
    ):
        raise RuntimeError("the required pending P0 release boundary was lost")
    if not GATE.is_file() or "LOCAL GATE PASSED; RELEASE GATE OPEN" not in GATE.read_text(encoding="utf-8"):
        raise RuntimeError("Phase 8 local gate evidence is missing or incomplete")
    return version, {"qualification": qualification, "blockingLiveCases": blocking}


def build_rpms(source_archive: Path, temporary: Path) -> tuple[Path, Path]:
    for command in ("rpmbuild", "rpm"):
        if not shutil.which(command):
            raise RuntimeError(f"required local package tool is missing: {command}")
    topdir = temporary / "rpmbuild"
    for directory in ("BUILD", "BUILDROOT", "RPMS", "SOURCES", "SPECS", "SRPMS"):
        (topdir / directory).mkdir(parents=True)
    shutil.copy2(source_archive, topdir / "SOURCES" / source_archive.name)
    run(
        [
            "rpmbuild",
            "-ba",
            "--define",
            f"_topdir {topdir}",
            str(ROOT / "packaging/noxforge.spec"),
        ]
    )
    source_packages = sorted(topdir.glob("SRPMS/*.src.rpm"))
    binary_packages = [
        path
        for path in sorted(topdir.glob("RPMS/*/*.rpm"))
        if "-debuginfo-" not in path.name and "-debugsource-" not in path.name
    ]
    if len(source_packages) != 1 or len(binary_packages) != 1:
        raise RuntimeError("expected exactly one source RPM and one installable binary RPM")
    return binary_packages[0], source_packages[0]


def stage(output: Path) -> dict[str, object]:
    version, state = require_unqualified_development_state()
    if output.exists() and any(output.iterdir()):
        raise RuntimeError(f"output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="noxforge-v7-candidate-") as name:
        temporary = Path(name)
        build_module = load_build_module()
        archive_a, _, hash_a = build_module.build(
            temporary / "archive-a/build", temporary / "archive-a/dist"
        )
        archive_b, _, hash_b = build_module.build(
            temporary / "archive-b/build", temporary / "archive-b/dist"
        )
        if hash_a != hash_b or archive_a.read_bytes() != archive_b.read_bytes():
            raise RuntimeError("independent development source archives are not byte-identical")
        binary_rpm, source_rpm = build_rpms(archive_a, temporary)

        staged_archive = output / archive_a.name
        staged_binary = output / binary_rpm.name
        staged_source_rpm = output / source_rpm.name
        for source, destination in (
            (archive_a, staged_archive),
            (binary_rpm, staged_binary),
            (source_rpm, staged_source_rpm),
        ):
            shutil.copy2(source, destination)

    repository_head = run(["git", "rev-parse", "HEAD"], capture=True).stdout.strip()
    status = run(["git", "status", "--porcelain=v1"], capture=True).stdout.splitlines()
    fedora_release = "unknown"
    try:
        fedora_release = Path("/etc/fedora-release").read_text(encoding="utf-8").strip()
    except OSError:
        pass

    artifacts = {
        "sourceArchive": {"name": staged_archive.name, "sha256": sha256(staged_archive)},
        "binaryRpm": {"name": staged_binary.name, "sha256": sha256(staged_binary)},
        "sourceRpm": {"name": staged_source_rpm.name, "sha256": sha256(staged_source_rpm)},
    }
    provenance = {
        "schemaVersion": 1,
        "version": version,
        "candidateState": "unqualified-local-development",
        "releaseReady": False,
        "exactSourceCommit": None,
        "repositoryHead": repository_head,
        "sourceRef": "working-tree",
        "worktreeDirty": bool(status),
        "sourceIdentity": {
            "archiveSha256": artifacts["sourceArchive"]["sha256"],
            "archiveIsByteReproducible": True,
            "repositoryStatusEntryCount": len(status),
        },
        "qualification": {
            "path": QUALIFICATION.relative_to(ROOT).as_posix(),
            "sha256": sha256(QUALIFICATION),
            "blockingLiveCases": state["blockingLiveCases"],
        },
        "artifacts": artifacts,
        "buildEnvironment": {
            "operatingSystem": fedora_release,
            "architecture": platform.machine(),
        },
        "policy": {
            "signature": "unsigned-local-development",
            "hostInstalled": False,
            "themeActivated": False,
            "published": False,
        },
    }
    provenance_path = output / "provenance.json"
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8", newline="\n")
    checksums = [
        f"{sha256(path)}  {path.name}"
        for path in (staged_archive, staged_binary, staged_source_rpm, provenance_path)
    ]
    checksum_path = output / "SHA256SUMS"
    checksum_path.write_text("\n".join(checksums) + "\n", encoding="utf-8", newline="\n")
    print(f"Staged unqualified local development artifacts in {output}")
    print("Release readiness: false; mandatory live qualification remains pending")
    return provenance


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    output = arguments.output.resolve()
    if output == Path("/"):
        parser.error("--output must not be the filesystem root")
    try:
        stage(output)
    except (OSError, RuntimeError, subprocess.CalledProcessError, ValueError) as error:
        print(f"NoxForge v7 local candidate staging failed: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
