#!/usr/bin/env python3
"""Validate the v7 native-style interaction contract and evidence."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "design/v7-style-contract.json"
STYLE_PATH = ROOT / "src/style/noxforgestyle.cpp"
PROBE_PATH = ROOT / "tests/qt/style_probe.cpp"
EVIDENCE_PATH = ROOT / "docs/evidence/v7/style/phase3.json"
CHECK = "--check" in sys.argv[1:]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_evidence() -> dict[str, object]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    style = STYLE_PATH.read_text(encoding="utf-8")
    probe = PROBE_PATH.read_text(encoding="utf-8")
    required_style = (
        "case PM_ScrollBarExtent: return 16;",
        "settings.contains(QStringLiteral(\"SingleClick\"))",
        "case SH_UnderlineShortcut:",
        "case SH_MenuBar_AltKeyNavigation:",
        "QCommonStyle::styleHint(hint, option, widget, returnData)",
        "visualSlider.setHeight(qMin(6, slider.height()))",
        "visualSlider.setWidth(qMin(6, slider.width()))",
    )
    missing = [fragment for fragment in required_style if fragment not in style]
    if missing:
        raise RuntimeError("native style contract drift: " + ", ".join(missing))
    required_probe = (
        "KDE/SingleClick",
        "SH_UnderlineShortcut",
        "SH_MenuBar_AltKeyNavigation",
        "PM_ScrollBarExtent",
        "visibleTrackRows",
    )
    missing_probe = [fragment for fragment in required_probe if fragment not in probe]
    if missing_probe:
        raise RuntimeError("native style probe drift: " + ", ".join(missing_probe))
    return {
        "schemaVersion": 1,
        "version": contract["version"],
        "phase": 3,
        "result": "passed",
        "interactionPolicy": contract["interactionPolicy"],
        "scrollbar": contract["scrollbar"],
        "selection": contract["selection"],
        "automatedProbe": {
            **contract["automatedProbe"],
            "status": "required-by-phase-gate",
            "cases": [
                "single-click true false and base fallback",
                "base mnemonic visibility",
                "base Alt navigation",
                "16 pixel scrollbar pointer extent",
                "six pixel maximum visual track",
                "scrollbar page and thumb hit testing",
            ],
        },
        "liveApplicationEvidence": {
            "status": "pending",
            "reason": "Requires complete Global Theme activation in an input-capable disposable or real Plasma session."
        },
        "sourceHashes": {
            "contract": sha256(CONTRACT_PATH),
            "style": sha256(STYLE_PATH),
            "probe": sha256(PROBE_PATH),
        },
    }


def main() -> int:
    try:
        payload = json.dumps(build_evidence(), indent=2) + "\n"
    except (KeyError, OSError, RuntimeError, ValueError) as error:
        print(f"NoxForge v7 style check failed: {error}", file=sys.stderr)
        return 1
    if CHECK:
        if not EVIDENCE_PATH.is_file() or EVIDENCE_PATH.read_text(encoding="utf-8") != payload:
            print("NoxForge v7 style evidence drifted", file=sys.stderr)
            return 1
        print("NoxForge v7 native style check passed")
        return 0
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(payload, encoding="utf-8", newline="\n")
    print("Wrote NoxForge v7 native style evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
