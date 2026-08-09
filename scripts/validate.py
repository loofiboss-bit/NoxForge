#!/usr/bin/env python3
"""Validate NoxForge sources and package contracts using the standard library."""

from __future__ import annotations

import configparser
import gzip
import hashlib
import json
import math
import re
import struct
import subprocess
import sys
import wave
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME_ID = "io.github.loofiboss.noxforge.desktop"
REPOSITORY_URL = "https://github.com/loofiboss-bit/NoxForge"
V6_RELEASE_VERSION = "6.0.0"
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
PACKAGE_ROOTS = (
    ROOT / "plasma",
    ROOT / "aurorae",
    ROOT / "icons",
    ROOT / "wallpapers",
    ROOT / "look-and-feel",
    ROOT / "kwin",
    ROOT / "cursors",
    ROOT / "sounds",
    ROOT / "sddm",
)
POSITIONS = {"top", "topright", "right", "bottomright", "bottom", "bottomleft", "left", "topleft", "center"}
PLASMA_STATES = {
    "widgets/button.svg": {"normal", "hover", "focus", "pressed", "toolbutton-hover", "toolbutton-focus", "toolbutton-pressed"},
    "widgets/tasks.svg": {"normal", "hover", "focus", "attention", "minimized", "progress"},
    "widgets/viewitem.svg": {"normal", "hover", "selected", "selected+hover"},
    "widgets/lineedit.svg": {"base", "hover", "focus"},
    "widgets/plasmoidheading.svg": {"header", "footer"},
    "widgets/listitem.svg": {"normal", "hover", "pressed", "section"},
    "widgets/menubaritem.svg": {"normal", "hover", "pressed"},
    "widgets/frame.svg": {"plain", "raised", "sunken"},
    "widgets/tabbar.svg": {"north-active-tab", "south-active-tab", "east-active-tab", "west-active-tab"},
    "widgets/scrollbar.svg": {"background-horizontal", "background-vertical", "slider", "mouseover-slider"},
    "widgets/slider.svg": {"groove", "groove-highlight"},
    "widgets/switch.svg": {"inactive", "active"},
}

COLOR_SECTIONS = {
    "Colors:Button",
    "Colors:Complementary",
    "Colors:Header",
    "Colors:Header][Inactive",
    "Colors:Selection",
    "Colors:Tooltip",
    "Colors:View",
    "Colors:Window",
}
COLOR_KEYS = {
    "backgroundalternate",
    "backgroundnormal",
    "decorationfocus",
    "decorationhover",
    "foregroundactive",
    "foregroundinactive",
    "foregroundlink",
    "foregroundnegative",
    "foregroundneutral",
    "foregroundnormal",
    "foregroundpositive",
    "foregroundvisited",
}


class ValidationError(RuntimeError):
    """Raised when a source or package contract is invalid."""


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValidationError(f"invalid JSON {path.relative_to(ROOT)}: {error}") from error


def load_colors(path: Path) -> configparser.ConfigParser:
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    parser.optionxform = str.lower
    try:
        parser.read(path, encoding="utf-8")
    except (OSError, configparser.Error) as error:
        raise ValidationError(f"invalid color scheme {path.relative_to(ROOT)}: {error}") from error
    return parser


def validate_version() -> str:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(version):
        raise ValidationError(f"VERSION is not SemVer: {version!r}")
    return version


def relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first: str, second: str) -> float:
    light, dark = sorted(
        (relative_luminance(first), relative_luminance(second)),
        reverse=True,
    )
    return (light + 0.05) / (dark + 0.05)


def validate_tokens(version: str) -> dict[str, object]:
    tokens = load_json(ROOT / "design/tokens.json")
    if not isinstance(tokens, dict):
        raise ValidationError("design/tokens.json must contain an object")
    if tokens.get("themeId") != THEME_ID or tokens.get("version") != version:
        raise ValidationError("token identity or version does not match repository metadata")
    required_colors = {
        "background": "#0E1318",
        "surfaceSunken": "#10171C",
        "surface": "#151D23",
        "surfaceRaised": "#1B252C",
        "surfaceOverlay": "#222D35",
        "surfaceHover": "#232F36",
        "surfaceSelected": "#1E2B31",
        "border": "#2B3942",
        "borderStrong": "#43535C",
        "edgeHighlight": "#3C4B53",
        "outlineMuted": "#314049",
        "textPrimary": "#E8F0F2",
        "textSecondary": "#A6B4B9",
        "textDisabled": "#748289",
        "accent": "#A3FF47",
        "accentPressed": "#82D936",
        "accentInk": "#0E1318",
        "accentSoft": "#243528",
        "accentMuted": "#71994F",
        "detailCyan": "#22D3EE",
        "detailViolet": "#A78BFA",
        "negative": "#FF6B7A",
        "neutral": "#FBBF24",
        "shadowAmbient": "#090C0F",
        "shadowOverlay": "#050708",
    }
    if tokens.get("schemaVersion") != 5 or tokens.get("colors") != required_colors:
        raise ValidationError("design tokens do not match the locked NoxForge palette")
    geometry = tokens.get("geometry")
    semantic_roles = tokens.get("semanticRoles")
    opacity = tokens.get("opacity")
    elevation = tokens.get("elevation")
    overlay = tokens.get("overlay")
    shadow = tokens.get("shadow")
    motion = tokens.get("motion")
    states = tokens.get("states")
    typography = tokens.get("typography")
    iconography = tokens.get("iconography")
    hallmark = tokens.get("hallmark")
    if not all(
        isinstance(value, dict)
        for value in (
            geometry,
            semantic_roles,
            opacity,
            elevation,
            overlay,
            shadow,
            motion,
            states,
            typography,
            iconography,
            hallmark,
        )
    ):
        raise ValidationError("design token schema v5 objects are incomplete")
    if (
        geometry.get("forgeNotch") != 4
        or geometry.get("compactSpacing") != 4
        or geometry.get("standardSpacing") != 8
        or geometry.get("overlayRadius") != 8
        or geometry.get("controlHeight") != 32
        or geometry.get("largeControlHeight") != 40
    ):
        raise ValidationError("design geometry does not match Kinetic Precision")
    if opacity != {
        "enabled": 1.0,
        "inactive": 0.72,
        "disabled": 0.55,
        "subtle": 0.12,
        "scrim": 0.72,
    }:
        raise ValidationError("design opacity roles are incomplete")

    role_names = {
        "canvas",
        "sunken",
        "surface",
        "raised",
        "overlay",
        "control",
        "controlHover",
        "controlPressed",
        "selection",
        "primaryAction",
        "primaryActionPressed",
        "focus",
        "disabled",
        "busy",
        "error",
        "success",
    }
    if set(semantic_roles) != role_names:
        raise ValidationError("semantic color roles are incomplete")
    for name, role in semantic_roles.items():
        if not isinstance(role, dict) or set(role) != {"background", "foreground", "border"}:
            raise ValidationError(f"semantic role {name} is incomplete")
        if any(reference not in required_colors for reference in role.values()):
            raise ValidationError(f"semantic role {name} references an unknown color")

    if set(elevation) != {"flat", "surface", "raised", "overlay"}:
        raise ValidationError("elevation roles are incomplete")
    for name, level in elevation.items():
        if (
            not isinstance(level, dict)
            or set(level) != {"level", "shadow"}
            or not isinstance(level.get("level"), int)
            or level["level"] < 0
            or level.get("shadow") not in shadow
        ):
            raise ValidationError(f"elevation role {name} is invalid")
    if set(overlay) != {"none", "hover", "pressed", "busy", "selection", "scrim"}:
        raise ValidationError("overlay roles are incomplete")
    for name, layer in overlay.items():
        if (
            not isinstance(layer, dict)
            or layer.get("color") not in required_colors
            or not isinstance(layer.get("opacity"), (int, float))
            or not 0 <= layer["opacity"] <= 1
        ):
            raise ValidationError(f"overlay role {name} is invalid")
    if set(shadow) != {"none", "ambient", "overlay"}:
        raise ValidationError("shadow roles are incomplete")
    for name, recipe in shadow.items():
        if not isinstance(recipe, dict) or recipe.get("color") not in required_colors:
            raise ValidationError(f"shadow role {name} is invalid")
        if set(recipe) != {"color", "opacity", "offsetX", "offsetY", "blurRadius", "spreadRadius"}:
            raise ValidationError(f"shadow role {name} is incomplete")
        if (
            not isinstance(recipe["opacity"], (int, float))
            or not 0 <= recipe["opacity"] <= 1
        ):
            raise ValidationError(f"shadow role {name} has invalid opacity")
        dimensions = [recipe[key] for key in ("offsetX", "offsetY", "blurRadius", "spreadRadius")]
        if any(not isinstance(value, int) or value % 4 for value in dimensions):
            raise ValidationError(f"shadow role {name} breaks the 4 px grid")

    expected_motion = {
        "instantMs": 0,
        "pressMs": 90,
        "productiveMs": 120,
        "selectionMs": 140,
        "containerMs": 180,
        "expressiveMs": 260,
        "staggerMs": 24,
        "busyCycleMs": 900,
        "curves": {
            "productiveEnter": [0.2, 0.0, 0.0, 1.0],
            "standard": [0.4, 0.0, 0.2, 1.0],
            "exit": [0.4, 0.0, 1.0, 1.0],
            "expressive": [0.2, 0.0, 0.0, 1.0],
        },
        "reducedMotion": {
            "durationMs": 0,
            "spatialMotion": False,
            "busyIndicatorStatic": True,
            "opacityTransitions": False,
        },
    }
    if motion != expected_motion:
        raise ValidationError("design motion does not match Kinetic Precision")
    if states.get("focusStyle") != "single-2px-outline" or states.get("normalNotch") is not False:
        raise ValidationError("design state hierarchy does not match Kinetic Precision")
    hierarchy = states.get("hierarchy")
    state_names = {
        "default",
        "hover",
        "focus",
        "pressed",
        "checked",
        "selected",
        "disabled",
        "busy",
        "error",
        "success",
    }
    if not isinstance(hierarchy, dict) or set(hierarchy) != state_names:
        raise ValidationError("interactive state hierarchy is incomplete")
    motion_names = {
        "instantMs",
        "pressMs",
        "productiveMs",
        "selectionMs",
        "busyCycleMs",
    }
    indicator_names = {
        "none",
        "singleFocusRing",
        "checkGlyph",
        "leadingMarker",
        "busyGlyph",
        "errorGlyph",
        "successGlyph",
    }
    for name, state in hierarchy.items():
        if not isinstance(state, dict) or set(state) != {
            "role",
            "opacity",
            "elevation",
            "overlay",
            "indicator",
            "motion",
        }:
            raise ValidationError(f"interactive state {name} is incomplete")
        if (
            state["role"] not in semantic_roles
            or state["opacity"] not in opacity
            or state["elevation"] not in elevation
            or state["overlay"] not in overlay
            or state["indicator"] not in indicator_names
            or state["motion"] not in motion_names
        ):
            raise ValidationError(f"interactive state {name} has an invalid token reference")
    if (
        iconography.get("grid") != 24
        or iconography.get("opticalSizes") != [16, 22]
        or iconography.get("accentCoveragePercentMax") != 8
    ):
        raise ValidationError("iconography tokens are incomplete")
    typography_roles = typography.get("roles")
    expected_typography_roles = {
        "displayClock",
        "surfaceTitle",
        "sectionTitle",
        "body",
        "controlLabel",
        "metadata",
        "microLabel",
    }
    if (
        typography.get("family") != "system-ui"
        or not isinstance(typography_roles, dict)
        or set(typography_roles) != expected_typography_roles
    ):
        raise ValidationError("semantic typography roles are incomplete")
    for name, role in typography_roles.items():
        required = {"pixelSize", "weight", "tracking", "lineHeight"}
        if name == "displayClock":
            required.add("tabularNumbers")
        if not isinstance(role, dict) or set(role) != required:
            raise ValidationError(f"semantic typography role {name} is incomplete")
        if (
            not isinstance(role["pixelSize"], int)
            or role["pixelSize"] <= 0
            or not isinstance(role["lineHeight"], int)
            or role["lineHeight"] <= 0
            or role["lineHeight"] % 4
        ):
            raise ValidationError(f"semantic typography role {name} breaks the 4 px grid")

    contrast_pairs = tokens.get("contrastPairs")
    if not isinstance(contrast_pairs, list) or not contrast_pairs:
        raise ValidationError("documented contrast pairs are missing")
    covered_pairs: set[tuple[str, str]] = set()
    pair_names: set[str] = set()
    for pair in contrast_pairs:
        if not isinstance(pair, dict) or set(pair) != {
            "name",
            "foreground",
            "background",
            "minimumRatio",
        }:
            raise ValidationError("a documented contrast pair is incomplete")
        foreground = pair["foreground"]
        background = pair["background"]
        minimum = pair["minimumRatio"]
        if (
            pair["name"] in pair_names
            or foreground not in required_colors
            or background not in required_colors
            or not isinstance(minimum, (int, float))
        ):
            raise ValidationError("a documented contrast pair is invalid")
        pair_names.add(pair["name"])
        covered_pairs.add((foreground, background))
        actual = contrast_ratio(required_colors[foreground], required_colors[background])
        if actual < minimum:
            raise ValidationError(
                f"contrast pair {pair['name']} is {actual:.2f}:1, below {minimum:.2f}:1"
            )
    required_pairs = {
        (role["foreground"], role["background"])
        for role in semantic_roles.values()
    }
    if not required_pairs.issubset(covered_pairs):
        raise ValidationError("contrast coverage does not include every semantic role")

    score_names = {
        "philosophy",
        "hierarchy",
        "execution",
        "specificity",
        "restraint",
        "variety",
    }
    if set(hallmark) != score_names or any(
        not isinstance(score, int) or not 4 <= score <= 5
        for score in hallmark.values()
    ):
        raise ValidationError("Hallmark scores must be complete and at least 4/5")
    return tokens


def validate_motion_contract(tokens: dict[str, object], version: str) -> None:
    contract = load_json(ROOT / "design/motion-contract.json")
    if (
        not isinstance(contract, dict)
        or contract.get("schemaVersion") != 1
        or contract.get("themeId") != THEME_ID
        or contract.get("version") != version
    ):
        raise ValidationError("motion contract identity is invalid")
    policy = contract.get("policy")
    performance = contract.get("performance")
    surfaces = contract.get("surfaces")
    transitions = contract.get("transitions")
    reduced = contract.get("reducedMotion")
    if not all(
        isinstance(value, dict)
        for value in (policy, performance, surfaces, transitions, reduced)
    ):
        raise ValidationError("motion contract sections are incomplete")
    if (
        policy.get("idleAnimationAllowed") is not False
        or policy.get("springAllowed") is not False
        or policy.get("overshootAllowed") is not False
        or policy.get("layoutPropertyAnimationAllowed") is not False
        or policy.get("focusIndicatorAnimated") is not False
    ):
        raise ValidationError("motion policy permits a forbidden behavior")
    if (
        performance.get("targetFramesPerSecond") != 60
        or performance.get("maximumTravelPx", 99) > 8
        or performance.get("maximumConcurrentTransitionsPerSurface", 99) > 8
    ):
        raise ValidationError("motion performance limits are invalid")
    state_names = set(tokens["states"]["hierarchy"])
    if not state_names.issubset(transitions):
        raise ValidationError("every semantic state must define animated behavior")
    reduced_outcomes = reduced.get("stateOutcomes")
    if not isinstance(reduced_outcomes, dict) or set(reduced_outcomes) != state_names:
        raise ValidationError("every semantic state must define reduced-motion behavior")
    motion = tokens["motion"]
    duration_names = {
        name
        for name, value in motion.items()
        if name.endswith("Ms") and isinstance(value, int)
    }
    curve_names = set(motion["curves"])
    allowed_properties = {"opacity", "color", "transform"}
    for name, transition in transitions.items():
        if (
            not isinstance(transition, dict)
            or set(transition) != {"duration", "curve", "properties"}
            or transition["duration"] not in duration_names
            or transition["curve"] not in curve_names
            or not isinstance(transition["properties"], list)
            or not set(transition["properties"]).issubset(allowed_properties)
        ):
            raise ValidationError(f"motion transition {name} is invalid")
    if (
        reduced.get("duration") != "instantMs"
        or reduced.get("spatialMotion") is not False
        or reduced.get("opacityTransitions") is not False
        or reduced.get("busyOutcome") != "static-semantic-glyph"
    ):
        raise ValidationError("reduced-motion behavior is incomplete")


def validate_color_scheme(path: Path) -> None:
    parser = load_colors(path)
    missing = COLOR_SECTIONS.difference(parser.sections())
    if missing:
        raise ValidationError(f"{path.name} is missing sections: {sorted(missing)}")
    for section in COLOR_SECTIONS:
        missing_keys = COLOR_KEYS.difference(parser[section])
        if missing_keys:
            raise ValidationError(f"{path.name} [{section}] missing keys: {sorted(missing_keys)}")
        for key in COLOR_KEYS:
            value = parser[section][key]
            try:
                channels = [int(channel) for channel in value.split(",")]
            except ValueError as error:
                raise ValidationError(f"invalid RGB value {value!r} in [{section}] {key}") from error
            if len(channels) != 3 or any(channel < 0 or channel > 255 for channel in channels):
                raise ValidationError(f"invalid RGB value {value!r} in [{section}] {key}")
    if parser["General"].get("colorscheme") != "NoxForgeDark":
        raise ValidationError(f"{path.name} has the wrong ColorScheme identifier")


def validate_metadata(version: str) -> None:
    path = ROOT / f"plasma/desktoptheme/{THEME_ID}/metadata.json"
    metadata = load_json(path)
    if not isinstance(metadata, dict) or not isinstance(metadata.get("KPlugin"), dict):
        raise ValidationError("Plasma Style metadata requires a KPlugin object")
    plugin = metadata["KPlugin"]
    if plugin.get("Id") != THEME_ID or plugin.get("Version") != version:
        raise ValidationError("Plasma Style metadata identity or version mismatch")
    if path.parent.name != plugin.get("Id"):
        raise ValidationError("Plasma Style directory must match KPlugin.Id")
    if metadata.get("X-Plasma-API") != "5.0":
        raise ValidationError("Plasma Style metadata has an unexpected X-Plasma-API")


def validate_repository_urls() -> None:
    json_metadata = (
        ROOT / f"plasma/desktoptheme/{THEME_ID}/metadata.json",
        ROOT / f"look-and-feel/{THEME_ID}/metadata.json",
    )
    for path in json_metadata:
        metadata = load_json(path)
        plugin = metadata.get("KPlugin") if isinstance(metadata, dict) else None
        if not isinstance(plugin, dict) or plugin.get("Website") != REPOSITORY_URL:
            raise ValidationError(f"{path.relative_to(ROOT)} has the wrong repository URL")

    desktop_metadata = (
        (
            ROOT / f"aurorae/{THEME_ID}/metadata.desktop",
            "Desktop Entry",
            "x-kde-plugininfo-website",
        ),
        (ROOT / "sddm/NoxForge/metadata.desktop", "SddmGreeterTheme", "website"),
    )
    for path, section, key in desktop_metadata:
        metadata = load_colors(path)
        if metadata[section].get(key) != REPOSITORY_URL:
            raise ValidationError(f"{path.relative_to(ROOT)} has the wrong repository URL")


def svg_ids(path: Path) -> set[str]:
    try:
        return {element.get("id") for element in ET.parse(path).iter() if element.get("id")}
    except (OSError, ET.ParseError) as error:
        raise ValidationError(f"invalid SVG {path.relative_to(ROOT)}: {error}") from error


def frame_base_paint(element: ET.Element) -> tuple[str | None, str | None]:
    """Return the semantic base paint from a direct shape or grouped frame part."""
    candidates = [element, *element.iter()]
    for candidate in candidates:
        if candidate.tag.endswith(("path", "rect")) and candidate.get("class"):
            return candidate.get("class"), candidate.get("fill-opacity")
    raise ValidationError("Plasma frame part has no semantic base paint")


def validate_plasma_style() -> None:
    theme = ROOT / f"plasma/desktoptheme/{THEME_ID}"
    contract = load_json(ROOT / "design/plasma-semantic-contract.json")
    if not isinstance(contract, dict) or contract.get("schemaVersion") != 4 or contract.get("plasmaVersion") != "6.7":
        raise ValidationError("Plasma semantic contract must target Plasma 6.7 with schema version 4")
    material_policy = contract.get("materialPolicy")
    if not isinstance(material_policy, dict) or material_policy.get("hierarchy") != [
        "canvas", "sunken", "surface", "raised", "overlay"
    ]:
        raise ValidationError("Plasma material hierarchy is incomplete")
    if (
        material_policy.get("edgeHighlightRecipe") != "edgeHighlight"
        or material_policy.get("overlayShadowRecipe") != "overlayShadow"
        or material_policy.get("coloredShadows") is not False
        or material_policy.get("runtimeSvgFilters") is not False
        or material_policy.get("blurRequiredForReadability") is not False
    ):
        raise ValidationError("Plasma material safety and depth policy is incomplete")
    widget_families = contract.get("widgetFamilies")
    weather_families = contract.get("weatherFamilies")
    if not isinstance(widget_families, list) or len(widget_families) != 43:
        raise ValidationError("Plasma semantic contract must declare all 43 widget families")
    if not isinstance(weather_families, list) or weather_families != ["wind-arrows"]:
        raise ValidationError("Plasma weather artwork contract is incomplete")
    recipes = contract.get("semanticRecipes")
    family_recipes = contract.get("familyRecipes")
    if not isinstance(recipes, dict) or not isinstance(family_recipes, dict):
        raise ValidationError("Plasma semantic recipe maps are missing")
    if set(family_recipes) != set(widget_families):
        raise ValidationError("Plasma semantic recipes must cover exactly all 43 widget families")
    invalid_recipes = sorted(
        family for family, recipe_name in family_recipes.items() if recipe_name not in recipes
    )
    if invalid_recipes:
        raise ValidationError(f"Plasma families reference unknown semantic recipes: {invalid_recipes}")
    qualified_surfaces = contract.get("qualifiedSurfaces")
    required_surfaces = {
        "panels",
        "popups",
        "notifications",
        "tooltips",
        "calendarWeather",
        "inputs",
        "osdContainment",
    }
    if not isinstance(qualified_surfaces, dict) or set(qualified_surfaces) != required_surfaces:
        raise ValidationError("Plasma shell surface qualification map is incomplete")
    missing_families = [name for name in widget_families if not (theme / f"widgets/{name}.svg").is_file()]
    missing_weather = [name for name in weather_families if not (theme / f"weather/{name}.svg").is_file()]
    if missing_families or missing_weather:
        raise ValidationError(f"Plasma asset families are incomplete: {missing_families + missing_weather}")
    for surface, paths in qualified_surfaces.items():
        if not isinstance(paths, list) or not paths or any(not (theme / relative).is_file() for relative in paths):
            raise ValidationError(f"Plasma shell surface qualification is incomplete: {surface}")
    backgrounds = {
        "dialogs/background.svg",
        "widgets/panel-background.svg",
        "widgets/background.svg",
        "widgets/tooltip.svg",
    }
    for relative in backgrounds:
        found = svg_ids(theme / relative)
        required = POSITIONS | {f"mask-{position}" for position in POSITIONS}
        if not required.issubset(found):
            raise ValidationError(f"{relative} has an incomplete background or blur mask frame")
    background_variants = contract.get("backgroundVariants")
    if not isinstance(background_variants, list) or len(background_variants) != 11:
        raise ValidationError("Plasma Style requires all opaque, solid and translucent background variants")
    variant_recipes = contract.get("backgroundVariantRecipes")
    if not isinstance(variant_recipes, dict) or set(variant_recipes) != set(background_variants):
        raise ValidationError("Plasma background variants lack material recipes")
    if {value.get("blur") for value in variant_recipes.values()} != {"on", "off"}:
        raise ValidationError("Plasma background recipes must separate blur-on and blur-off variants")
    for relative in background_variants:
        path = theme / relative
        found = svg_ids(path)
        if not POSITIONS.issubset(found):
            raise ValidationError(f"{relative} has an incomplete seam-free background frame")
        elements = {element.get("id"): element for element in ET.parse(path).iter() if element.get("id") in POSITIONS}
        paints = {frame_base_paint(element) for element in elements.values()}
        if len(elements) != len(POSITIONS) or len(paints) != 1:
            raise ValidationError(f"{relative} uses inconsistent frame paints that can create dark seams")
        variant = variant_recipes[relative]
        if set(variant) != {"recipe", "opacity", "edgeHighlight", "overlayShadow", "blur"}:
            raise ValidationError(f"{relative} has an incomplete material recipe")
        text = path.read_text(encoding="utf-8")
        if variant["edgeHighlight"] and "NoxForge-EdgeHighlight" not in text:
            raise ValidationError(f"{relative} lacks its neutral edge highlight")
        if variant["overlayShadow"] and "NoxForge-OverlayShadow" not in text:
            raise ValidationError(f"{relative} lacks its controlled overlay shadow")
    for relative, states in PLASMA_STATES.items():
        found = svg_ids(theme / relative)
        for state in states:
            if not {f"{state}-{position}" for position in POSITIONS}.issubset(found):
                raise ValidationError(f"{relative} has an incomplete {state} frame")
    tasks = svg_ids(theme / "widgets/tasks.svg")
    for orientation in ("north", "south", "east", "west"):
        for state in PLASMA_STATES["widgets/tasks.svg"]:
            prefix = f"{orientation}-{state}"
            if not {f"{prefix}-{position}" for position in POSITIONS}.issubset(tasks):
                raise ValidationError(f"tasks.svg lacks the complete {prefix} edge state")
    required_hints = contract.get("requiredHints")
    if not isinstance(required_hints, dict):
        raise ValidationError("Plasma semantic contract lacks required hints")
    for family, hints in required_hints.items():
        found = svg_ids(theme / f"widgets/{family}.svg")
        if not set(hints).issubset(found):
            raise ValidationError(f"widgets/{family}.svg lacks required hints: {sorted(set(hints) - found)}")
    required_shell_assets = {
        "widgets/calendar.svg", "widgets/clock.svg", "widgets/busywidget.svg",
        "widgets/configuration-icons.svg", "widgets/containment-controls.svg",
        "widgets/pager.svg", "widgets/media-delegate.svg", "widgets/action-overlays.svg",
        "widgets/analog_meter.svg", "widgets/bar_meter_horizontal.svg",
        "widgets/bar_meter_vertical.svg", "widgets/notes.svg", "widgets/timer.svg",
        "solid/widgets/background.svg", "translucent/widgets/background.svg",
        "opaque/widgets/panel-background.svg",
    }
    missing_assets = sorted(relative for relative in required_shell_assets if not (theme / relative).is_file())
    if missing_assets:
        raise ValidationError(f"Plasma shell asset coverage is incomplete: {missing_assets}")
    if len(list(theme.rglob("*.svg"))) < 56:
        raise ValidationError("Plasma Style requires the complete generated SVG asset set")
    for path in sorted(theme.rglob("*.svg")):
        text = path.read_text(encoding="utf-8")
        if 'id="current-color-scheme"' not in text or "ColorScheme-Highlight" not in text:
            raise ValidationError(f"{path.relative_to(ROOT)} does not use Plasma color classes")
        if "filter=" in text:
            raise ValidationError(f"{path.relative_to(ROOT)} uses unsupported runtime SVG filters")
    capture_matrix = contract.get("sourceCaptureMatrix")
    if not isinstance(capture_matrix, dict) or capture_matrix != {
        "scales": [1.0, 1.25, 1.4, 2.0],
        "panelEdges": ["top", "bottom", "left", "right"],
        "layouts": ["standard", "compact"],
        "virtualOutputs": ["primary", "secondary"],
        "blur": ["on", "off"],
        "evidenceClass": "deterministic-static-svg-source",
        "qualifiesLivePlasma": False,
    }:
        raise ValidationError("Plasma static source capture matrix is incomplete or claims live evidence")
    plasmarc = (theme / "plasmarc").read_text(encoding="utf-8")
    if "FallbackTheme" in plasmarc:
        raise ValidationError("complete Plasma Style must not declare a fallback theme")
    if list(theme.rglob("metadata.desktop")):
        raise ValidationError("Plasma Style must not use Plasma 5 metadata.desktop")


def validate_look_and_feel(version: str) -> None:
    package = ROOT / f"look-and-feel/{THEME_ID}"
    for name in ("metadata.json", "manifest.json"):
        data = load_json(package / name)
        if not isinstance(data, dict) or data.get("KPackageStructure") != "Plasma/LookAndFeel":
            raise ValidationError(f"{name} must declare Plasma/LookAndFeel")
        plugin = data.get("KPlugin")
        if not isinstance(plugin, dict) or plugin.get("Id") != THEME_ID or plugin.get("Version") != version:
            raise ValidationError(f"{name} identity or version mismatch")
    required = (
        "contents/defaults",
        "contents/layouts/org.kde.plasma.desktop-layout.js",
        "contents/splash/Splash.qml",
        "contents/logout/Logout.qml",
        "contents/previews/preview.png",
    )
    missing = [relative for relative in required if not (package / relative).is_file()]
    if missing:
        raise ValidationError(f"Look-and-Feel package is incomplete: {missing}")
    defaults = (package / "contents/defaults").read_text(encoding="utf-8")
    expected = ("widgetStyle=NoxForge", "ColorScheme=NoxForgeDark", "Theme=NoxForge", f"name={THEME_ID}")
    if any(value not in defaults for value in expected):
        raise ValidationError("Look-and-Feel defaults do not select all NoxForge components")
    if re.search(r"breeze|default", defaults, re.IGNORECASE):
        raise ValidationError("Look-and-Feel defaults must not reference Breeze or default themes")
    validate_qml_design_consumers()


def validate_qml_design_consumers() -> None:
    qml_files = (
        ROOT / f"look-and-feel/{THEME_ID}/contents/splash/Splash.qml",
        ROOT / f"look-and-feel/{THEME_ID}/contents/logout/Logout.qml",
        ROOT / f"kwin/tabbox/{THEME_ID}/contents/ui/Switcher.qml",
        ROOT / "sddm/NoxForge/Main.qml",
    )
    raw_color = re.compile(r"#[0-9A-Fa-f]{6,8}")
    for path in qml_files:
        text = path.read_text(encoding="utf-8")
        if "Tokens {" not in text:
            raise ValidationError(f"{path.relative_to(ROOT)} does not consume generated tokens")
        if raw_color.search(text):
            raise ValidationError(f"{path.relative_to(ROOT)} contains a hard-coded palette color")
    token_copies = [path.parent / "Tokens.qml" for path in qml_files]
    if len({path.read_bytes() for path in token_copies}) != 1:
        raise ValidationError("physical QML token copies differ")
    marks = (
        ROOT / "design/brand/noxforge-mark.svg",
        ROOT / f"look-and-feel/{THEME_ID}/contents/splash/NoxForgeMark.svg",
        ROOT / f"look-and-feel/{THEME_ID}/contents/logout/NoxForgeMark.svg",
        ROOT / f"kwin/tabbox/{THEME_ID}/contents/ui/NoxForgeMark.svg",
        ROOT / "sddm/NoxForge/NoxForgeMark.svg",
    )
    if len({path.read_bytes() for path in marks}) != 1:
        raise ValidationError("physical canonical N/F mark copies differ")
    lockups = (
        ROOT / "design/brand/noxforge-lockup.svg",
        ROOT / f"look-and-feel/{THEME_ID}/contents/splash/NoxForgeLockup.svg",
        ROOT / "sddm/NoxForge/NoxForgeLockup.svg",
    )
    if len({path.read_bytes() for path in lockups}) != 1:
        raise ValidationError("physical canonical NoxForge lockup copies differ")


def validate_tabbox(version: str) -> None:
    package = ROOT / f"kwin/tabbox/{THEME_ID}"
    metadata = load_json(package / "metadata.json")
    if not isinstance(metadata, dict) or metadata.get("KPackageStructure") != "KWin/WindowSwitcher":
        raise ValidationError("task switcher has the wrong KPackage structure")
    plugin = metadata.get("KPlugin")
    if not isinstance(plugin, dict) or plugin.get("Id") != THEME_ID or plugin.get("Version") != version:
        raise ValidationError("task switcher identity or version mismatch")
    if not (package / "contents/ui/main.qml").is_file():
        raise ValidationError("task switcher main QML is missing")


def validate_aurorae(version: str) -> None:
    theme = ROOT / f"aurorae/{THEME_ID}"
    metadata = load_colors(theme / "metadata.desktop")
    entry = metadata["Desktop Entry"]
    if entry.get("x-kde-plugininfo-name") != THEME_ID:
        raise ValidationError("Aurorae plugin ID does not match its directory")
    if entry.get("x-kde-plugininfo-version") != version:
        raise ValidationError("Aurorae version does not match VERSION")
    rc = theme / f"{THEME_ID}rc"
    settings = load_colors(rc)
    if settings["General"].get("rightbuttons") != "IAX":
        raise ValidationError("Aurorae must configure minimize, maximize/restore, and close buttons")
    decoration_ids = svg_ids(theme / "decoration.svg")
    for prefix in ("decoration", "decoration-inactive"):
        if not {f"{prefix}-{position}" for position in POSITIONS}.issubset(decoration_ids):
            raise ValidationError(f"Aurorae has an incomplete {prefix} frame")
    states = {
        "active",
        "inactive",
        "hover",
        "hover-inactive",
        "pressed",
        "pressed-inactive",
        "deactivated",
        "deactivated-inactive",
    }
    for name in ("menu", "close", "minimize", "maximize", "restore"):
        svg_path = theme / f"{name}.svg"
        if not {f"{state}-center" for state in states}.issubset(svg_ids(svg_path)):
            raise ValidationError(f"Aurorae {name}.svg has incomplete button states")
    for svg_path in sorted(theme.glob("*.svg")):
        svgz_path = svg_path.with_suffix(".svgz")
        try:
            compressed = gzip.decompress(svgz_path.read_bytes())
        except (OSError, gzip.BadGzipFile) as error:
            raise ValidationError(f"invalid compressed Aurorae asset {svgz_path.name}: {error}") from error
        if compressed != svg_path.read_bytes():
            raise ValidationError(f"compressed Aurorae asset differs from {svg_path.name}")


def validate_icons() -> None:
    theme = ROOT / "icons/NoxForge"
    artwork = load_json(ROOT / "design/artwork-contract.json")
    if not isinstance(artwork, dict):
        raise ValidationError("artwork contract is invalid")
    fixture = artwork.get("runtimeIconFixture")
    if not isinstance(fixture, dict):
        raise ValidationError("runtime icon fixture is missing")
    index = load_colors(theme / "index.theme")
    inherited = index["Icon Theme"].get("inherits", "").split(",")
    if inherited != ["breeze-dark", "breeze", "hicolor"]:
        raise ValidationError("icon theme must use the verified Fedora KDE overlay fallback chain")
    valid_contexts = {
        "Actions", "Animations", "Applications", "Categories", "Devices", "Emblems",
        "Emotes", "International", "MimeTypes", "Places", "Status",
    }
    for directory in index["Icon Theme"].get("directories", "").split(","):
        if index[directory].get("context") not in valid_contexts:
            raise ValidationError(f"icon directory {directory} has an invalid Context")
    expected_categories = {"actions", "applets", "categories", "devices", "emblems", "mimetypes", "places", "preferences", "status"}
    icons = list((theme / "scalable").glob("*/*.svg"))
    if len(icons) < 120:
        raise ValidationError(f"system icon coverage requires at least 120 SVGs, found {len(icons)}")
    if {path.parent.name for path in icons} != expected_categories:
        raise ValidationError("system icon categories are incomplete")
    coverage = load_json(theme / "coverage.json")
    if not isinstance(coverage, dict) or coverage.get("schemaVersion") != 3 or coverage.get("iconCount") != len(icons):
        raise ValidationError("icon coverage manifest does not match generated files")
    if coverage.get("opticalSizes") != [16, 22] or not isinstance(coverage.get("aliases"), dict):
        raise ValidationError("icon optical-size or alias coverage is incomplete")
    edge_polish = load_json(ROOT / "design/edge-polish-contract.json")
    if not isinstance(edge_polish, dict) or edge_polish.get("schemaVersion") != 1:
        raise ValidationError("edge-polish contract is invalid")
    priority = coverage.get("phase6Priority")
    review_sizes = coverage.get("phase6ReviewSizes")
    if priority != edge_polish.get("icons", {}).get("priority") or review_sizes != [16, 22, 24, 32, 48]:
        raise ValidationError("icon priority ranking or review sizes drifted")
    duplicate_allowlist = coverage.get("duplicateAllowlist")
    if not isinstance(duplicate_allowlist, list):
        raise ValidationError("icon duplicate allowlist is missing")
    optical_count = 0
    for size in (16, 22):
        optical = list((theme / f"{size}x{size}").glob("*/*.svg"))
        if any(path.is_symlink() for path in optical):
            raise ValidationError("small optical icons must be physical files")
        optical_count += len(optical)
    if optical_count != coverage.get("opticalCount"):
        raise ValidationError("icon optical manifest does not match generated files")
    required_fixture = sorted(fixture.get("required", []))
    if not required_fixture or coverage.get("runtimeFixture") != required_fixture:
        raise ValidationError("icon coverage does not bind the fixed runtime fixture")
    generated = {path.relative_to(theme / "scalable").as_posix() for path in icons}
    if not set(required_fixture).issubset(generated):
        raise ValidationError("fixed KDE/Plasma/System Settings runtime fixture is incomplete")
    distinct_pairs = (
        ("actions/go-next.svg", "actions/go-previous.svg"),
        ("actions/media-playback-start.svg", "actions/media-playback-pause.svg"),
        ("actions/media-playback-pause.svg", "actions/media-playback-stop.svg"),
        ("status/audio-volume-high.svg", "status/audio-volume-muted.svg"),
        ("status/battery-good.svg", "status/battery-charging.svg"),
        ("status/network-wireless.svg", "status/network-wireless-disconnected.svg"),
    )
    for first, second in distinct_pairs:
        if (theme / "scalable" / first).read_bytes() == (theme / "scalable" / second).read_bytes():
            raise ValidationError(f"semantic icon states must differ: {first}, {second}")
    groups: dict[bytes, list[str]] = {}
    for path in icons:
        digest = hashlib.sha256(path.read_bytes()).digest()
        groups.setdefault(digest, []).append(path.relative_to(theme / "scalable").as_posix())
    actual_duplicates = sorted(sorted(group) for group in groups.values() if len(group) > 1)
    if actual_duplicates != sorted(duplicate_allowlist):
        raise ValidationError("icon duplicates differ from the explicit semantic allowlist")
    for path in icons:
        root = ET.parse(path).getroot()
        if root.get("viewBox") != "0 0 24 24":
            raise ValidationError(f"icon {path.name} must use the 24px design grid")
        forbidden = [element for element in root.iter() if element.tag.rsplit("}", 1)[-1] in {"image", "text"}]
        if forbidden:
            raise ValidationError(f"icon {path.name} embeds raster data or text")


def validate_cursors() -> None:
    theme = ROOT / "cursors/NoxForge-Cursors"
    index = load_colors(theme / "index.theme")
    if index["Icon Theme"].get("name") != "NoxForge":
        raise ValidationError("cursor theme display name must be NoxForge")
    cursors = sorted((theme / "cursors").iterdir())
    if len(cursors) < 90 or any(not path.is_file() or path.is_symlink() for path in cursors):
        raise ValidationError("cursor theme requires at least 90 physical cursor files")
    expected_sizes = {24, 32, 48}
    cursor_counts: dict[str, int] = {}
    for path in cursors:
        data = path.read_bytes()
        if len(data) < 52:
            raise ValidationError(f"cursor {path.name} is truncated")
        magic, header, version, count = struct.unpack("<4I", data[:16])
        if magic != 0x72756358 or header != 16 or version != 0x00010000:
            raise ValidationError(f"cursor {path.name} has an invalid Xcursor header")
        sizes = {struct.unpack("<3I", data[16 + offset * 12 : 28 + offset * 12])[1] for offset in range(count)}
        if sizes != expected_sizes:
            raise ValidationError(f"cursor {path.name} lacks required sizes")
        cursor_counts[path.name] = count
    coverage = load_json(theme / "coverage.json")
    if not isinstance(coverage, dict) or coverage.get("schemaVersion") != 3 or coverage.get("sizes") != [24, 32, 48]:
        raise ValidationError("cursor coverage manifest is invalid")
    hotspots = coverage.get("hotspots")
    if not isinstance(hotspots, dict):
        raise ValidationError("cursor hotspot manifest is missing")
    animations = coverage.get("animations")
    if not isinstance(animations, dict):
        raise ValidationError("cursor animation manifest is missing")
    for name in ("wait", "progress"):
        if cursor_counts.get(name) != 36 or animations.get(name) != {"delayMs": 80, "frames": 12}:
            raise ValidationError(f"cursor {name} must contain 12 frames at each size")
        data = (theme / "cursors" / name).read_bytes()
        _, _, _, count = struct.unpack("<4I", data[:16])
        for offset in range(count):
            position = struct.unpack("<3I", data[16 + offset * 12 : 28 + offset * 12])[2]
            if struct.unpack("<9I", data[position : position + 36])[8] != 80:
                raise ValidationError(f"cursor {name} contains a frame with the wrong delay")
    canonical = coverage.get("canonical")
    if not isinstance(canonical, list):
        raise ValidationError("cursor canonical manifest is invalid")
    source_files = [theme / "source" / f"{name}.svg" for name in canonical]
    if any(not path.is_file() for path in source_files):
        raise ValidationError("editable cursor SVG sources are incomplete")
    if len({hashlib.sha256(path.read_bytes()).digest() for path in source_files}) != len(source_files):
        raise ValidationError("editable cursor sources must represent distinct canonical glyphs")
    for name in canonical:
        data = (theme / "cursors" / name).read_bytes()
        _, _, _, count = struct.unpack("<4I", data[:16])
        declared = hotspots.get(name)
        if not isinstance(declared, dict):
            raise ValidationError(f"cursor {name} has no declared hotspots")
        observed: dict[str, list[int]] = {}
        for offset in range(count):
            position = struct.unpack("<3I", data[16 + offset * 12 : 28 + offset * 12])[2]
            _, _, size, _, _, _, xhot, yhot, _ = struct.unpack("<9I", data[position : position + 36])
            observed[str(size)] = [xhot, yhot]
            if xhot >= size or yhot >= size:
                raise ValidationError(f"cursor {name} hotspot lies outside its physical image")
        if observed != declared:
            raise ValidationError(f"cursor {name} hotspots differ from the coverage manifest")


def validate_sounds() -> None:
    theme = ROOT / "sounds/NoxForge"
    index = load_colors(theme / "index.theme")
    if index["Sound Theme"].get("name") != "NoxForge" or index["Sound Theme"].get("directories") != "stereo":
        raise ValidationError("sound theme index is invalid")
    sounds = sorted((theme / "stereo").glob("*.oga"))
    coverage = load_json(theme / "coverage.json")
    if (
        not isinstance(coverage, dict)
        or coverage.get("schemaVersion") != 2
        or not isinstance(coverage.get("events"), dict)
        or not isinstance(coverage.get("sources"), dict)
    ):
        raise ValidationError("sound coverage manifest is invalid")
    if len(sounds) != len(coverage["events"]) or len(sounds) < 30:
        raise ValidationError("sound event coverage does not match encoded files")
    for path in sounds:
        if path.read_bytes()[:4] != b"OggS":
            raise ValidationError(f"sound {path.name} is not an Ogg stream")
    sources = sorted((theme / "source").glob("*.wav"))
    if len(sources) < 10 or any(path.read_bytes()[:4] != b"RIFF" for path in sources):
        raise ValidationError("editable WAV sound sources are incomplete")
    normalization = coverage.get("normalization")
    if not isinstance(normalization, dict):
        raise ValidationError("sound loudness normalization contract is missing")
    tolerance = normalization.get("toleranceDb")
    if not isinstance(tolerance, (int, float)):
        raise ValidationError("sound loudness tolerance is invalid")
    measured_signatures: set[tuple[int, tuple[float, ...]]] = set()
    for path in sources:
        name = path.stem
        details = coverage["sources"].get(name)
        if not isinstance(details, dict):
            raise ValidationError(f"sound source metrics are missing: {name}")
        target = (
            normalization["alarmTargetRmsDbfs"]
            if name == "alarm"
            else normalization["targetRmsDbfs"]
        )
        if abs(details.get("rmsDbfs", 999) - target) > tolerance:
            raise ValidationError(f"sound {name} is outside its RMS loudness target")
        if details.get("peakDbfs", 999) > normalization["peakCeilingDbfs"] + 0.01:
            raise ValidationError(f"sound {name} exceeds its peak ceiling")
        with wave.open(str(path), "rb") as handle:
            frames = handle.readframes(handle.getnframes())
            if handle.getframerate() != coverage["sampleRate"] or handle.getnchannels() != 1:
                raise ValidationError(f"sound {name} source format is invalid")
        samples = struct.unpack(f"<{len(frames) // 2}h", frames)
        rms = math.sqrt(sum(sample * sample for sample in samples) / len(samples)) / 32767
        measured_dbfs = 20 * math.log10(rms)
        if abs(measured_dbfs - details["rmsDbfs"]) > 0.01:
            raise ValidationError(f"sound {name} measured loudness differs from its manifest")
        signature = (details.get("durationMs"), tuple(details.get("frequenciesHz", [])))
        if signature in measured_signatures:
            raise ValidationError(f"sound {name} loses semantic distinction in duration and pitch")
        measured_signatures.add(signature)


def validate_sddm(version: str) -> None:
    theme = ROOT / "sddm/NoxForge"
    metadata = load_colors(theme / "metadata.desktop")
    entry = metadata["SddmGreeterTheme"]
    if entry.get("theme-id") != "NoxForge" or entry.get("version") != version or entry.get("qtversion") != "6":
        raise ValidationError("SDDM metadata identity, version, or Qt contract is invalid")
    qml = (theme / "Main.qml").read_text(encoding="utf-8")
    for required in ("userModel", "sessionModel", "keyboard.layouts", "sddm.login", "onLoginFailed", 'qsTr("Username")', 'qsTr("Password")', "Accessible.name"):
        if required not in qml:
            raise ValidationError(f"SDDM theme lacks required flow: {required}")
    if re.search(r"breeze|plasma5", qml, re.IGNORECASE):
        raise ValidationError("SDDM theme must not import Breeze or Plasma 5 components")
    if png_dimensions(theme / "background.png") != (2560, 1440):
        raise ValidationError("SDDM background must be 2560x1440")
    if png_dimensions(theme / "preview.png") != (960, 540):
        raise ValidationError("SDDM preview must be 960x540")


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValidationError(f"invalid PNG header: {path.relative_to(ROOT)}")
    return struct.unpack(">II", data[16:24])


def validate_wallpaper(version: str) -> None:
    package = ROOT / "wallpapers/NoxForge"
    contract = load_json(ROOT / "design/artwork-contract.json")
    if not isinstance(contract, dict) or contract.get("schemaVersion") != 2:
        raise ValidationError("artwork contract must use schema version 2")
    metadata = load_json(package / "metadata.json")
    if not isinstance(metadata, dict) or not isinstance(metadata.get("KPlugin"), dict):
        raise ValidationError("wallpaper metadata requires a KPlugin object")
    plugin = metadata["KPlugin"]
    if plugin.get("Id") != "NoxForge" or plugin.get("Version") != version or plugin.get("License") != "MIT":
        raise ValidationError("wallpaper metadata identity, version, or license mismatch")
    compositions = contract.get("wallpapers")
    if not isinstance(compositions, dict) or set(compositions) != {"16:9", "ultrawide"}:
        raise ValidationError("wallpaper contract requires separate 16:9 and ultrawide compositions")
    sources = [ROOT / details["source"] for details in compositions.values()]
    if len({path.read_bytes() for path in sources}) != 2:
        raise ValidationError("16:9 and ultrawide wallpaper sources must be independent compositions")
    expected_viewboxes = {"16:9": "0 0 2560 1440", "ultrawide": "0 0 3440 1440"}
    for name, details in compositions.items():
        source = ET.parse(ROOT / details["source"]).getroot()
        if source.get("viewBox") != expected_viewboxes[name]:
            raise ValidationError(f"editable {name} wallpaper source has the wrong viewBox")
        if details.get("original") is not True or details.get("editable") is not True:
            raise ValidationError(f"{name} wallpaper lacks original/editable provenance")
        quiet = details.get("quietWorkspace")
        width, height = map(int, expected_viewboxes[name].split()[2:])
        if (
            not isinstance(quiet, dict)
            or set(quiet) != {"x", "y", "width", "height"}
            or quiet["x"] < 1000
            or quiet["width"] < 1200
            or quiet["x"] + quiet["width"] > width
            or quiet["y"] + quiet["height"] > height
        ):
            raise ValidationError(f"{name} wallpaper quiet workspace is invalid")
        for output in details.get("outputs", []):
            output_width, output_height = map(int, output.split("x"))
            path = package / f"contents/images/{output}.png"
            if png_dimensions(path) != (output_width, output_height):
                raise ValidationError(f"wallpaper output must be exactly {output}")
    brand = contract.get("brand")
    if (
        not isinstance(brand, dict)
        or brand.get("opticalSizes") != [16, 24, 48, 128, 512]
        or brand.get("viewBox") != "0 0 192 144"
        or brand.get("lockupViewBox") != "0 0 600 144"
        or brand.get("original") is not True
        or brand.get("editable") is not True
    ):
        raise ValidationError("Kinetic Precision brand contract is invalid")
    semantic = ET.parse(ROOT / brand["source"]).getroot()
    monochrome = ET.parse(ROOT / brand["monochromeSource"]).getroot()
    lockup = ET.parse(ROOT / brand["lockupSource"]).getroot()
    namespace = "{http://www.w3.org/2000/svg}"
    if (
        semantic.get("viewBox") != brand["viewBox"]
        or monochrome.get("viewBox") != brand["viewBox"]
        or lockup.get("viewBox") != brand["lockupViewBox"]
        or semantic.find(f".//{namespace}path").get("d")
        != monochrome.find(f".//{namespace}path").get("d")
        or lockup.findall(f".//{namespace}text")
    ):
        raise ValidationError("Kinetic Precision brand masters are inconsistent")
    for kind, paths in brand.get("physicalCopies", {}).items():
        source_path = ROOT / (
            brand["source"] if kind == "mark" else brand["lockupSource"]
        )
        if any((ROOT / path).read_bytes() != source_path.read_bytes() for path in paths):
            raise ValidationError(f"physical {kind} copies differ from their master")
    derived = contract.get("derivedArtwork")
    expected_derived = {
        "sessionBackground": "sddm/NoxForge/background.png",
        "sddmPreview": "sddm/NoxForge/preview.png",
        "globalThemeTile": f"look-and-feel/{THEME_ID}/contents/previews/preview.png",
        "globalThemePreview": (
            f"look-and-feel/{THEME_ID}/contents/previews/fullscreenpreview.png"
        ),
        "readmeHero": "wallpapers/NoxForge/contents/images/2560x1440.png",
    }
    if derived != expected_derived or any(
        not (ROOT / relative).is_file() for relative in expected_derived.values()
    ):
        raise ValidationError("Kinetic Precision derived artwork contract is invalid")


def validate_artwork_evidence(version: str) -> None:
    manifest_path = ROOT / "docs/evidence/artwork-contact-sheets.json"
    manifest = load_json(manifest_path)
    if (
        not isinstance(manifest, dict)
        or manifest.get("schemaVersion") != 2
        or manifest.get("release") != version
        or manifest.get("phase") != 2
        or manifest.get("reviewStatus") != "reviewed-offscreen"
        or manifest.get("liveEvidence") is not False
        or manifest.get("originalEditable") is not True
    ):
        raise ValidationError("Phase 2 artwork contact-sheet manifest is invalid")
    assertions = manifest.get("reviewAssertions")
    if not isinstance(assertions, list) or len(assertions) < 4:
        raise ValidationError("Phase 2 artwork review assertions are incomplete")
    for section in ("sources", "sheets"):
        entries = manifest.get(section)
        if not isinstance(entries, dict) or not entries:
            raise ValidationError(f"Phase 2 artwork {section} hashes are missing")
        for relative, expected in entries.items():
            path = ROOT / relative
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise ValidationError(f"Phase 2 artwork evidence hash mismatch: {relative}")
    if len(manifest["sheets"]) != 4:
        raise ValidationError("Phase 2 requires four reviewed contact sheets")
    optical = manifest.get("brandOpticalRenders")
    if (
        not isinstance(optical, dict)
        or set(optical) != {"16", "24", "48", "128", "512"}
        or any(
            details.get("width") != int(size)
            or details.get("height") != round(int(size) * 0.75)
            or not re.fullmatch(r"[0-9a-f]{64}", details.get("sha256", ""))
            for size, details in optical.items()
        )
    ):
        raise ValidationError("Phase 2 optical-size render evidence is incomplete")
    for relative in manifest["sheets"]:
        width, height = png_dimensions(ROOT / relative)
        minimum_height = 120 if relative.endswith("artwork-brand-optical-sizes.png") else 200
        if width < 400 or height < minimum_height:
            raise ValidationError(f"Phase 2 artwork contact sheet is too small: {relative}")


def validate_v6_brand_previews(version: str) -> None:
    manifest = load_json(ROOT / "docs/evidence/v6/brand/preview-manifest.json")
    if (
        not isinstance(manifest, dict)
        or manifest.get("schemaVersion") != 1
        or manifest.get("release") != version
        or manifest.get("phase") != 2
        or manifest.get("kind") != "authentic-offscreen-preview"
        or manifest.get("liveEvidence") is not False
    ):
        raise ValidationError("v6 brand preview identity is invalid")
    sources = manifest.get("sources")
    outputs = manifest.get("outputs")
    if not isinstance(sources, dict) or not isinstance(outputs, dict):
        raise ValidationError("v6 brand preview lineage is incomplete")
    for relative, expected in sources.items():
        path = ROOT / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValidationError(f"v6 brand preview source drift: {relative}")
    expected_outputs = {
        "globalTheme": (
            f"look-and-feel/{THEME_ID}/contents/previews/preview.png",
            (480, 380),
        ),
        "sddm": ("sddm/NoxForge/preview.png", (960, 540)),
    }
    if set(outputs) != set(expected_outputs):
        raise ValidationError("v6 brand preview outputs are incomplete")
    for name, (relative, expected_size) in expected_outputs.items():
        details = outputs[name]
        path = ROOT / relative
        if (
            not isinstance(details, dict)
            or details.get("path") != relative
            or details.get("sha256") != hashlib.sha256(path.read_bytes()).hexdigest()
            or png_dimensions(path) != expected_size
        ):
            raise ValidationError(f"v6 brand preview is invalid: {name}")


def validate_v6_north_star(version: str) -> None:
    root = ROOT / "docs/evidence/v6/north-star"
    manifest = load_json(root / "manifest.json")
    if (
        not isinstance(manifest, dict)
        or manifest.get("schemaVersion") != 1
        or manifest.get("release") != version
        or manifest.get("phase") != 1
        or manifest.get("kind") != "rendered-north-star-prototype"
        or manifest.get("prototype") is not True
        or manifest.get("productionRuntime") is not False
        or manifest.get("liveEvidence") is not False
    ):
        raise ValidationError("v6 north-star evidence identity is invalid")
    comparisons = manifest.get("comparisons")
    expected_files = {
        "north-star-qt.png",
        "north-star-plasma.png",
        "north-star-session.png",
        "north-star-tabbox.png",
        "north-star-brand-wallpaper.png",
        "north-star-motion-storyboard.png",
    }
    if (
        not isinstance(comparisons, list)
        or {entry.get("file") for entry in comparisons if isinstance(entry, dict)}
        != expected_files
    ):
        raise ValidationError("v6 north-star comparison matrix is incomplete")
    for entry in comparisons:
        path = root / entry["file"]
        baseline = (root / entry["baseline"]).resolve()
        if (
            not path.is_file()
            or not baseline.is_file()
            or entry.get("status") != "passed"
            or entry.get("sha256") != hashlib.sha256(path.read_bytes()).hexdigest()
            or entry.get("baselineSha256")
            != hashlib.sha256(baseline.read_bytes()).hexdigest()
            or png_dimensions(path) != png_dimensions(baseline)
            or entry.get("rootMeanSquareDifference", 0) <= 0
        ):
            raise ValidationError(f"v6 north-star comparison is invalid: {entry['file']}")
    sources = manifest.get("sources")
    if not isinstance(sources, dict) or sources != {
        "tokensSha256": hashlib.sha256((ROOT / "design/tokens.json").read_bytes()).hexdigest(),
        "motionContractSha256": hashlib.sha256(
            (ROOT / "design/motion-contract.json").read_bytes()
        ).hexdigest(),
        "rendererSha256": hashlib.sha256(
            (ROOT / "tools/north_star_renderer.cpp").read_bytes()
        ).hexdigest(),
    }:
        raise ValidationError("v6 north-star source lineage is stale")
    scorecard = manifest.get("scorecard")
    scores = scorecard.get("scores") if isinstance(scorecard, dict) else None
    if (
        not isinstance(scores, dict)
        or scorecard.get("status") != "passed"
        or any(not isinstance(score, int) or score < 4 for score in scores.values())
    ):
        raise ValidationError("v6 north-star scorecard does not meet the phase-one floor")
    public_scorecard = load_json(ROOT / "docs/evidence/v6/visual-scorecard.json")
    categories = (
        public_scorecard.get("categories") if isinstance(public_scorecard, dict) else None
    )
    if (
        not isinstance(categories, dict)
        or set(categories) != set(scores)
        or any(
            category.get("v6Score") != scores[name]
            or category.get("status") != "reviewed-prototype"
            or category.get("evidence") != "north-star/manifest.json"
            for name, category in categories.items()
        )
    ):
        raise ValidationError("v6 visual scorecard is not linked to north-star evidence")


def validate_v6_motion_evidence(version: str) -> None:
    root = ROOT / "docs/evidence/v6/qt-motion"
    manifest = load_json(root / "manifest.json")
    if (
        not isinstance(manifest, dict)
        or manifest.get("schemaVersion") != 1
        or manifest.get("version") != version
        or manifest.get("phase") != 3
        or manifest.get("kind") != "authentic-offscreen-native-qt-motion"
        or manifest.get("liveEvidence") is not False
        or manifest.get("deterministicProgress") != [0, 50, 100]
    ):
        raise ValidationError("v6 native Qt motion evidence identity is invalid")
    renders = manifest.get("renders")
    if (
        not isinstance(renders, list)
        or [render.get("progressPercent") for render in renders] != [0, 50, 100]
    ):
        raise ValidationError("v6 native Qt motion evidence is incomplete")
    hashes = set()
    for render in renders:
        path = ROOT / render.get("path", "")
        if (
            not path.is_file()
            or render.get("width") != 960
            or render.get("height") != 540
            or render.get("sha256") != hashlib.sha256(path.read_bytes()).hexdigest()
        ):
            raise ValidationError("v6 native Qt motion render drift")
        hashes.add(render["sha256"])
    if len(hashes) != 3:
        raise ValidationError("v6 native Qt motion states are not visually distinct")
    sources = manifest.get("sources")
    if not isinstance(sources, dict) or len(sources) < 8:
        raise ValidationError("v6 native Qt motion evidence has incomplete source lineage")
    for relative, digest in sources.items():
        path = ROOT / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValidationError(f"v6 native Qt motion source drift: {relative}")
    performance = load_json(root / "performance.json")
    if (
        not isinstance(performance, dict)
        or performance.get("schemaVersion") != 1
        or performance.get("phase") != 3
        or performance.get("result") != "passed"
        or performance.get("baselineCommit")
        != "6a113e71980d106c38a2bbdece6df171c0ae9ed3"
        or performance.get("maximumRatio") != 1.1
        or performance.get("idleTimerExpected") is not False
    ):
        raise ValidationError("v6 native Qt performance evidence identity is invalid")
    metrics = performance.get("metrics")
    if not isinstance(metrics, dict) or set(metrics) != {
        "galleryStartup",
        "controlRendering",
    }:
        raise ValidationError("v6 native Qt performance metrics are incomplete")
    for name, metric in metrics.items():
        if (
            metric.get("result") != "passed"
            or metric.get("ratio", 99) > 1.1
            or len(metric.get("baselineSamplesMs", [])) != 11
            or len(metric.get("currentSamplesMs", [])) != 11
        ):
            raise ValidationError(f"v6 native Qt performance metric failed: {name}")


def validate_v6_session_evidence(version: str) -> None:
    root = ROOT / "docs/evidence/v6/session"
    contract = load_json(ROOT / "design/session-surface-contract.json")
    manifest = load_json(root / "manifest.json")
    if (
        not isinstance(contract, dict)
        or contract.get("schemaVersion") != 2
        or not isinstance(manifest, dict)
        or manifest.get("schemaVersion") != 1
        or manifest.get("release") != version
        or manifest.get("kind") != "authentic-offscreen-qml"
        or manifest.get("authenticQml") is not True
        or manifest.get("liveSession") is not False
        or manifest.get("reviewStatus") != "reviewed-offscreen"
        or manifest.get("captureCount") != 46
    ):
        raise ValidationError("v6 session evidence identity is invalid")

    captures = manifest.get("captures")
    if not isinstance(captures, list) or len(captures) != 46:
        raise ValidationError("v6 session evidence capture matrix is incomplete")
    expected_resolutions = {
        (size["width"], size["height"])
        for size in contract.get("v6ResolutionMatrix", [])
    }
    expected_scenarios = {
        (surface, scenario)
        for surface, scenarios in contract.get("v6ScenarioMatrix", {}).items()
        for scenario in scenarios
    }
    resolution_captures = set()
    scenario_captures = set()
    choreography: dict[str, set[str]] = {}
    choreography_hashes: dict[str, set[str]] = {}
    for capture in captures:
        if not isinstance(capture, dict):
            raise ValidationError("v6 session evidence contains an invalid capture")
        path = root / capture.get("file", "")
        width = capture.get("width")
        height = capture.get("height")
        digest = capture.get("sha256")
        if (
            not path.is_file()
            or not isinstance(width, int)
            or not isinstance(height, int)
            or png_dimensions(path) != (width, height)
            or digest != hashlib.sha256(path.read_bytes()).hexdigest()
        ):
            raise ValidationError(f"v6 session render drift: {capture.get('file')}")
        kind = capture.get("kind")
        surface = capture.get("surface")
        scenario = capture.get("scenario")
        if kind == "resolution":
            resolution_captures.add((surface, width, height))
        elif kind == "scenario":
            if not isinstance(scenario, str) or not scenario.endswith("-end"):
                raise ValidationError("v6 session scenario is not a settled frame")
            scenario_captures.add((surface, scenario.removesuffix("-end")))
        elif kind == "choreography":
            if not isinstance(scenario, str) or not scenario.startswith("standard-"):
                raise ValidationError("v6 session choreography scenario is invalid")
            frame = scenario.removeprefix("standard-")
            choreography.setdefault(surface, set()).add(frame)
            choreography_hashes.setdefault(surface, set()).add(digest)
        else:
            raise ValidationError(f"unknown v6 session evidence kind: {kind}")

    surfaces = set(contract.get("surfaces", {}))
    if resolution_captures != {
        (surface, width, height)
        for surface in surfaces
        for width, height in expected_resolutions
    }:
        raise ValidationError("v6 session four-resolution matrix is incomplete")
    if scenario_captures != expected_scenarios:
        raise ValidationError("v6 session scenario matrix is incomplete")
    for surface in surfaces:
        if choreography.get(surface) != {"start", "mid", "end"}:
            raise ValidationError(f"v6 session choreography is incomplete: {surface}")
        if len(choreography_hashes.get(surface, set())) != 3:
            raise ValidationError(f"v6 session choreography states are not distinct: {surface}")

    sources = manifest.get("sourceHashes")
    if not isinstance(sources, dict) or len(sources) < 18:
        raise ValidationError("v6 session evidence source lineage is incomplete")
    for relative, digest in sources.items():
        path = ROOT / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValidationError(f"v6 session evidence source drift: {relative}")

    performance = load_json(root / "performance.json")
    metric = performance.get("metric") if isinstance(performance, dict) else None
    if (
        not isinstance(performance, dict)
        or performance.get("schemaVersion") != 1
        or performance.get("phase") != 5
        or performance.get("result") != "passed"
        or performance.get("baselineCommit")
        != "6a113e71980d106c38a2bbdece6df171c0ae9ed3"
        or performance.get("maximumRatio") != 1.1
        or not isinstance(metric, dict)
        or metric.get("result") != "passed"
        or metric.get("ratio", 99) > 1.1
        or len(metric.get("baselineSamplesMs", [])) != 11
        or len(metric.get("currentSamplesMs", [])) != 11
    ):
        raise ValidationError("v6 session first-frame performance evidence is invalid")


def validate_v6_edge_evidence(version: str) -> None:
    contract = load_json(ROOT / "design/edge-polish-contract.json")
    root = ROOT / "docs/evidence/v6/edge-polish"
    manifest = load_json(root / "manifest.json")
    if (
        not isinstance(contract, dict)
        or contract.get("schemaVersion") != 1
        or contract.get("version") != version
        or contract.get("phase") != 6
        or not isinstance(manifest, dict)
        or manifest.get("schemaVersion") != 1
        or manifest.get("version") != version
        or manifest.get("phase") != 6
        or manifest.get("kind") != "deterministic-source-optical-review"
        or manifest.get("reviewStatus") != "reviewed-offscreen"
        or manifest.get("liveDecoration") is not False
        or manifest.get("liveDecorationRemainsPhase7") is not True
    ):
        raise ValidationError("v6 edge-polish evidence identity is invalid")

    aurorae = contract.get("aurorae")
    if (
        not isinstance(aurorae, dict)
        or aurorae.get("titleHeight") != 26
        or aurorae.get("buttonSize") != 26
        or aurorae.get("activeMaterial") != "surfaceRaised"
        or aurorae.get("inactiveMaterial") != "surfaceSunken"
        or aurorae.get("coloredGlow") is not False
        or aurorae.get("buttons") != ["menu", "minimize", "maximize", "restore", "close"]
    ):
        raise ValidationError("v6 Aurorae polish contract is invalid")
    theme = ROOT / f"aurorae/{THEME_ID}"
    settings = load_colors(theme / f"{THEME_ID}rc")
    layout = settings["Layout"]
    if (
        layout.get("titleheight") != "26"
        or layout.get("buttonheight") != "26"
        or any(layout.get(key) != "26" for key in (
            "buttonwidth",
            "buttonwidthmenu",
            "buttonwidthminimize",
            "buttonwidthmaximizerestore",
            "buttonwidthclose",
        ))
    ):
        raise ValidationError("v6 Aurorae title or button geometry drifted")
    decoration = (theme / "decoration.svg").read_text(encoding="utf-8")
    for required in (
        "ColorScheme-Raised",
        "ColorScheme-Sunken",
        "ColorScheme-Highlight",
    ):
        if required not in decoration:
            raise ValidationError(f"v6 Aurorae material is missing {required}")
    if "filter=" in decoration:
        raise ValidationError("v6 Aurorae must not use SVG glow or filters")

    icon_contract = contract.get("icons")
    icon_coverage = load_json(ROOT / "icons/NoxForge/coverage.json")
    if not isinstance(icon_contract, dict) or not isinstance(icon_coverage, dict):
        raise ValidationError("v6 icon polish contract is invalid")
    priority_groups = icon_contract.get("priority")
    if not isinstance(priority_groups, dict):
        raise ValidationError("v6 icon priority groups are missing")
    priority = [
        relative
        for group in ("panel", "systemSettings", "dolphin", "session")
        for relative in priority_groups.get(group, [])
    ]
    frozen = icon_contract.get("coverageFrozen")
    if (
        len(priority) != 56
        or len(set(priority)) != 56
        or icon_coverage.get("phase6Priority") != priority_groups
        or icon_coverage.get("phase6ReviewSizes") != [16, 22, 24, 32, 48]
        or not isinstance(frozen, dict)
        or icon_coverage.get("iconCount") != frozen.get("scalable")
        or icon_coverage.get("opticalCount") != frozen.get("optical")
        or len(icon_coverage.get("runtimeFixture", [])) != frozen.get("runtimeFixture")
        or not set(priority).issubset(icon_coverage.get("runtimeFixture", []))
    ):
        raise ValidationError("v6 priority icon inventory or frozen coverage drifted")

    cursor_contract = contract.get("cursors")
    cursor_coverage = load_json(ROOT / "cursors/NoxForge-Cursors/coverage.json")
    if (
        not isinstance(cursor_contract, dict)
        or not isinstance(cursor_coverage, dict)
        or cursor_contract.get("physicalSizes") != [24, 32, 48]
        or cursor_contract.get("outlineWidth") != 1.75
        or cursor_contract.get("hotspotsFrozen") is not True
        or cursor_coverage.get("sizes") != cursor_contract.get("physicalSizes")
        or cursor_coverage.get("animations", {}).get("wait")
        != cursor_contract.get("animation")
        or cursor_coverage.get("animations", {}).get("progress")
        != cursor_contract.get("animation")
    ):
        raise ValidationError("v6 cursor optical contract drifted")

    sound_contract = contract.get("sound")
    sound_root = ROOT / "sounds/NoxForge"
    sound_digest = hashlib.sha256()
    for path in sorted(candidate for candidate in sound_root.rglob("*") if candidate.is_file()):
        sound_digest.update(path.relative_to(sound_root).as_posix().encode())
        sound_digest.update(b"\0")
        sound_digest.update(path.read_bytes())
    if (
        not isinstance(sound_contract, dict)
        or sound_contract.get("policy") != "unchanged"
        or sound_digest.hexdigest() != sound_contract.get("treeSha256")
    ):
        raise ValidationError("Phase 6 must keep the qualified sound theme unchanged")

    expected_outputs = set(contract.get("evidence", {}).get("outputs", []))
    outputs = manifest.get("outputs")
    if not isinstance(outputs, dict) or set(outputs) != expected_outputs:
        raise ValidationError("v6 edge-polish output matrix is incomplete")
    for relative, details in outputs.items():
        path = ROOT / relative
        if (
            not path.is_file()
            or details.get("sha256") != hashlib.sha256(path.read_bytes()).hexdigest()
            or png_dimensions(path) != (details.get("width"), details.get("height"))
        ):
            raise ValidationError(f"v6 edge-polish output drift: {relative}")

    sources = manifest.get("sourceHashes")
    if not isinstance(sources, dict) or len(sources) < 100:
        raise ValidationError("v6 edge-polish evidence source lineage is incomplete")
    for relative, digest in sources.items():
        path = ROOT / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValidationError(f"v6 edge-polish source drift: {relative}")


def validate_v6_phase7_evidence(version: str) -> None:
    accessibility = load_json(ROOT / "docs/evidence/v6/accessibility-review.json")
    if (
        not isinstance(accessibility, dict)
        or accessibility.get("schemaVersion") != 1
        or accessibility.get("version") != version
        or accessibility.get("phase") != 7
        or accessibility.get("reviewStatus") != "passed"
        or accessibility.get("liveInteraction") is not False
        or accessibility.get("hardcodedRuntimeFontFamilies") != []
    ):
        raise ValidationError("v6 Phase 7 accessibility evidence identity is invalid")
    reviews = accessibility.get("reviews")
    if not isinstance(reviews, dict) or not reviews or not all(reviews.values()):
        raise ValidationError("v6 Phase 7 accessibility review is incomplete")
    preference = accessibility.get("highContrastPreference")
    if (
        not isinstance(preference, dict)
        or preference.get("preference") not in {"NoPreference", "HighContrast"}
        or preference.get("result") not in {"passed", "not-exposed"}
        or (preference.get("preference") == "NoPreference"
            and preference.get("result") != "not-exposed")
    ):
        raise ValidationError("v6 Phase 7 high-contrast observation is not truthful")
    for pair in accessibility.get("contrastPairs", {}).values():
        if pair.get("actual", 0) < pair.get("minimum", 999):
            raise ValidationError("v6 Phase 7 contrast evidence contains a failed pair")

    performance = load_json(ROOT / "docs/evidence/v6/performance.json")
    if (
        not isinstance(performance, dict)
        or performance.get("schemaVersion") != 1
        or performance.get("version") != version
        or performance.get("phase") != 7
        or performance.get("result") != "passed"
        or performance.get("baselineCommit")
        != "6a113e71980d106c38a2bbdece6df171c0ae9ed3"
        or performance.get("maximumRatio") != 1.1
    ):
        raise ValidationError("v6 Phase 7 performance evidence identity is invalid")
    metrics = performance.get("metrics")
    if (
        not isinstance(metrics, dict)
        or set(metrics) != {"galleryStartup", "controlRendering", "qmlFirstFrame"}
    ):
        raise ValidationError("v6 Phase 7 performance metrics are incomplete")
    for metric in metrics.values():
        if metric.get("result") != "passed" or metric.get("ratio", 99) > 1.1:
            raise ValidationError("v6 Phase 7 performance metric failed")
    stress = performance.get("motionStress")
    if (
        not isinstance(stress, dict)
        or stress.get("result") != "passed"
        or stress.get("cycles") != 500
        or stress.get("failedCases") != 0
        or stress.get("idleTimerActive") is not False
        or stress.get("trackedWidgetsAfterCleanup") != 0
        or stress.get("heapGrowthBytes", -1) < 0
        or stress.get("heapGrowthBytes", 999999999)
        > stress.get("heapGrowthLimitBytes", -1)
    ):
        raise ValidationError("v6 Phase 7 motion stress evidence failed")


def validate_tooling(version: str) -> None:
    required = (
        ROOT / "scripts/build.py",
        ROOT / "scripts/release-check.py",
        ROOT / "scripts/sync_version.py",
        ROOT / "scripts/generate_design_system.py",
        ROOT / "scripts/check_v7_aurorae.py",
        ROOT / "scripts/check_v7_icons.py",
        ROOT / "scripts/check_v7_style.py",
        ROOT / "scripts/check_v7_sessions.py",
        ROOT / "scripts/check_v7_assets.py",
        ROOT / "scripts/check_v7_diagnostics.py",
        ROOT / "scripts/check_v7_candidate.py",
        ROOT / "scripts/prepare_v7_candidate.py",
        ROOT / "scripts/run_python_tests.py",
        ROOT / "scripts/render_v6_north_star.py",
        ROOT / "scripts/render_v6_previews.py",
        ROOT / "scripts/render_v6_motion_evidence.py",
        ROOT / "scripts/check_v6_phase3_sanitizers.py",
        ROOT / "scripts/measure_v6_phase3_performance.py",
        ROOT / "scripts/render_v6_session_evidence.py",
        ROOT / "scripts/measure_v6_phase5_performance.py",
        ROOT / "scripts/render_v6_edge_evidence.py",
        ROOT / "scripts/check_v6_accessibility.py",
        ROOT / "scripts/measure_v6_phase7_performance.py",
        ROOT / "scripts/install.sh",
        ROOT / "scripts/uninstall.sh",
        ROOT / "scripts/install-system.sh",
        ROOT / "scripts/uninstall-system.sh",
        ROOT / "docs/QUICKSTART.md",
        ROOT / "docs/INSTALL_FEDORA.md",
        ROOT / "docs/TROUBLESHOOTING.md",
        ROOT / "docs/MANUAL_TESTING.md",
        ROOT / "docs/NOXFORGE_V7_PLAN.md",
        ROOT / "docs/releases/v7.0.0.md",
        ROOT / "docs/evidence/v5/qualification.json",
        ROOT / "docs/evidence/v6/qualification.json",
        ROOT / "docs/evidence/v6/baseline/manifest.json",
        ROOT / "docs/evidence/v6/north-star/manifest.json",
        ROOT / "docs/evidence/v6/brand/preview-manifest.json",
        ROOT / "docs/evidence/v6/qt-motion/manifest.json",
        ROOT / "docs/evidence/v6/qt-motion/performance.json",
        ROOT / "docs/evidence/v6/session/manifest.json",
        ROOT / "docs/evidence/v6/session/performance.json",
        ROOT / "docs/evidence/v6/edge-polish/manifest.json",
        ROOT / "docs/evidence/v6/accessibility-review.json",
        ROOT / "docs/evidence/v6/performance.json",
        ROOT / "docs/evidence/v6/automated-gate.md",
        ROOT / "docs/evidence/v6/public-readback.json",
        ROOT / "docs/evidence/v7/phase0-baseline.json",
        ROOT / "docs/evidence/v7/qualification.json",
        ROOT / "docs/evidence/v7/aurorae/phase1.json",
        ROOT / "docs/evidence/v7/candidate/phase8.json",
        ROOT / "design/v7-candidate-contract.json",
        ROOT / "packaging/noxforge.spec",
        ROOT / "tools/noxforge-doctor",
    )
    missing = [path.relative_to(ROOT) for path in required if not path.is_file()]
    if missing:
        raise ValidationError(f"missing phase 4 tooling or documentation: {missing}")
    install_text = (ROOT / "scripts/install.sh").read_text(encoding="utf-8")
    uninstall_text = (ROOT / "scripts/uninstall.sh").read_text(encoding="utf-8")
    for option in ("--user", "--dry-run"):
        if option not in install_text or option not in uninstall_text:
            raise ValidationError(f"install and uninstall must support {option}")
    system_install = (ROOT / "scripts/install-system.sh").read_text(encoding="utf-8")
    system_uninstall = (ROOT / "scripts/uninstall-system.sh").read_text(encoding="utf-8")
    for option in ("--system", "--dry-run"):
        if option not in system_install or option not in system_uninstall:
            raise ValidationError(f"system install and uninstall must support {option}")
    forbidden = ("sudo", "kwriteconfig", "qdbus", "systemctl", "plasmashell --replace", "plasma-apply-")
    for command in forbidden:
        if command in install_text or command in uninstall_text:
            raise ValidationError(f"install tooling must not execute live-setting command {command!r}")
        if command in system_install or command in system_uninstall:
            raise ValidationError(f"system tooling must not execute live-setting command {command!r}")
    checklist = (ROOT / "docs/MANUAL_TESTING.md").read_text(encoding="utf-8")
    if (
        "docs/evidence/v7/qualification.json" not in checklist
        or "pending" not in checklist.lower()
    ):
        raise ValidationError("manual graphical checks must use the active structured v7 evidence manifest")
    evidence_root = ROOT / "docs/evidence/v5"
    evidence = load_json(evidence_root / "qualification.json")
    if not isinstance(evidence, dict) or evidence.get("schemaVersion") != 2:
        raise ValidationError("v5 evidence manifest must use schema version 2")
    release_state = evidence.get("releaseState")
    if release_state not in {"development", "release"}:
        raise ValidationError("v5 evidence manifest has an invalid release state")
    candidate = evidence.get("candidate")
    if not isinstance(candidate, dict) or candidate.get("version") != "5.0.0":
        raise ValidationError("historical v5 evidence candidate version drift")
    if not isinstance(candidate.get("worktreeDirty"), bool):
        raise ValidationError("v5 evidence candidate must record worktreeDirty")
    release_contract = evidence.get("releaseContract")
    expected_asset_kinds = {
        "source-archive",
        "source-rpm",
        "binary-rpm",
        "qualification",
        "automated-gate",
        "checksums",
    }
    if (
        not isinstance(release_contract, dict)
        or release_contract.get("assetCount") != 6
        or set(release_contract.get("assetKinds", [])) != expected_asset_kinds
    ):
        raise ValidationError("v5 evidence manifest must define the six-asset release contract")
    if release_state == "development":
        if not str(candidate["version"]).endswith("-dev"):
            raise ValidationError("development evidence requires a -dev version")
        if any(candidate.get(field) is not None for field in ("sourceCommit", "package")):
            raise ValidationError("development evidence must not invent a release commit or package")
        if candidate.get("sourceRef") != "main" or candidate.get("artifacts") != []:
            raise ValidationError("development evidence must target main with no release artifacts")
    else:
        source_commit = candidate.get("sourceCommit")
        if str(candidate["version"]).endswith("-dev"):
            raise ValidationError("release evidence requires a stable version")
        if candidate.get("sourceRef") != f"v{candidate['version']}":
            raise ValidationError("release evidence tag does not match its version")
        if not isinstance(source_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", source_commit):
            raise ValidationError("release evidence requires an exact source commit")
        if not isinstance(candidate.get("package"), str) or not candidate["package"]:
            raise ValidationError("release evidence requires a package description")
        if not isinstance(candidate.get("artifacts"), list) or len(candidate["artifacts"]) != 6:
            raise ValidationError("release evidence requires exactly six artifacts")
    cases = evidence.get("liveCases") if isinstance(evidence, dict) else None
    if not isinstance(cases, list) or len(cases) < 16:
        raise ValidationError("v5 evidence manifest does not contain the required live matrix")
    allowed_results = {"passed", "failed", "blocked", "not-applicable"}
    for case in cases:
        if not isinstance(case, dict) or case.get("result") not in allowed_results:
            raise ValidationError("v5 evidence manifest has an invalid live result")
        if case.get("result") == "blocked" and not case.get("blocker"):
            raise ValidationError("blocked live evidence must record its blocker")
        if case.get("result") == "passed":
            linked = case.get("evidence")
            if not isinstance(linked, str) or not (
                evidence_root / linked
            ).is_file():
                raise ValidationError("passed live evidence must link a real evidence file")
    automated = evidence.get("automatedEvidence")
    if not isinstance(automated, dict) or automated.get("result") not in allowed_results:
        raise ValidationError("v5 automated evidence has an invalid result")
    if automated.get("result") == "passed":
        linked = automated.get("evidence")
        if not isinstance(linked, str) or not (evidence_root / linked).is_file():
            raise ValidationError("passed automated evidence must link a real evidence file")
    elif automated.get("result") == "blocked" and not automated.get("blocker"):
        raise ValidationError("blocked automated evidence must record its blocker")

    v6 = load_json(ROOT / "docs/evidence/v6/qualification.json")
    v6_version = V6_RELEASE_VERSION
    if (
        not isinstance(v6, dict)
        or v6.get("schemaVersion") != 2
        or v6.get("releaseState") not in {"candidate", "release"}
    ):
        raise ValidationError("v6 qualification identity is invalid")
    v6_candidate = v6.get("candidate")
    expected_artifacts = {
        "automated-gate.md",
        f"noxforge-{v6_version}.tar.xz",
        f"noxforge-{v6_version}-1.fc44.src.rpm",
        f"noxforge-{v6_version}-1.fc44.x86_64.rpm",
        "qualification.json",
        "SHA256SUMS",
    }
    if (
        not isinstance(v6_candidate, dict)
        or v6_candidate.get("version") != v6_version
        or v6_candidate.get("sourceRef") != f"v{v6_version}"
        or v6_candidate.get("package") != f"noxforge-{v6_version}-1.fc44.x86_64.rpm"
        or set(v6_candidate.get("artifacts", [])) != expected_artifacts
    ):
        raise ValidationError("v6 candidate metadata is incomplete")
    v6_release_contract = v6.get("releaseContract")
    if (
        not isinstance(v6_release_contract, dict)
        or v6_release_contract.get("assetCount") != 6
        or set(v6_release_contract.get("assetKinds", [])) != expected_asset_kinds
    ):
        raise ValidationError("v6 qualification must preserve the six-asset contract")
    if v6["releaseState"] == "candidate":
        if (
            v6_candidate.get("sourceCommit") is not None
            or v6_candidate.get("worktreeDirty") is not None
            or not isinstance(v6.get("releaseBlockers"), list)
            or len(v6["releaseBlockers"]) < 4
        ):
            raise ValidationError("v6 local candidate must keep remote/tag state blocked")
    else:
        if (
            not isinstance(v6_candidate.get("sourceCommit"), str)
            or not re.fullmatch(r"[0-9a-f]{40}", v6_candidate["sourceCommit"])
            or v6_candidate.get("worktreeDirty") is not False
        ):
            raise ValidationError("v6 release evidence requires exact clean tag lineage")
    policy = v6.get("evidencePolicy")
    if (
        not isinstance(policy, dict)
        or policy.get("v5ResultsPromoted") is not False
        or policy.get("offscreenIsLiveEvidence") is not False
        or policy.get("unavailableCasesRemainBlocked") is not True
    ):
        raise ValidationError("v6 evidence policy is invalid")
    v6_automated = v6.get("automatedEvidence")
    if (
        not isinstance(v6_automated, dict)
        or v6_automated.get("result") != "passed"
        or not isinstance(v6_automated.get("evidence"), str)
        or not (
            ROOT / "docs/evidence/v6" / v6_automated["evidence"]
        ).is_file()
    ):
        raise ValidationError("v6 automated candidate evidence is invalid")
    automated_cases = v6.get("automatedCases")
    if not isinstance(automated_cases, list) or not automated_cases:
        raise ValidationError("v6 automatedCases are missing")
    for case in automated_cases:
        if (
            not isinstance(case, dict)
            or case.get("status") not in {"pending", "blocked", "passed"}
            or not case.get("reason")
        ):
            raise ValidationError("v6 automatedCases contain an invalid result")
        if case.get("status") == "passed":
            linked = case.get("evidence")
            if not isinstance(linked, str) or not (
                ROOT / "docs/evidence/v6" / linked
            ).is_file():
                raise ValidationError("passed v6 automated evidence must link a real file")
    live_cases = v6.get("liveCases")
    if not isinstance(live_cases, list) or not live_cases:
        raise ValidationError("v6 liveCases are missing")
    for case in live_cases:
        if (
            not isinstance(case, dict)
            or case.get("status") not in {"pending", "blocked", "passed"}
            or not case.get("reason")
        ):
            raise ValidationError("v6 liveCases contain an invalid result")
        if case.get("status") == "passed":
            linked = case.get("evidence")
            if not isinstance(linked, str) or not (
                ROOT / "docs/evidence/v6" / linked
            ).is_file():
                raise ValidationError("passed v6 live evidence must link a real file")

    v7 = load_json(ROOT / "docs/evidence/v7/qualification.json")
    if (
        not isinstance(v7, dict)
        or v7.get("schemaVersion") != 2
        or v7.get("releaseState") != "release"
        or v7.get("releaseReady") is not True
    ):
        raise ValidationError("v7 qualification identity is invalid")
    v7_candidate = v7.get("candidate")
    if (
        not isinstance(v7_candidate, dict)
        or v7_candidate.get("version") != version
        or not isinstance(v7_candidate.get("sourceCommit"), str)
        or not re.fullmatch(r"[0-9a-f]{40}", v7_candidate["sourceCommit"])
        or v7_candidate.get("sourceRef") != f"v{version}"
        or v7_candidate.get("worktreeDirty") is not False
        or v7_candidate.get("package") != f"noxforge-{version}-1.fc44.x86_64.rpm"
        or not isinstance(v7_candidate.get("artifacts"), list)
        or len(v7_candidate["artifacts"]) != 6
    ):
        raise ValidationError("v7 stable candidate metadata is invalid")
    v7_policy = v7.get("evidencePolicy")
    if (
        not isinstance(v7_policy, dict)
        or v7_policy.get("v6ResultsPromoted") is not False
        or v7_policy.get("offscreenIsLiveEvidence") is not False
        or v7_policy.get("mandatoryCasesRequireComposedEvidence") is not True
        or v7_policy.get("physicalLimitationsRemainUnclaimed") is not True
    ):
        raise ValidationError("v7 evidence policy is invalid")
    v7_live = v7.get("liveCases")
    if not isinstance(v7_live, list) or not v7_live:
        raise ValidationError("v7 live matrix is missing")
    allowed_v7 = {"pending", "blocked", "failed", "passed", "not-applicable"}
    for case in v7_live:
        if (
            not isinstance(case, dict)
            or case.get("status") not in allowed_v7
            or not case.get("reason")
        ):
            raise ValidationError("v7 live matrix contains an invalid result")
    required_live = {
        "aurorae-maximized-scaling",
        "core-icon-visibility",
        "application-cohesion",
        "plasma-shell-matrix",
        "session-surfaces",
        "accessibility-input",
    }
    live_by_id = {case.get("id"): case for case in v7_live}
    if not required_live <= set(live_by_id) or any(
        live_by_id[case_id].get("status") != "passed" for case_id in required_live
    ):
        raise ValidationError("v7 mandatory composed live cases must pass")
    if v7.get("releaseBlockers") != []:
        raise ValidationError("qualified v7 release must not retain release blockers")
    p0 = [case for case in v7_live if case.get("priority") == "P0"]
    if not p0 or any(case.get("status") != "passed" for case in p0):
        raise ValidationError("v7 P0 release cases must be closed by composed evidence")


def validate_tooling(version: str) -> None:
    """Validate active V8 tooling without reinterpreting historical evidence."""
    required = (
        ROOT / "scripts/build.py",
        ROOT / "scripts/build_store_packages.py",
        ROOT / "scripts/check_store_kpackages.py",
        ROOT / "scripts/validate_store_packages.py",
        ROOT / "scripts/validate_release_manifest.py",
        ROOT / "scripts/release-check.py",
        ROOT / "scripts/sync_version.py",
        ROOT / "scripts/run_python_tests.py",
        ROOT / "scripts/install.sh",
        ROOT / "scripts/uninstall.sh",
        ROOT / "scripts/install-system.sh",
        ROOT / "scripts/uninstall-system.sh",
        ROOT / "docs/QUICKSTART.md",
        ROOT / "docs/INSTALL_FEDORA.md",
        ROOT / "docs/INSTALL_PORTABLE.md",
        ROOT / "docs/INSTALL_ARCH.md",
        ROOT / "docs/DOCTOR_MANUAL.md",
        ROOT / "docs/TROUBLESHOOTING.md",
        ROOT / "docs/MANUAL_TESTING.md",
        ROOT / "docs/NOXFORGE_V8_PLAN.md",
        ROOT / "distribution/release-manifest.json",
        ROOT / "distribution/kde-store/package-manifest.json",
        ROOT / "media/manifest.json",
        ROOT / "packaging/noxforge.spec",
        ROOT / "packaging/arch/PKGBUILD",
        ROOT / "packaging/arch/.SRCINFO",
        ROOT / "tools/noxforge-doctor",
    )
    missing = [path.relative_to(ROOT) for path in required if not path.is_file()]
    if missing:
        raise ValidationError(f"missing active V8 tooling or documentation: {missing}")
    issue_templates = sorted((ROOT / ".github/ISSUE_TEMPLATE").glob("*.yml"))
    if len(issue_templates) != 4:
        raise ValidationError("V8 requires exactly four focused issue templates")
    install_text = (ROOT / "scripts/install.sh").read_text(encoding="utf-8")
    uninstall_text = (ROOT / "scripts/uninstall.sh").read_text(encoding="utf-8")
    for option in ("--user", "--dry-run"):
        if option not in install_text or option not in uninstall_text:
            raise ValidationError(f"install and uninstall must support {option}")
    for forbidden in ("sudo", "kwriteconfig", "qdbus", "systemctl", "plasmashell --replace", "plasma-apply-"):
        if forbidden in install_text or forbidden in uninstall_text:
            raise ValidationError(f"portable tooling must not execute live-setting command {forbidden!r}")
    manifest = load_json(ROOT / "distribution/release-manifest.json")
    if manifest.get("release", {}).get("version") != version:
        raise ValidationError("release manifest version drift")
    if manifest.get("evidence", {}).get("policy", {}).get("offscreenIsLiveEvidence") is not False:
        raise ValidationError("V8 evidence policy must keep offscreen separate from live")


def validate_generated_sources(version: str) -> None:
    scripts = [
        "scripts/sync_version.py",
        "scripts/generate_design_system.py",
        "scripts/generate_plasma_svgs.py",
        "scripts/generate_visual_assets.py",
        "scripts/generate_cursors.py",
        "scripts/generate_sound_theme.py",
        "scripts/render_wallpaper.py",
        "scripts/render_artwork_evidence.py",
        "scripts/check_v7_aurorae.py",
        "scripts/check_v7_icons.py",
        "scripts/check_v7_style.py",
        "scripts/check_v7_sessions.py",
        "scripts/check_v7_assets.py",
        "scripts/check_v7_diagnostics.py",
        "scripts/check_v7_candidate.py",
    ]
    if version == V6_RELEASE_VERSION:
        scripts.extend(
            [
                "scripts/capture_v6_baseline.py",
                "scripts/render_v6_north_star.py",
                "scripts/render_v6_previews.py",
                "scripts/render_v6_motion_evidence.py",
                "scripts/measure_v6_phase3_performance.py",
                "scripts/render_v6_session_evidence.py",
                "scripts/measure_v6_phase5_performance.py",
                "scripts/render_v6_edge_evidence.py",
                "scripts/check_v6_accessibility.py",
                "scripts/measure_v6_phase7_performance.py",
            ]
        )
    for script in scripts:
        result = subprocess.run(
            [sys.executable, str(ROOT / script), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise ValidationError(f"generated source drift in {script}: {detail}")
    raster = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_plasma_rasters.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if raster.returncode != 0:
        raise ValidationError(f"Plasma raster matrix failed: {(raster.stderr or raster.stdout).strip()}")


def validate_generated_sources(version: str) -> None:
    scripts = [
        ("scripts/sync_version.py", "--check"),
        ("scripts/generate_design_system.py", "--check"),
        ("scripts/generate_plasma_svgs.py", "--check"),
        ("scripts/generate_visual_assets.py", "--check"),
        ("scripts/generate_cursors.py", "--check"),
        ("scripts/generate_sound_theme.py", "--check"),
        ("scripts/render_wallpaper.py", "--check"),
        ("scripts/check_plasma_rasters.py",),
        ("scripts/validate_release_manifest.py",),
    ]
    for command in scripts:
        result = subprocess.run(
            [sys.executable, str(ROOT / command[0]), *command[1:]],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise ValidationError(f"generated source drift in {command[0]}: {detail}")


def validate_json_and_xml() -> None:
    for path in sorted(ROOT.rglob("*.json")):
        if ".git" not in path.parts:
            load_json(path)
    for pattern in ("*.svg", "*.xml"):
        for path in sorted(ROOT.rglob(pattern)):
            if ".git" not in path.parts:
                try:
                    ET.parse(path)
                except (OSError, ET.ParseError) as error:
                    raise ValidationError(f"invalid XML {path.relative_to(ROOT)}: {error}") from error


def validate_no_package_symlinks() -> None:
    for package_root in PACKAGE_ROOTS:
        if not package_root.exists():
            continue
        links = [path.relative_to(ROOT) for path in package_root.rglob("*") if path.is_symlink()]
        if links:
            raise ValidationError(f"package symlinks are forbidden: {links}")


def validate() -> None:
    version = validate_version()
    tokens = validate_tokens(version)
    validate_motion_contract(tokens, version)
    validate_color_scheme(ROOT / "color-schemes/NoxForgeDark.colors")
    validate_color_scheme(ROOT / f"plasma/desktoptheme/{THEME_ID}/colors")
    if (ROOT / "color-schemes/NoxForgeDark.colors").read_bytes() != (
        ROOT / f"plasma/desktoptheme/{THEME_ID}/colors"
    ).read_bytes():
        raise ValidationError("standalone and Plasma Style color schemes differ")
    validate_metadata(version)
    validate_repository_urls()
    validate_plasma_style()
    validate_look_and_feel(version)
    validate_tabbox(version)
    validate_aurorae(version)
    validate_icons()
    validate_cursors()
    validate_sounds()
    validate_sddm(version)
    validate_wallpaper(version)
    validate_artwork_evidence(version)
    if version == V6_RELEASE_VERSION:
        validate_v6_brand_previews(version)
        validate_v6_north_star(version)
        validate_v6_motion_evidence(version)
        validate_v6_session_evidence(version)
        validate_v6_edge_evidence(version)
        validate_v6_phase7_evidence(version)
    validate_tooling(version)
    validate_generated_sources(version)
    validate_json_and_xml()
    validate_no_package_symlinks()


def main() -> int:
    try:
        validate()
    except (OSError, ValidationError) as error:
        print(f"validation failed: {error}", file=sys.stderr)
        return 1
    print("NoxForge validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
