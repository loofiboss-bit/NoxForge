#!/usr/bin/env python3
"""Validate the stable v7 qualification and exact local release evidence."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "design/v7-candidate-contract.json"
QUALIFICATION_PATH = ROOT / "docs/evidence/v7/qualification.json"
LIVE_PATH = ROOT / "docs/evidence/v7/live/manifest.json"
UPGRADE_PATH = ROOT / "docs/evidence/v7/upgrade-matrix.json"
NOTES_PATH = ROOT / "docs/releases/v7.0.0.md"
MANUAL_PATH = ROOT / "docs/MANUAL_TESTING.md"
PREPARE_PATH = ROOT / "scripts/prepare_v7_candidate.py"
INSTALL_PATH = ROOT / "scripts/install-system.sh"
UNINSTALL_PATH = ROOT / "scripts/uninstall-system.sh"
EVIDENCE_PATH = ROOT / "docs/evidence/v7/candidate/phase8.json"
CHECK = "--check" in sys.argv[1:]
REQUIRED_COMPOSED_CHECKS = {
    "applications-maximize-restore",
    "aurorae-edges-and-states",
    "core-and-session-icons",
    "plasma-shell-surfaces",
    "blur-enabled-disabled",
    "session-surfaces",
    "tabbox-state-matrix",
    "motion-matrix",
    "keyboard-focus-and-activation",
    "translation-expansion",
    "rtl-layout",
    "runtime-readback",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(text: str, fragments: tuple[str, ...], subject: str) -> None:
    missing = [fragment for fragment in fragments if fragment not in text]
    if missing:
        raise RuntimeError(f"{subject} contract drift: {', '.join(missing)}")


def git_text(*arguments: str) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={ROOT}", "-C", str(ROOT), *arguments],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0:
        raise RuntimeError(f"qualification Git lineage check failed: {result.stdout.strip()}")
    return result.stdout.strip()


def verify_source_commit(commit: str, version: str) -> None:
    if git_text("cat-file", "-t", commit) != "commit":
        raise RuntimeError("qualification sourceCommit does not identify a commit")
    git_text("merge-base", "--is-ancestor", commit, "HEAD")
    if git_text("show", f"{commit}:VERSION") != version:
        raise RuntimeError("qualification sourceCommit is not a stable source commit")
    spec = git_text("show", f"{commit}:packaging/noxforge.spec")
    if not re.search(rf"^Version:\s+{re.escape(version)}$", spec, re.MULTILINE):
        raise RuntimeError("qualification sourceCommit does not contain the stable RPM version")


def verify_live_files(manifest: dict[str, object], evidence_root: Path) -> None:
    declared = manifest.get("files")
    if not isinstance(declared, dict) or not declared:
        raise RuntimeError("live manifest does not bind its evidence files")
    actual = {
        path.relative_to(evidence_root).as_posix()
        for path in evidence_root.rglob("*")
        if path.is_file() and path.name != "manifest.json"
    }
    if set(declared) != actual:
        missing = sorted(set(declared) - actual)
        unbound = sorted(actual - set(declared))
        raise RuntimeError(
            "live evidence file set drifted"
            + (f"; missing: {', '.join(missing)}" if missing else "")
            + (f"; unbound: {', '.join(unbound)}" if unbound else "")
        )
    for relative, raw_entry in declared.items():
        relative_path = PurePosixPath(relative)
        if relative_path.is_absolute() or ".." in relative_path.parts or "." in relative_path.parts:
            raise RuntimeError(f"unsafe live evidence path: {relative}")
        if not isinstance(raw_entry, dict):
            raise RuntimeError(f"invalid live evidence entry: {relative}")
        path = evidence_root.joinpath(*relative_path.parts)
        if sha256(path) != raw_entry.get("sha256") or path.stat().st_size != raw_entry.get("bytes"):
            raise RuntimeError(f"live evidence hash or size drifted: {relative}")
        if path.suffix == ".png" and png_size(path) != raw_entry.get("pixelSize"):
            raise RuntimeError(f"live evidence pixel dimensions drifted: {relative}")


def png_size(path: Path) -> list[int]:
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"invalid PNG evidence: {path}")
    return [int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")]


def build_evidence() -> dict[str, object]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    qualification = json.loads(QUALIFICATION_PATH.read_text(encoding="utf-8"))
    live_manifest = json.loads(LIVE_PATH.read_text(encoding="utf-8"))
    upgrade = json.loads(UPGRADE_PATH.read_text(encoding="utf-8"))
    notes = NOTES_PATH.read_text(encoding="utf-8")
    manual = MANUAL_PATH.read_text(encoding="utf-8")
    prepare = PREPARE_PATH.read_text(encoding="utf-8")
    install = INSTALL_PATH.read_text(encoding="utf-8")
    uninstall = UNINSTALL_PATH.read_text(encoding="utf-8")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if version != "7.0.0":
        raise RuntimeError("Phase 8 release qualification requires VERSION 7.0.0")

    candidate = qualification.get("candidate", {})
    if (
        qualification.get("schemaVersion") != 2
        or qualification.get("releaseState") != "release"
        or qualification.get("releaseReady") is not True
        or candidate.get("version") != version
        or candidate.get("sourceRef") != f"v{version}"
        or not re.fullmatch(r"[0-9a-f]{40}", str(candidate.get("sourceCommit", "")))
        or candidate.get("worktreeDirty") is not False
        or candidate.get("package") != f"noxforge-{version}-1.fc44.x86_64.rpm"
        or len(candidate.get("artifacts", [])) != 6
        or qualification.get("releaseBlockers") != []
    ):
        raise RuntimeError("stable v7 qualification identity or lineage is incomplete")
    verify_source_commit(str(candidate["sourceCommit"]), version)
    release_contract = qualification.get("releaseContract", {})
    if release_contract.get("assetCount") != 6 or len(release_contract.get("assetKinds", [])) != 6:
        raise RuntimeError("stable v7 qualification must preserve the six-asset contract")

    live = {case["id"]: case for case in qualification.get("liveCases", [])}
    missing_live = sorted(set(contract["mandatoryLiveCases"]) - set(live))
    if missing_live:
        raise RuntimeError("mandatory live matrix is incomplete: " + ", ".join(missing_live))
    if any(live[case_id].get("status") != "passed" for case_id in contract["mandatoryLiveCases"]):
        raise RuntimeError("every mandatory v7 live case must pass")

    expected_cases = {
        "single-100",
        "single-125",
        "single-140",
        "single-150",
        "single-175",
        "single-200",
        "mixed-100-140",
        "mixed-100-200",
    }
    live_cases = {case.get("id"): case for case in live_manifest.get("cases", [])}
    package = live_manifest.get("package", {})
    if (
        live_manifest.get("schemaVersion") != 1
        or live_manifest.get("version") != version
        or set(live_cases) != expected_cases
        or any(case.get("status") != "passed" for case in live_cases.values())
        or set(live_manifest.get("requiredChecksPerCase", [])) != REQUIRED_COMPOSED_CHECKS
        or any(set(case.get("checks", [])) != REQUIRED_COMPOSED_CHECKS for case in live_cases.values())
        or not isinstance(package, dict)
        or package.get("nevra") != f"noxforge-{version}-1.fc44.x86_64"
        or package.get("rpmVerify") != "passed"
    ):
        raise RuntimeError("exact-RPM composed live manifest is incomplete")
    verify_live_files(live_manifest, LIVE_PATH.parent)

    upgrade_candidate = upgrade.get("candidate", {})
    upgrade_result = upgrade.get("result", {})
    if (
        upgrade.get("status") != "passed"
        or upgrade.get("version") != version
        or upgrade_candidate.get("path") != f"noxforge-{version}-1.fc44.x86_64.rpm"
        or upgrade_result.get("candidateNevra") != f"noxforge-{version}-1.fc44.x86_64"
        or upgrade_result.get("configurationPreservation") != "passed"
        or upgrade_result.get("themeApplied") is not False
        or upgrade_result.get("hostMutated") is not False
    ):
        raise RuntimeError("disposable Fedora v6-to-v7 lifecycle evidence is incomplete")

    require(
        notes,
        (
            "Corrected behavior",
            "Qualification status and limitations",
            "100/125/140/150/175/200",
            "100+140/100+200",
            "System Settings",
            "Dolphin",
            "Konsole",
            "translation",
            "expansion",
            "RTL",
            "Installation and upgrade",
            "Rollback",
            "Hardware blur",
            "PAM",
            "authentication",
        ),
        "release notes",
    )
    if "UNQUALIFIED" in notes or "not release-ready" in notes:
        raise RuntimeError("stable release notes retain a development-only warning")
    require(
        manual,
        (
            "V7 Phase 8 mandatory live matrix",
            "100% + 140%",
            "100% + 200%",
            "normal, reduced/disabled, and deliberately slow motion",
        ),
        "manual qualification",
    )
    require(
        prepare,
        (
            "unqualified-local-development",
            "archiveIsByteReproducible",
            "unsigned-local-development",
            "hostInstalled\": False",
            "themeActivated\": False",
            "published\": False",
            "rpmbuild",
            "SHA256SUMS",
        ),
        "historical candidate staging",
    )
    for forbidden in ("curl", "wget", "gh release", "git push", "plasma-apply-", "kwriteconfig", "qdbus"):
        if forbidden in prepare:
            raise RuntimeError(f"candidate staging contains forbidden external or activation command: {forbidden}")
    require(install, ("NOXFORGE_BUILD_ROOT", "DESTDIR"), "isolated install")
    require(uninstall, ("NOXFORGE_BUILD_ROOT", "install_manifest.txt"), "isolated rollback")

    return {
        "schemaVersion": 2,
        "version": version,
        "phase": 8,
        "result": "release-gate-passed",
        "candidateState": "qualified-stable-release",
        "releaseReady": True,
        "localGate": {
            "status": "passed",
            "categories": {
                category: "passed" for category in contract["localGate"]["requiredPassedCategories"]
            },
            "freshV6Upgrade": "passed",
            "exactSourceCommit": candidate["sourceCommit"],
        },
        "artifactPolicy": {
            "output": "canonical release workflow",
            "assetCount": 6,
            "hostInstallAllowed": False,
            "themeActivationAllowed": False,
            "publicationRequiresExactTag": True,
        },
        "liveQualification": {
            "status": "passed",
            "qualifiesLiveSession": True,
            "requiredScales": contract["requiredScales"],
            "requiredMixedOutputs": contract["requiredMixedOutputs"],
            "cases": {
                case_id: {"priority": live[case_id]["priority"], "status": "passed"}
                for case_id in contract["mandatoryLiveCases"]
            },
        },
        "releaseBlockers": [],
        "limitations": qualification["limitations"],
        "evidenceBoundary": {
            "offscreenIsLiveEvidence": False,
            "physicalLimitationsRemainUnclaimed": True,
            "packageInstallationAppliesTheme": False,
        },
        "sourceHashes": {
            "contract": sha256(CONTRACT_PATH),
            "qualification": sha256(QUALIFICATION_PATH),
            "liveManifest": sha256(LIVE_PATH),
            "upgradeMatrix": sha256(UPGRADE_PATH),
            "releaseNotes": sha256(NOTES_PATH),
            "manualGate": sha256(MANUAL_PATH),
            "candidateStaging": sha256(PREPARE_PATH),
            "isolatedInstall": sha256(INSTALL_PATH),
            "isolatedUninstall": sha256(UNINSTALL_PATH),
        },
    }


def main() -> int:
    try:
        payload = json.dumps(build_evidence(), indent=2) + "\n"
    except (KeyError, OSError, RuntimeError, ValueError) as error:
        print(f"NoxForge v7 candidate check failed: {error}", file=sys.stderr)
        return 1
    if CHECK:
        if not EVIDENCE_PATH.is_file() or EVIDENCE_PATH.read_text(encoding="utf-8") != payload:
            print("NoxForge v7 candidate evidence drifted", file=sys.stderr)
            return 1
        print("NoxForge v7 stable release qualification check passed")
        return 0
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(payload, encoding="utf-8", newline="\n")
    print("Wrote NoxForge v7 stable release evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
