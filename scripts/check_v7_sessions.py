#!/usr/bin/env python3
"""Validate the v7 SDDM, Logout, and TabBox contract and evidence."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "design/v7-session-contract.json"
SDDM_PATH = ROOT / "sddm/NoxForge/Main.qml"
LOGOUT_PATH = ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/logout/Logout.qml"
TABBOX_PATH = ROOT / "kwin/tabbox/io.github.loofiboss.noxforge.desktop/contents/ui/Switcher.qml"
TOKENS_PATH = ROOT / "design/tokens.json"
CMAKE_PATH = ROOT / "CMakeLists.txt"
RENDERER_PATH = ROOT / "tools/session_renderer.cpp"
EVIDENCE_PATH = ROOT / "docs/evidence/v7/session/phase5.json"
CHECK = "--check" in sys.argv[1:]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(text: str, fragments: tuple[str, ...], surface: str) -> None:
    missing = [fragment for fragment in fragments if fragment not in text]
    if missing:
        raise RuntimeError(f"{surface} contract drift: {', '.join(missing)}")


def build_evidence() -> dict[str, object]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    tokens = json.loads(TOKENS_PATH.read_text(encoding="utf-8"))
    sddm = SDDM_PATH.read_text(encoding="utf-8")
    logout = LOGOUT_PATH.read_text(encoding="utf-8")
    tabbox = TABBOX_PATH.read_text(encoding="utf-8")
    cmake = CMAKE_PATH.read_text(encoding="utf-8")
    renderer = RENDERER_PATH.read_text(encoding="utf-8")

    if tokens["geometry"]["largeControlHeight"] != contract["importantControlHeight"]:
        raise RuntimeError("important control height does not match the v7 session contract")
    require(
        sddm,
        (
            "import QtQuick.Controls as QQC2",
            "QQC2.BusyIndicator",
            "KeyboardIndicator.KeyState",
            'qsTr("Caps Lock is on")',
            "Layout.minimumHeight: 40",
            "Qt.callLater(root.focusFirstAction)",
            "sddm.login",
            "sddm.suspend",
            "sddm.reboot",
            "sddm.powerOff",
        ),
        "SDDM",
    )
    if "↻" in sddm:
        raise RuntimeError("SDDM still contains a functional Unicode busy glyph")
    require(logout, tuple(f'iconName: "{name}"' for name in contract["logout"]["distinctActionIcons"]), "Logout")
    require(
        tabbox,
        (
            '"application-x-executable"',
            "Keys.onReturnPressed",
            "Keys.onSpacePressed",
            "Accessible.role: Accessible.List",
            "Accessible.role: Accessible.ListItem",
            "required property string caption",
            "required property var icon",
            "required property bool minimized",
        ),
        "TabBox",
    )
    for scale in ("1.0", "1.25", "1.4", "1.5", "2.0"):
        if f"QT_SCALE_FACTOR=${{scale}}" not in cmake or scale not in cmake:
            raise RuntimeError(f"offscreen session scale is missing: {scale}")
    for scenario in ("empty", "many", "long-rtl", "keyboard", "missing-icon"):
        if scenario not in cmake and scenario not in renderer:
            raise RuntimeError(f"TabBox scenario is missing: {scenario}")

    return {
        "schemaVersion": 1,
        "version": contract["version"],
        "phase": 5,
        "result": "passed",
        "importantControlHeight": contract["importantControlHeight"],
        "authenticationBoundary": contract["authenticationBoundary"],
        "sddm": contract["sddm"],
        "logout": contract["logout"],
        "tabbox": contract["tabbox"],
        "offscreenScaleMatrix": {
            "status": "required-by-phase-gate",
            "scales": contract["offscreenScaleMatrix"],
            "surfaces": ["sddm", "splash", "logout", "tabbox"],
        },
        "mixedDpi": contract["mixedDpi"],
        "liveQualification": contract["liveQualification"],
        "sourceHashes": {
            "contract": sha256(CONTRACT_PATH),
            "tokens": sha256(TOKENS_PATH),
            "sddm": sha256(SDDM_PATH),
            "logout": sha256(LOGOUT_PATH),
            "tabbox": sha256(TABBOX_PATH),
            "cmake": sha256(CMAKE_PATH),
            "renderer": sha256(RENDERER_PATH),
        },
    }


def main() -> int:
    try:
        payload = json.dumps(build_evidence(), indent=2) + "\n"
    except (KeyError, OSError, RuntimeError, ValueError) as error:
        print(f"NoxForge v7 session check failed: {error}", file=sys.stderr)
        return 1
    if CHECK:
        if not EVIDENCE_PATH.is_file() or EVIDENCE_PATH.read_text(encoding="utf-8") != payload:
            print("NoxForge v7 session evidence drifted", file=sys.stderr)
            return 1
        print("NoxForge v7 session-surface check passed")
        return 0
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(payload, encoding="utf-8", newline="\n")
    print("Wrote NoxForge v7 session-surface evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
