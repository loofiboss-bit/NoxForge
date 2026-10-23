#!/usr/bin/env python3
"""Create deterministic, source-bound v6 accessibility qualification evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/evidence/v6/accessibility-review.json"
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


def platform_probe() -> tuple[dict[str, object], dict[str, object]]:
    with tempfile.TemporaryDirectory(prefix="noxforge-v6-accessibility-") as temporary:
        build = Path(temporary) / "build"
        subprocess.run(
            [
                "cmake",
                "-S",
                str(ROOT),
                "-B",
                str(build),
                "-G",
                "Ninja",
                "-DCMAKE_BUILD_TYPE=Release",
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        subprocess.run(
            [
                "cmake",
                "--build",
                str(build),
                "--target",
                "noxforge_style",
                "noxforge_accessibility_probe",
                "noxforge_session_renderer",
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        environment = {
            **os.environ,
            "QT_QPA_PLATFORM": "offscreen",
            "QT_PLUGIN_PATH": str(build / "plugins"),
            "QT_STYLE_OVERRIDE": "NoxForge",
        }
        result = subprocess.run(
            [str(build / "noxforge_accessibility_probe")],
            cwd=ROOT,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        surfaces = {
            "sddm": ROOT / "sddm/NoxForge/Main.qml",
            "splash": ROOT
            / f"look-and-feel/{THEME_ID}/contents/splash/Splash.qml",
            "logout": ROOT
            / f"look-and-feel/{THEME_ID}/contents/logout/Logout.qml",
            "tabbox": ROOT / f"kwin/tabbox/{THEME_ID}/contents/ui/Switcher.qml",
        }
        reduced_results = {}
        for surface, qml in surfaces.items():
            output = Path(temporary) / f"{surface}-reduced-motion.json"
            subprocess.run(
                [
                    str(build / "noxforge_session_renderer"),
                    surface,
                    str(qml),
                    str(ROOT / "sddm/NoxForge/background.png"),
                    str(output),
                    "1280",
                    "720",
                    "reduced-probe",
                    str(ROOT),
                ],
                cwd=ROOT,
                env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
                check=True,
            )
            reduced_results[surface] = json.loads(output.read_text(encoding="utf-8"))
    return json.loads(result.stdout), {
        "result": (
            "passed"
            if all(item["result"] == "passed" for item in reduced_results.values())
            else "failed"
        ),
        "surfaces": reduced_results,
    }


def create_report() -> dict[str, object]:
    tokens_path = ROOT / "design/tokens.json"
    tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
    colors = tokens["colors"]
    ratios = {}
    for pair in tokens["contrastPairs"]:
        actual = round(
            contrast(colors[pair["foreground"]], colors[pair["background"]]), 2
        )
        minimum = pair["minimumRatio"]
        if actual < minimum:
            raise RuntimeError(f"{pair['name']} contrast is {actual}, below {minimum}")
        ratios[pair["name"]] = {"actual": actual, "minimum": minimum}

    qml_text = {
        path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
        for path in RUNTIME_QML
    }
    hardcoded_fonts = [
        path for path, text in qml_text.items() if re.search(r"\bfont\.family\s*:", text)
    ]
    if hardcoded_fonts:
        raise RuntimeError(f"runtime QML hardcodes font families: {hardcoded_fonts}")

    design = (ROOT / "DESIGN.md").read_text(encoding="utf-8")
    if "The KDE-configured system font is the only application and shell typeface." not in design:
        raise RuntimeError("DESIGN.md does not preserve the system-font contract")

    sddm = qml_text["sddm/NoxForge/Main.qml"]
    logout = qml_text[f"look-and-feel/{THEME_ID}/contents/logout/Logout.qml"]
    splash = qml_text[f"look-and-feel/{THEME_ID}/contents/splash/Splash.qml"]
    switcher = qml_text[f"kwin/tabbox/{THEME_ID}/contents/ui/Switcher.qml"]
    cmake = (ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
    session_contract = json.loads(
        (ROOT / "design/session-surface-contract.json").read_text(encoding="utf-8")
    )
    session_manifest = json.loads(
        (ROOT / "docs/evidence/v6/session/manifest.json").read_text(encoding="utf-8")
    )
    observed_scenarios = {
        capture["scenario"].removesuffix("-start").removesuffix("-mid").removesuffix("-end")
        for capture in session_manifest["captures"]
    }
    expected_scenarios = {
        scenario
        for scenarios in session_contract["v6ScenarioMatrix"].values()
        for scenario in scenarios
    }
    probe, reduced_motion_probe = platform_probe()
    reviews = {
        "colorIndependentStates": all(
            tokens["states"]["hierarchy"][state]["indicator"] != "none"
            for state in ("focus", "checked", "selected", "busy", "error", "success")
        ),
        "keyboardTraversal": all(
            value in sddm + logout
            for value in (
                "KeyNavigation.tab",
                "KeyNavigation.backtab",
                "Accessible.name",
                "Keys.onReturnPressed",
                "Keys.onSpacePressed",
            )
        ),
        "reducedMotion": (
            tokens["motion"]["reducedMotion"]["durationMs"] == 0
            and tokens["motion"]["reducedMotion"]["spatialMotion"] is False
            and all(
                value in splash + logout + switcher
                for value in ("reducedMotion", "MotionPolicy { id: motion }")
            )
            and "reduced" in observed_scenarios
            and reduced_motion_probe["result"] == "passed"
        ),
        "rtl": (
            all(
                "LayoutMirroring.enabled" in text
                for text in (sddm, logout, switcher)
            )
            and "long-rtl" in observed_scenarios
        ),
        "scaleCoverage": all(
            f"widget-gallery-ltr-{label} {scale}" in cmake
            and f"widget-gallery-rtl-{label} {scale}" in cmake
            for label, scale in (("100", "1.0"), ("125", "1.25"), ("140", "1.4"), ("200", "2.0"))
        ),
        "scenarioCoverage": expected_scenarios <= observed_scenarios,
        "systemFont": not hardcoded_fonts,
    }
    failed = [name for name, passed in reviews.items() if not passed]
    if failed:
        raise RuntimeError(f"v6 accessibility assertions failed: {failed}")

    preference = probe["contrastPreference"]
    if preference not in {"NoPreference", "HighContrast"}:
        raise RuntimeError(f"unexpected Qt contrast preference: {preference}")
    high_contrast = {
        "api": "QGuiApplication::styleHints()->accessibility()->contrastPreference()",
        "preference": preference,
        "exposed": probe["highContrastExposed"],
        "result": "passed" if probe["highContrastExposed"] else "not-exposed",
        "observation": (
            "The platform exposed HighContrast and every semantic contrast pair passes."
            if probe["highContrastExposed"]
            else "The Qt offscreen platform reported NoPreference; high contrast is not claimed."
        ),
    }

    source_paths = (
        ROOT / "CMakeLists.txt",
        ROOT / "DESIGN.md",
        tokens_path,
        ROOT / "design/motion-contract.json",
        ROOT / "design/session-surface-contract.json",
        ROOT / "docs/evidence/v6/session/manifest.json",
        ROOT / "scripts/check_v6_accessibility.py",
        ROOT / "tests/qt/accessibility_probe.cpp",
        ROOT / "tests/qt/motion_probe.cpp",
        ROOT / "tools/session_renderer.cpp",
        *RUNTIME_QML,
    )
    return {
        "schemaVersion": 1,
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "phase": 7,
        "reviewStatus": "passed",
        "kind": "automated-source-and-offscreen-platform-review",
        "liveInteraction": False,
        "platformProbe": probe,
        "reducedMotionProbe": reduced_motion_probe,
        "highContrastPreference": high_contrast,
        "hardcodedRuntimeFontFamilies": [],
        "contrastPairs": ratios,
        "reviews": reviews,
        "nonColorIndicators": {
            state: tokens["states"]["hierarchy"][state]["indicator"]
            for state in ("focus", "checked", "selected", "busy", "error", "success")
        },
        "sources": {
            path.relative_to(ROOT).as_posix(): digest(path)
            for path in sorted(set(source_paths))
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    report = create_report()
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if arguments.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != encoded:
            raise SystemExit("v6 accessibility evidence is missing or stale")
        print("v6 accessibility evidence is current")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(encoded, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
