#!/usr/bin/env python3
"""Validate the v7 local-candidate and honest release-readiness boundary."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "design/v7-candidate-contract.json"
QUALIFICATION_PATH = ROOT / "docs/evidence/v7/qualification.json"
NOTES_PATH = ROOT / "docs/releases/v7.0.0.md"
MANUAL_PATH = ROOT / "docs/MANUAL_TESTING.md"
PREPARE_PATH = ROOT / "scripts/prepare_v7_candidate.py"
INSTALL_PATH = ROOT / "scripts/install-system.sh"
UNINSTALL_PATH = ROOT / "scripts/uninstall-system.sh"
EVIDENCE_PATH = ROOT / "docs/evidence/v7/candidate/phase8.json"
CHECK = "--check" in sys.argv[1:]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(text: str, fragments: tuple[str, ...], subject: str) -> None:
    missing = [fragment for fragment in fragments if fragment not in text]
    if missing:
        raise RuntimeError(f"{subject} contract drift: {', '.join(missing)}")


def build_evidence() -> dict[str, object]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    qualification = json.loads(QUALIFICATION_PATH.read_text(encoding="utf-8"))
    notes = NOTES_PATH.read_text(encoding="utf-8")
    manual = MANUAL_PATH.read_text(encoding="utf-8")
    prepare = PREPARE_PATH.read_text(encoding="utf-8")
    install = INSTALL_PATH.read_text(encoding="utf-8")
    uninstall = UNINSTALL_PATH.read_text(encoding="utf-8")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if version != contract["version"] or not version.endswith("-dev"):
        raise RuntimeError("Phase 8 must remain bound to the development version")
    candidate = qualification.get("candidate", {})
    if (
        qualification.get("releaseState") != "development"
        or qualification.get("releaseReady") is not False
        or candidate.get("sourceCommit") is not None
        or candidate.get("artifacts") != []
    ):
        raise RuntimeError("qualification invented stable lineage or release artifacts")

    live = {case["id"]: case for case in qualification.get("liveCases", [])}
    missing_live = sorted(set(contract["mandatoryLiveCases"]) - set(live))
    if missing_live:
        raise RuntimeError("mandatory live matrix is incomplete: " + ", ".join(missing_live))
    if any(live[case_id]["status"] != "pending" for case_id in contract["mandatoryLiveCases"]):
        raise RuntimeError("unavailable mandatory v7 live cases must remain pending")
    if not any(live[case_id].get("priority") == "P0" for case_id in contract["mandatoryLiveCases"]):
        raise RuntimeError("pending P0 release boundary is missing")

    require(
        notes,
        (
            "UNQUALIFIED DEVELOPMENT NOTES",
            "not release-ready",
            "100/125/140/150/175/200",
            "100+140/100+200",
            "System Settings",
            "Dolphin",
            "Konsole",
            "Keyboard-only",
            "translation expansion",
            "RTL",
            "Installation and upgrade",
            "Rollback",
        ),
        "release notes",
    )
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
        "candidate staging",
    )
    for forbidden in ("curl", "wget", "gh release", "git push", "plasma-apply-", "kwriteconfig", "qdbus"):
        if forbidden in prepare:
            raise RuntimeError(f"candidate staging contains forbidden external or activation command: {forbidden}")
    require(install, ("NOXFORGE_BUILD_ROOT", "DESTDIR"), "isolated install")
    require(uninstall, ("NOXFORGE_BUILD_ROOT", "install_manifest.txt"), "isolated rollback")

    return {
        "schemaVersion": 1,
        "version": version,
        "phase": 8,
        "result": "local-gate-passed-release-gate-open",
        "candidateState": contract["candidateState"],
        "releaseReady": False,
        "localGate": {
            "status": "passed",
            "categories": {
                category: "passed" for category in contract["localGate"]["requiredPassedCategories"]
            },
            "freshV6Upgrade": "pending",
            "exactSourceCommit": "pending",
        },
        "artifactPolicy": contract["artifactPolicy"],
        "liveQualification": {
            "status": "pending",
            "qualifiesLiveSession": False,
            "requiredScales": contract["requiredScales"],
            "requiredMixedOutputs": contract["requiredMixedOutputs"],
            "cases": {
                case_id: {"priority": live[case_id]["priority"], "status": live[case_id]["status"]}
                for case_id in contract["mandatoryLiveCases"]
            },
        },
        "releaseBlockers": [
            "mandatory composed Wayland and input-capable live matrix",
            "fresh v6 to v7 upgrade in a clean Fedora 44 KDE environment",
            "clean exact-source commit lineage",
        ],
        "evidenceBoundary": contract["evidenceBoundary"],
        "sourceHashes": {
            "contract": sha256(CONTRACT_PATH),
            "qualification": sha256(QUALIFICATION_PATH),
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
        print("NoxForge v7 local-candidate boundary check passed")
        return 0
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(payload, encoding="utf-8", newline="\n")
    print("Wrote NoxForge v7 local-candidate evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
