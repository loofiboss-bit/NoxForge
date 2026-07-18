#!/usr/bin/env python3
"""Validate NoxForge sources and package contracts using the standard library."""

from __future__ import annotations

import configparser
import gzip
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME_ID = "io.github.loofiboss.noxforge.desktop"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
PACKAGE_ROOTS = (ROOT / "plasma", ROOT / "aurorae", ROOT / "icons", ROOT / "wallpapers")
POSITIONS = {"top", "topright", "right", "bottomright", "bottom", "bottomleft", "left", "topleft", "center"}
PLASMA_STATES = {
    "widgets/button.svg": {"normal", "hover", "focus", "pressed", "toolbutton-hover", "toolbutton-focus", "toolbutton-pressed"},
    "widgets/tasks.svg": {"normal", "hover", "focus", "attention", "minimized", "progress"},
    "widgets/viewitem.svg": {"normal", "hover", "selected", "selected+hover"},
    "widgets/lineedit.svg": {"base", "hover", "focus"},
    "widgets/plasmoidheading.svg": {"header", "footer"},
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
        raise ValidationError(f"VERSION is not stable SemVer: {version!r}")
    return version


def validate_tokens(version: str) -> dict[str, object]:
    tokens = load_json(ROOT / "design/tokens.json")
    if not isinstance(tokens, dict):
        raise ValidationError("design/tokens.json must contain an object")
    if tokens.get("themeId") != THEME_ID or tokens.get("version") != version:
        raise ValidationError("token identity or version does not match repository metadata")
    required = {
        "background": "#0E1318",
        "surface": "#141B21",
        "surfaceRaised": "#1A232B",
        "textPrimary": "#E8F0F2",
        "textSecondary": "#A6B4B9",
        "accent": "#A3FF47",
        "detailCyan": "#22D3EE",
        "detailViolet": "#A78BFA",
    }
    if tokens.get("colors") != {**required, "negative": "#FF6B7A", "neutral": "#FBBF24"}:
        raise ValidationError("design tokens do not match the locked NoxForge palette")
    return tokens


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


def svg_ids(path: Path) -> set[str]:
    try:
        return {element.get("id") for element in ET.parse(path).iter() if element.get("id")}
    except (OSError, ET.ParseError) as error:
        raise ValidationError(f"invalid SVG {path.relative_to(ROOT)}: {error}") from error


def validate_plasma_style() -> None:
    theme = ROOT / f"plasma/desktoptheme/{THEME_ID}"
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
    for relative, states in PLASMA_STATES.items():
        found = svg_ids(theme / relative)
        for state in states:
            if not {f"{state}-{position}" for position in POSITIONS}.issubset(found):
                raise ValidationError(f"{relative} has an incomplete {state} frame")
    for path in sorted(theme.rglob("*.svg")):
        text = path.read_text(encoding="utf-8")
        if 'id="current-color-scheme"' not in text or "ColorScheme-Highlight" not in text:
            raise ValidationError(f"{path.relative_to(ROOT)} does not use Plasma color classes")
        if "filter=" in text:
            raise ValidationError(f"{path.relative_to(ROOT)} uses unsupported runtime SVG filters")
    plasmarc = (theme / "plasmarc").read_text(encoding="utf-8")
    if "FallbackTheme=default" not in plasmarc:
        raise ValidationError("Plasma Style must explicitly fall back to Breeze")
    if list(theme.rglob("metadata.desktop")):
        raise ValidationError("Plasma Style must not use Plasma 5 metadata.desktop")


def validate_aurorae() -> None:
    theme = ROOT / f"aurorae/{THEME_ID}"
    metadata = load_colors(theme / "metadata.desktop")
    entry = metadata["Desktop Entry"]
    if entry.get("x-kde-plugininfo-name") != THEME_ID:
        raise ValidationError("Aurorae plugin ID does not match its directory")
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
    for name in ("close", "minimize", "maximize", "restore"):
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
    index = load_colors(theme / "index.theme")
    inherited = index["Icon Theme"].get("inherits", "").split(",")
    if inherited != ["breeze-dark", "breeze", "hicolor"]:
        raise ValidationError("icon fallback order must be breeze-dark,breeze,hicolor")
    expected_counts = {"actions": 8, "places": 5, "devices": 6, "status": 5}
    icons = list((theme / "scalable").glob("*/*.svg"))
    if len(icons) != 24:
        raise ValidationError(f"icon prototype must contain exactly 24 SVGs, found {len(icons)}")
    for category, count in expected_counts.items():
        found = list((theme / "scalable" / category).glob("*.svg"))
        if len(found) != count:
            raise ValidationError(f"icon category {category} requires {count} icons, found {len(found)}")
    for path in icons:
        root = ET.parse(path).getroot()
        if root.get("viewBox") != "0 0 24 24":
            raise ValidationError(f"icon {path.name} must use the 24px design grid")
        forbidden = [element for element in root.iter() if element.tag.rsplit("}", 1)[-1] in {"image", "text"}]
        if forbidden:
            raise ValidationError(f"icon {path.name} embeds raster data or text")


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValidationError(f"invalid PNG header: {path.relative_to(ROOT)}")
    return struct.unpack(">II", data[16:24])


def validate_wallpaper(version: str) -> None:
    package = ROOT / "wallpapers/NoxForge"
    metadata = load_json(package / "metadata.json")
    if not isinstance(metadata, dict) or not isinstance(metadata.get("KPlugin"), dict):
        raise ValidationError("wallpaper metadata requires a KPlugin object")
    plugin = metadata["KPlugin"]
    if plugin.get("Id") != "NoxForge" or plugin.get("Version") != version or plugin.get("License") != "MIT":
        raise ValidationError("wallpaper metadata identity, version, or license mismatch")
    source = ET.parse(package / "contents/source/NoxForge.svg").getroot()
    if source.get("viewBox") != "0 0 2560 1440":
        raise ValidationError("editable wallpaper source must use a 2560x1440 viewBox")
    if png_dimensions(package / "contents/images/2560x1440.png") != (2560, 1440):
        raise ValidationError("wallpaper output must be exactly 2560x1440")


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
    validate_tokens(version)
    validate_color_scheme(ROOT / "color-schemes/NoxForgeDark.colors")
    validate_color_scheme(ROOT / f"plasma/desktoptheme/{THEME_ID}/colors")
    if (ROOT / "color-schemes/NoxForgeDark.colors").read_bytes() != (
        ROOT / f"plasma/desktoptheme/{THEME_ID}/colors"
    ).read_bytes():
        raise ValidationError("standalone and Plasma Style color schemes differ")
    validate_metadata(version)
    validate_plasma_style()
    validate_aurorae()
    validate_icons()
    validate_wallpaper(version)
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
