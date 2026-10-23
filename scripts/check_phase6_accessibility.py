#!/usr/bin/env python3
"""Create deterministic Phase 6 accessibility review evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/evidence/v5/accessibility-review.json"
THEME_ID = "io.github.loofiboss.noxforge.desktop"
RUNTIME_QML = (
    ROOT / "sddm/NoxForge/Main.qml",
    ROOT / f"look-and-feel/{THEME_ID}/contents/splash/Splash.qml",
    ROOT / f"look-and-feel/{THEME_ID}/contents/logout/Logout.qml",
    ROOT / f"kwin/tabbox/{THEME_ID}/contents/ui/Switcher.qml",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def linear(channel: int) -> float:
    value = channel / 255
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def luminance(value: str) -> float:
    red, green, blue = (int(value[index : index + 2], 16) for index in (1, 3, 5))
    return 0.2126 * linear(red) + 0.7152 * linear(green) + 0.0722 * linear(blue)


def contrast(first: str, second: str) -> float:
    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def system_font() -> str:
    result = subprocess.run(
        ["fc-match", "--format=%{family}", "sans-serif"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def create_report() -> dict[str, object]:
    tokens = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))
    colors = tokens["colors"]
    ratios = {}
    for pair in tokens["contrastPairs"]:
        actual = round(contrast(colors[pair["foreground"]], colors[pair["background"]]), 2)
        minimum = pair["minimumRatio"]
        if actual < minimum:
            raise RuntimeError(f"{pair['name']} contrast is {actual}, below {minimum}")
        ratios[pair["name"]] = {"actual": actual, "minimum": minimum}

    qml_text = {str(path.relative_to(ROOT)): path.read_text(encoding="utf-8") for path in RUNTIME_QML}
    hardcoded_fonts = [
        path for path, text in qml_text.items() if re.search(r"\bfont\.family\s*:", text)
    ]
    if hardcoded_fonts:
        raise RuntimeError(f"runtime QML hardcodes font families: {hardcoded_fonts}")
    if "KDE's configured system font is the only application and shell typeface." not in (
        ROOT / "DESIGN.md"
    ).read_text(encoding="utf-8"):
        raise RuntimeError("DESIGN.md does not preserve the system-font contract")

    sddm = qml_text["sddm/NoxForge/Main.qml"]
    logout = qml_text[f"look-and-feel/{THEME_ID}/contents/logout/Logout.qml"]
    splash = qml_text[f"look-and-feel/{THEME_ID}/contents/splash/Splash.qml"]
    switcher = qml_text[f"kwin/tabbox/{THEME_ID}/contents/ui/Switcher.qml"]
    assertions = {
        "keyboardOnly": all(
            value in sddm + logout
            for value in ("KeyNavigation.tab", "KeyNavigation.backtab", "Accessible.name")
        ),
        "rtl": all("LayoutMirroring.enabled" in text for text in (sddm, logout, switcher)),
        "reducedMotion": (
            tokens["motion"]["reducedMotion"]["durationMs"] == 0
            and tokens["motion"]["reducedMotion"]["spatialMotion"] is False
            and all(
                value in splash + switcher
                for value in ("reducedMotionDuration", "Kirigami.Units.longDuration <= 0")
            )
        ),
        "scaleCoverage": True,
        "colorIndependentStates": all(
            tokens["states"]["hierarchy"][state]["indicator"] != "none"
            for state in ("focus", "checked", "selected", "busy", "error", "success")
        ),
    }
    session = json.loads(
        (ROOT / "docs/evidence/v5/session-surfaces.json").read_text(encoding="utf-8")
    )
    scales = {(item["width"], item["height"]) for item in session["captures"]}
    assertions["scaleCoverage"] = scales == {
        (1280, 720),
        (1920, 1080),
        (2560, 1440),
        (3440, 1440),
    }
    if not all(assertions.values()):
        failed = [name for name, passed in assertions.items() if not passed]
        raise RuntimeError(f"accessibility assertions failed: {failed}")

    sources = {
        str(path.relative_to(ROOT)): digest(path)
        for path in (
            ROOT / "DESIGN.md",
            ROOT / "design/tokens.json",
            ROOT / "docs/evidence/v5/session-surfaces.json",
            *RUNTIME_QML,
        )
    }
    return {
        "schemaVersion": 1,
        "phase": 6,
        "reviewStatus": "passed",
        "systemFont": system_font(),
        "hardcodedRuntimeFontFamilies": [],
        "contrastPairs": ratios,
        "reviews": assertions,
        "colorVisionReview": {
            "result": "passed",
            "method": "Every semantic color state also has a named non-color indicator.",
            "indicators": {
                state: tokens["states"]["hierarchy"][state]["indicator"]
                for state in ("focus", "checked", "selected", "busy", "error", "success")
            },
        },
        "sources": sources,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    report = create_report()
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if arguments.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != encoded:
            raise SystemExit("Phase 6 accessibility evidence is missing or stale")
        print("Phase 6 accessibility evidence is current")
        return 0
    OUTPUT.write_text(encoded, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
