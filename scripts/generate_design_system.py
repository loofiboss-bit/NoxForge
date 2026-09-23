#!/usr/bin/env python3
"""Generate NoxForge design-system consumers from the canonical token file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKENS_PATH = ROOT / "design/tokens.json"
THEME_ID = "io.github.loofiboss.noxforge.desktop"

THEME_OBSIDIAN_ID = "io.github.loofiboss.noxforge.obsidian.desktop"

QML_TARGETS = (
    (ROOT / f"look-and-feel/{THEME_ID}/contents/splash/Tokens.qml", "standard"),
    (ROOT / f"look-and-feel/{THEME_ID}/contents/logout/Tokens.qml", "standard"),
    (ROOT / f"kwin/tabbox/{THEME_ID}/contents/ui/Tokens.qml", "standard"),
    (ROOT / "sddm/NoxForge/Tokens.qml", "standard"),
    (ROOT / f"look-and-feel/{THEME_OBSIDIAN_ID}/contents/splash/Tokens.qml", "obsidian"),
    (ROOT / f"look-and-feel/{THEME_OBSIDIAN_ID}/contents/logout/Tokens.qml", "obsidian"),
    (ROOT / "sddm/NoxForgeObsidian/Tokens.qml", "obsidian"),
)

MOTION_POLICY_TARGETS = (
    ROOT / f"look-and-feel/{THEME_ID}/contents/splash/MotionPolicy.qml",
    ROOT / f"look-and-feel/{THEME_ID}/contents/logout/MotionPolicy.qml",
    ROOT / f"kwin/tabbox/{THEME_ID}/contents/ui/MotionPolicy.qml",
    ROOT / f"look-and-feel/{THEME_OBSIDIAN_ID}/contents/splash/MotionPolicy.qml",
    ROOT / f"look-and-feel/{THEME_OBSIDIAN_ID}/contents/logout/MotionPolicy.qml",
)

MARK_TARGETS = (
    ROOT / "design/brand/noxforge-mark.svg",
    ROOT / f"look-and-feel/{THEME_ID}/contents/splash/NoxForgeMark.svg",
    ROOT / f"look-and-feel/{THEME_ID}/contents/logout/NoxForgeMark.svg",
    ROOT / f"kwin/tabbox/{THEME_ID}/contents/ui/NoxForgeMark.svg",
    ROOT / "sddm/NoxForge/NoxForgeMark.svg",
    ROOT / f"look-and-feel/{THEME_OBSIDIAN_ID}/contents/splash/NoxForgeMark.svg",
    ROOT / f"look-and-feel/{THEME_OBSIDIAN_ID}/contents/logout/NoxForgeMark.svg",
    ROOT / "sddm/NoxForgeObsidian/NoxForgeMark.svg",
)

LOCKUP_TARGETS = (
    ROOT / "design/brand/noxforge-lockup.svg",
    ROOT / f"look-and-feel/{THEME_ID}/contents/splash/NoxForgeLockup.svg",
    ROOT / "sddm/NoxForge/NoxForgeLockup.svg",
    ROOT / f"look-and-feel/{THEME_OBSIDIAN_ID}/contents/splash/NoxForgeLockup.svg",
    ROOT / "sddm/NoxForgeObsidian/NoxForgeLockup.svg",
)

MONO_MARK_TARGET = ROOT / "design/brand/noxforge-mark-mono.svg"


def load_tokens() -> dict[str, object]:
    return json.loads(TOKENS_PATH.read_text(encoding="utf-8"))


def rgb(hex_color: str) -> str:
    return ",".join(str(int(hex_color[index : index + 2], 16)) for index in (1, 3, 5))


def canonical_tokens(tokens: dict[str, object]) -> str:
    return json.dumps(tokens, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def cpp_header(tokens: dict[str, object]) -> str:
    colors = tokens["colors"]
    colors_obsidian = tokens.get("colorsObsidian", colors)
    geometry = tokens["geometry"]
    opacity = tokens["opacity"]
    overlay = tokens["overlay"]
    shadow = tokens["shadow"]
    states = tokens["states"]
    motion = tokens["motion"]
    assert all(
        isinstance(value, dict)
        for value in (colors, colors_obsidian, geometry, opacity, overlay, shadow, states, motion)
    )
    reduced_motion = motion["reducedMotion"]
    assert isinstance(reduced_motion, dict)
    functions = (
        ("background", "background"), ("surfaceSunken", "surfaceSunken"),
        ("surface", "surface"), ("surfaceRaised", "surfaceRaised"),
        ("surfaceOverlay", "surfaceOverlay"), ("surfaceHover", "surfaceHover"),
        ("surfaceSelected", "surfaceSelected"), ("border", "border"),
        ("borderStrong", "borderStrong"), ("edgeHighlight", "edgeHighlight"),
        ("outlineMuted", "outlineMuted"), ("textPrimary", "textPrimary"),
        ("textSecondary", "textSecondary"), ("textDisabled", "textDisabled"),
        ("accent", "accent"), ("accentPressed", "accentPressed"),
        ("accentSoft", "accentSoft"), ("accentMuted", "accentMuted"),
        ("cyan", "detailCyan"), ("violet", "detailViolet"),
        ("negative", "negative"), ("warning", "neutral"),
    )
    standard_lines = "\n".join(
        f'inline QColor {name}() {{ return QColor(QStringLiteral("{colors[key]}")); }}'
        for name, key in functions
    )
    obsidian_lines = "\n".join(
        f'inline QColor {name}() {{ return QColor(QStringLiteral("{colors_obsidian[key]}")); }}'
        for name, key in functions
    )
    struct_fields = "\n".join(
        f'    QColor {name};'
        for name, _ in functions
    ) + "\n    QColor accentInk;"

    struct_standard_init = "\n".join(
        f'        Standard::{name}(),'
        for name, _ in functions
    ) + "\n        Standard::accentInk()"

    struct_obsidian_init = "\n".join(
        f'        Obsidian::{name}(),'
        for name, _ in functions
    ) + "\n        Obsidian::accentInk()"

    compat_lines = "\n".join(
        f'inline QColor {name}(bool obsidian = false) {{ return obsidian ? Obsidian::{name}() : Standard::{name}(); }}'
        for name, _ in functions
    )

    return f'''// SPDX-License-Identifier: MIT
// Generated by scripts/generate_design_system.py. Do not edit directly.
#pragma once

#include <QByteArray>
#include <QColor>

namespace NoxForgePalette {{

namespace Standard {{
{standard_lines}
inline QColor accentInk() {{ return background(); }}
}} // namespace Standard

namespace Obsidian {{
{obsidian_lines}
inline QColor accentInk() {{ return background(); }}
}} // namespace Obsidian

struct PaletteColors {{
{struct_fields}
}};

inline PaletteColors standardColors()
{{
    return {{
{struct_standard_init}
    }};
}}

inline PaletteColors obsidianColors()
{{
    return {{
{struct_obsidian_init}
    }};
}}

inline PaletteColors palette(bool obsidian = false)
{{
    return obsidian ? obsidianColors() : standardColors();
}}

{compat_lines}
inline QColor accentInk(bool obsidian = false) {{ return background(obsidian); }}

constexpr int radius = {geometry["cornerRadius"]};
constexpr int compactRadius = {geometry["compactRadius"]};
constexpr int overlayRadius = {geometry["overlayRadius"]};
constexpr int notch = {geometry["forgeNotch"]};
constexpr int borderWidth = {geometry["borderWidth"]};
constexpr int focusWidth = {geometry["focusWidth"]};
constexpr int controlHeight = {geometry["controlHeight"]};
constexpr int largeControlHeight = {geometry["largeControlHeight"]};
constexpr int activeMarkerWidth = {states["activeMarkerWidth"]};
constexpr qreal disabledOpacity = {opacity["disabled"]};
constexpr qreal enabledOpacity = {opacity["enabled"]};
constexpr qreal inactiveOpacity = {opacity["inactive"]};
constexpr qreal subtleOpacity = {opacity["subtle"]};
constexpr qreal scrimOpacity = {opacity["scrim"]};
constexpr qreal hoverOverlayOpacity = {overlay["hover"]["opacity"]};
constexpr qreal pressedOverlayOpacity = {overlay["pressed"]["opacity"]};
constexpr qreal busyOverlayOpacity = {overlay["busy"]["opacity"]};
constexpr int controlShadowOffsetY = {shadow["ambient"]["offsetY"]};
constexpr int controlShadowBlurRadius = {shadow["ambient"]["blurRadius"]};
constexpr qreal controlShadowOpacity = {shadow["ambient"]["opacity"]};
constexpr int popupShadowOffsetY = {shadow["overlay"]["offsetY"]};
constexpr int popupShadowBlurRadius = {shadow["overlay"]["blurRadius"]};
constexpr qreal popupShadowOpacity = {shadow["overlay"]["opacity"]};
constexpr int instantDuration = {motion["instantMs"]};
constexpr int pressDuration = {motion["pressMs"]};
constexpr int productiveDuration = {motion["productiveMs"]};
constexpr int selectionDuration = {motion["selectionMs"]};
constexpr int containerDuration = {motion["containerMs"]};
constexpr int expressiveDuration = {motion["expressiveMs"]};
constexpr int staggerDuration = {motion["staggerMs"]};
constexpr int busyCycleDuration = {motion["busyCycleMs"]};
constexpr int reducedMotionDuration = {reduced_motion["durationMs"]};
constexpr bool reducedSpatialMotion = {str(reduced_motion["spatialMotion"]).lower()};
constexpr bool reducedBusyIndicatorStatic = {str(reduced_motion["busyIndicatorStatic"]).lower()};

inline QByteArray canonicalTokensJson()
{{
    return QByteArrayLiteral(R"noxforge({canonical_tokens(tokens)})noxforge");
}}

}} // namespace NoxForgePalette
'''


def qml_tokens(tokens: dict[str, object], variant: str = "standard") -> str:
    colors = (
        tokens["colorsObsidian"]
        if variant == "obsidian" and "colorsObsidian" in tokens
        else tokens["colors"]
    )
    geometry = tokens["geometry"]
    opacity = tokens["opacity"]
    overlay = tokens["overlay"]
    shadow = tokens["shadow"]
    states = tokens["states"]
    motion = tokens["motion"]
    typography = tokens["typography"]
    assert all(
        isinstance(value, dict)
        for value in (colors, geometry, opacity, overlay, shadow, states, motion, typography)
    )
    reduced_motion = motion["reducedMotion"]
    typography_roles = typography["roles"]
    curves = motion["curves"]
    assert all(
        isinstance(value, dict)
        for value in (reduced_motion, typography_roles, curves)
    )
    color_lines = "\n".join(
        f'    readonly property color {name}: "{value}"' for name, value in colors.items()
    )
    return f'''// SPDX-License-Identifier: MIT
// Generated by scripts/generate_design_system.py. Do not edit directly.
import QtQuick 2.15

QtObject {{
{color_lines}
    readonly property int radius: {geometry["cornerRadius"]}
    readonly property int compactRadius: {geometry["compactRadius"]}
    readonly property int overlayRadius: {geometry["overlayRadius"]}
    readonly property int notch: {geometry["forgeNotch"]}
    readonly property int compactSpacing: {geometry["compactSpacing"]}
    readonly property int standardSpacing: {geometry["standardSpacing"]}
    readonly property int borderWidth: {geometry["borderWidth"]}
    readonly property int focusWidth: {geometry["focusWidth"]}
    readonly property int controlHeight: {geometry["controlHeight"]}
    readonly property int largeControlHeight: {geometry["largeControlHeight"]}
    readonly property int activeMarkerWidth: {states["activeMarkerWidth"]}
    readonly property real disabledOpacity: {opacity["disabled"]}
    readonly property real enabledOpacity: {opacity["enabled"]}
    readonly property real inactiveOpacity: {opacity["inactive"]}
    readonly property real subtleOpacity: {opacity["subtle"]}
    readonly property real scrimOpacity: {opacity["scrim"]}
    readonly property color hoverOverlayColor: "{colors[overlay["hover"]["color"]]}"
    readonly property real hoverOverlayOpacity: {overlay["hover"]["opacity"]}
    readonly property color pressedOverlayColor: "{colors[overlay["pressed"]["color"]]}"
    readonly property real pressedOverlayOpacity: {overlay["pressed"]["opacity"]}
    readonly property color busyOverlayColor: "{colors[overlay["busy"]["color"]]}"
    readonly property real busyOverlayOpacity: {overlay["busy"]["opacity"]}
    readonly property int controlShadowOffsetY: {shadow["ambient"]["offsetY"]}
    readonly property int controlShadowBlurRadius: {shadow["ambient"]["blurRadius"]}
    readonly property real controlShadowOpacity: {shadow["ambient"]["opacity"]}
    readonly property int popupShadowOffsetY: {shadow["overlay"]["offsetY"]}
    readonly property int popupShadowBlurRadius: {shadow["overlay"]["blurRadius"]}
    readonly property real popupShadowOpacity: {shadow["overlay"]["opacity"]}
    readonly property int instantDuration: {motion["instantMs"]}
    readonly property int pressDuration: {motion["pressMs"]}
    readonly property int productiveDuration: {motion["productiveMs"]}
    readonly property int selectionDuration: {motion["selectionMs"]}
    readonly property int containerDuration: {motion["containerMs"]}
    readonly property int expressiveDuration: {motion["expressiveMs"]}
    readonly property int staggerDuration: {motion["staggerMs"]}
    readonly property int busyCycleDuration: {motion["busyCycleMs"]}
    readonly property int hoverDuration: productiveDuration
    readonly property int popupDuration: containerDuration
    readonly property int busyDuration: busyCycleDuration
    readonly property list<real> productiveEnterCurve: {json.dumps(curves["productiveEnter"])}
    readonly property list<real> standardCurve: {json.dumps(curves["standard"])}
    readonly property list<real> exitCurve: {json.dumps(curves["exit"])}
    readonly property list<real> expressiveCurve: {json.dumps(curves["expressive"])}
    readonly property int reducedMotionDuration: {reduced_motion["durationMs"]}
    readonly property bool reducedSpatialMotion: {str(reduced_motion["spatialMotion"]).lower()}
    readonly property bool reducedBusyIndicatorStatic: {str(reduced_motion["busyIndicatorStatic"]).lower()}
    readonly property bool reducedOpacityTransitions: {str(reduced_motion["opacityTransitions"]).lower()}
    readonly property int bodyWeight: {typography_roles["body"]["weight"]}
    readonly property int headingWeight: {typography_roles["sectionTitle"]["weight"]}
    readonly property int displayClockSize: {typography_roles["displayClock"]["pixelSize"]}
    readonly property int surfaceTitleSize: {typography_roles["surfaceTitle"]["pixelSize"]}
    readonly property int sectionTitleSize: {typography_roles["sectionTitle"]["pixelSize"]}
    readonly property int bodySize: {typography_roles["body"]["pixelSize"]}
    readonly property int controlLabelSize: {typography_roles["controlLabel"]["pixelSize"]}
    readonly property int metadataSize: {typography_roles["metadata"]["pixelSize"]}
    readonly property int microLabelSize: {typography_roles["microLabel"]["pixelSize"]}
    readonly property int brandTracking: {typography["brandTracking"]}
    readonly property string canonicalTokensJson: '{canonical_tokens(tokens)}'
}}
'''


def qml_motion_policy() -> str:
    return '''// SPDX-License-Identifier: MIT
// Generated by scripts/generate_design_system.py. Do not edit directly.
import QtQuick
import org.kde.kirigami as Kirigami

QtObject {
    readonly property real durationScale: Kirigami.Units.shortDuration <= 0
        ? 0
        : Kirigami.Units.shortDuration / 100.0
    readonly property bool reducedMotion: durationScale <= 0

    function duration(baseDuration) {
        return reducedMotion ? 0 : Math.max(1, Math.round(baseDuration * durationScale))
    }

    function segment(progress, start, end) {
        if (end <= start) {
            return progress >= end ? 1 : 0
        }
        return Math.max(0, Math.min(1, (progress - start) / (end - start)))
    }
}
'''


def brand_mark(tokens: dict[str, object]) -> str:
    colors = tokens["colors"]
    assert isinstance(colors, dict)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="192" height="144" viewBox="0 0 192 144">
  <title>NoxForge Kinetic Precision N/F mark</title>
  <g fill="none" stroke-linecap="square" stroke-linejoin="miter">
    <path d="M18 116L46 28l62 88 28-88h48M123 70h45"
          stroke="{colors['textPrimary']}" stroke-width="14"/>
    <path d="M47 30l59 84M136 28h48"
          stroke="{colors['accent']}" stroke-width="4"/>
  </g>
</svg>
'''


def monochrome_brand_mark(tokens: dict[str, object]) -> str:
    colors = tokens["colors"]
    assert isinstance(colors, dict)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="192" height="144" viewBox="0 0 192 144">
  <title>NoxForge Kinetic Precision monochrome N/F mark</title>
  <path d="M18 116L46 28l62 88 28-88h48M123 70h45"
        fill="none" stroke="{colors['textPrimary']}" stroke-width="14"
        stroke-linecap="square" stroke-linejoin="miter"/>
</svg>
'''


def brand_lockup(tokens: dict[str, object]) -> str:
    colors = tokens["colors"]
    assert isinstance(colors, dict)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="144" viewBox="0 0 600 144">
  <title>NoxForge Kinetic Precision horizontal lockup</title>
  <g fill="none" stroke-linecap="square" stroke-linejoin="miter">
    <path d="M18 116L46 28l62 88 28-88h48M123 70h45"
          stroke="{colors['textPrimary']}" stroke-width="14"/>
    <path d="M47 30l59 84M136 28h48"
          stroke="{colors['accent']}" stroke-width="4"/>
  </g>
  <g transform="translate(216 46)" fill="none" stroke="{colors['textPrimary']}"
     stroke-width="5" stroke-linecap="square" stroke-linejoin="miter">
    <path d="M0 52V0l28 52V0"/>
    <path d="M44 0h28v52H44z"/>
    <path d="M88 0l28 52M116 0L88 52"/>
    <path d="M132 52V0h30M132 25h24"/>
    <path d="M178 0h28v52h-28z"/>
    <path d="M222 52V0h28l8 8v14l-8 8h-28M244 30l16 22"/>
    <path d="M304 8l-8-8h-20v52h28V30h-14"/>
    <path d="M320 0h30M320 0v52h30M320 25h24"/>
  </g>
</svg>
'''


def color_scheme_for_palette(
    colors: dict[str, object], scheme_id: str, display_name: str
) -> str:
    roles = {
        "BackgroundAlternate": colors["surface"],
        "BackgroundNormal": colors["surfaceRaised"],
        "DecorationFocus": colors["accent"],
        "DecorationHover": colors["detailCyan"],
        "ForegroundActive": colors["accent"],
        "ForegroundInactive": colors["textSecondary"],
        "ForegroundLink": colors["detailCyan"],
        "ForegroundNegative": colors["negative"],
        "ForegroundNeutral": colors["neutral"],
        "ForegroundNormal": colors["textPrimary"],
        "ForegroundPositive": colors["accent"],
        "ForegroundVisited": colors["detailViolet"],
    }

    def section(name: str, background: str, alternate: str | None = None) -> str:
        section_roles = dict(roles)
        section_roles["BackgroundNormal"] = background
        section_roles["BackgroundAlternate"] = alternate or colors["surface"]
        body = "\n".join(f"{key}={rgb(str(value))}" for key, value in section_roles.items())
        return f"[{name}]\n{body}\n"

    return f'''# SPDX-FileCopyrightText: 2026 Loofi
# SPDX-License-Identifier: MIT

[ColorEffects:Disabled]
Color=70,79,86
ColorAmount=0
ColorEffect=0
ContrastAmount=0.55
ContrastEffect=1
IntensityAmount=0.1
IntensityEffect=2

[ColorEffects:Inactive]
ChangeSelectionColor=true
Color={rgb(str(colors["textSecondary"]))}
ColorAmount=0.025
ColorEffect=2
ContrastAmount=0.1
ContrastEffect=2
Enable=false
IntensityAmount=0
IntensityEffect=0

{section("Colors:Button", str(colors["surfaceRaised"]))}
{section("Colors:Complementary", str(colors["background"]))}
{section("Colors:Header", str(colors["surfaceRaised"]))}
{section("Colors:Header][Inactive", str(colors["background"]))}
{section("Colors:Selection", str(colors["surfaceSelected"]), str(colors["surfaceSelected"]))}
{section("Colors:Tooltip", str(colors["surfaceRaised"]))}
{section("Colors:View", str(colors["background"]))}
{section("Colors:Window", str(colors["surface"]), str(colors["surfaceRaised"]))}
[General]
ColorScheme={scheme_id}
Name={display_name}
shadeSortColumn=true

[KDE]
contrast=4

[WM]
activeBackground={rgb(str(colors["surface"]))}
activeBlend={rgb(str(colors["accent"]))}
activeForeground={rgb(str(colors["textPrimary"]))}
inactiveBackground={rgb(str(colors["background"]))}
inactiveBlend={rgb(str(colors["textSecondary"]))}
inactiveForeground={rgb(str(colors["textSecondary"]))}
'''


def color_scheme(tokens: dict[str, object]) -> str:
    colors = tokens["colors"]
    assert isinstance(colors, dict)
    return color_scheme_for_palette(colors, "NoxForgeDark", "NoxForge Dark")


def obsidian_color_scheme(tokens: dict[str, object]) -> str:
    base = tokens["colors"]
    variants = tokens["variants"]
    assert isinstance(base, dict) and isinstance(variants, dict)
    obsidian = variants["obsidian"]
    assert isinstance(obsidian, dict)
    palette = dict(base)
    palette.update(obsidian)
    return color_scheme_for_palette(palette, "NoxForgeObsidian", "NoxForge Obsidian")


def konsole_scheme(tokens: dict[str, object], variant: str) -> str:
    terminal = tokens["terminal"]
    assert isinstance(terminal, dict)
    backgrounds = terminal["backgrounds"]
    foreground = terminal["foreground"]
    ansi = terminal["ansi"]
    assert isinstance(backgrounds, dict)
    assert isinstance(foreground, dict)
    assert isinstance(ansi, dict)
    background = backgrounds[variant]
    assert isinstance(background, dict)
    names = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")
    lines = [
        "[General]",
        f"Description={'NoxForge' if variant == 'standard' else 'NoxForge Obsidian'}",
        "Opacity=1",
        "Blur=false",
        "ColorRandomization=false",
        "",
        "[Background]",
        f"Color={rgb(str(background['background']))}",
        "",
        "[BackgroundFaint]",
        f"Color={rgb(str(background['faint']))}",
        "",
        "[BackgroundIntense]",
        f"Color={rgb(str(background['intense']))}",
        "",
    ]
    for index, name in enumerate(names):
        value = ansi[name]
        assert isinstance(value, dict)
        lines.extend(
            [
                f"[Color{index}]",
                f"Color={rgb(str(value['normal']))}",
                "",
                f"[Color{index}Faint]",
                f"Color={rgb(str(value['faint']))}",
                "",
                f"[Color{index}Intense]",
                f"Color={rgb(str(value['intense']))}",
                "",
            ]
        )
    lines.extend(
        [
            "[Foreground]",
            f"Color={rgb(str(foreground['normal']))}",
            "",
            "[ForegroundFaint]",
            f"Color={rgb(str(foreground['faint']))}",
            "",
            "[ForegroundIntense]",
            f"Color={rgb(str(foreground['intense']))}",
            "",
        ]
    )
    return "\n".join(lines)


def gtk_theme_css(tokens: dict[str, object], variant: str = "standard", gtk_version: str = "3.0") -> str:
    colors = tokens["colors"]
    obsidian_colors = tokens["variants"]["obsidian"]
    bg = obsidian_colors["background"] if variant == "obsidian" else colors["background"]
    surface = obsidian_colors["surface"] if variant == "obsidian" else colors["surface"]
    surface_sunken = obsidian_colors["surfaceSunken"] if variant == "obsidian" else colors["surfaceSunken"]
    surface_raised = obsidian_colors["surfaceRaised"] if variant == "obsidian" else colors["surfaceRaised"]
    surface_hover = "#19242C" if variant == "obsidian" else colors["surfaceHover"]
    surface_selected = obsidian_colors["surfaceSelected"] if variant == "obsidian" else colors["surfaceSelected"]
    fg = colors["textPrimary"]
    fg_secondary = colors["textSecondary"]
    fg_disabled = colors["textDisabled"]
    accent = colors["accent"]
    accent_pressed = colors["accentPressed"]
    accent_ink = colors["accentInk"]
    border = colors["border"]
    border_strong = colors["borderStrong"]
    edge_highlight = colors["edgeHighlight"]
    cyan = colors["detailCyan"]
    violet = colors["detailViolet"]
    red = colors["negative"]
    amber = colors["neutral"]

    return f"""/* SPDX-License-Identifier: MIT */
/* Generated by scripts/generate_design_system.py for NoxForge {variant.capitalize()} GTK {gtk_version}. Do not edit directly. */

@define-color theme_bg_color {bg};
@define-color theme_fg_color {fg};
@define-color theme_base_color {surface};
@define-color theme_text_color {fg};
@define-color theme_selected_bg_color {accent};
@define-color theme_selected_fg_color {accent_ink};
@define-color theme_view_hover {surface_hover};
@define-color theme_view_active {surface_selected};
@define-color theme_border_color {border};
@define-color accent_color {accent};
@define-color accent_bg_color {accent};
@define-color accent_fg_color {accent_ink};
@define-color window_bg_color {bg};
@define-color window_fg_color {fg};
@define-color view_bg_color {surface};
@define-color view_fg_color {fg};
@define-color headerbar_bg_color {surface_sunken};
@define-color headerbar_fg_color {fg};
@define-color headerbar_border_color {border};
@define-color card_bg_color {surface_raised};
@define-color card_fg_color {fg};
@define-color card_border_color {border};
@define-color popover_bg_color {colors["surfaceOverlay"]};
@define-color popover_fg_color {fg};
@define-color destructive_color {red};
@define-color destructive_bg_color {red};
@define-color destructive_fg_color {accent_ink};
@define-color warning_color {amber};
@define-color warning_bg_color {amber};
@define-color warning_fg_color {accent_ink};
@define-color success_color {accent};
@define-color success_bg_color {accent};
@define-color success_fg_color {accent_ink};

/* Global application surfaces */
window, dialog {{
    background-color: {bg};
    color: {fg};
}}

headerbar {{
    background-color: {surface_sunken};
    border-bottom: 1px solid {border};
    color: {fg};
    padding: 4px 6px;
}}

/* Standard controls & buttons */
button {{
    background-color: {surface_raised};
    border: 1px solid {colors["outlineMuted"]};
    border-radius: 6px;
    color: {fg};
    padding: 4px 12px;
    transition: background-color 90ms ease-out, border-color 90ms ease-out;
}}

button:hover {{
    background-color: {surface_hover};
    border-color: {edge_highlight};
}}

button:active, button:checked {{
    background-color: {surface_sunken};
    border-color: {colors["outlineMuted"]};
}}

button:focus {{
    outline: 2px solid {accent};
    outline-offset: 1px;
}}

button:disabled {{
    opacity: 0.55;
    color: {fg_disabled};
}}

button.suggested-action {{
    background-color: {accent};
    border-color: {accent};
    color: {accent_ink};
    font-weight: 600;
}}

button.suggested-action:hover {{
    background-color: {accent_pressed};
    border-color: {accent_pressed};
}}

button.destructive-action {{
    background-color: {red};
    border-color: {red};
    color: {accent_ink};
    font-weight: 600;
}}

/* Text entry fields */
entry {{
    background-color: {surface_sunken};
    border: 1px solid {border};
    border-radius: 4px;
    color: {fg};
    padding: 4px 8px;
}}

entry:focus {{
    border-color: {accent};
    outline: 1px solid {accent};
}}

/* List views and item trees */
treeview, listview, row {{
    background-color: {surface};
    color: {fg};
}}

row:hover {{
    background-color: {surface_hover};
}}

row:selected {{
    background-color: {surface_selected};
    color: {fg};
    border-left: 3px solid {accent};
}}

/* Tabs / Notebook */
notebook > header.top > tab {{
    background-color: {surface_sunken};
    border: 1px solid {border};
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    color: {fg_secondary};
    padding: 4px 12px;
}}

notebook > header.top > tab:checked, notebook > header.top > tab:active {{
    background-color: {surface};
    color: {fg};
    border-top: 2px solid {accent};
}}

/* Scrollbars */
scrollbar slider {{
    background-color: {border};
    border-radius: 4px;
    min-width: 6px;
    min-height: 6px;
}}

scrollbar slider:hover {{
    background-color: {border_strong};
}}

/* Checkboxes and Radio buttons */
check, radio {{
    border: 1px solid {border_strong};
    border-radius: 4px;
    min-width: 16px;
    min-height: 16px;
}}

radio {{
    border-radius: 50%;
}}

check:checked, radio:checked {{
    background-color: {accent};
    border-color: {accent};
    color: {accent_ink};
}}

/* Tooltips */
tooltip {{
    background-color: {colors["surfaceOverlay"]};
    border: 1px solid {border_strong};
    border-radius: 4px;
    color: {fg};
    padding: 4px 8px;
}}
"""


def gtk_index_theme(variant: str = "standard") -> str:
    name = "NoxForgeObsidian" if variant == "obsidian" else "NoxForge"
    comment = (
        "NoxForge Obsidian OLED True-Black theme"
        if variant == "obsidian"
        else "NoxForge Graphite and Electric Lime theme"
    )
    return f"""[Desktop Entry]
Type=X-GNOME-Metatheme
Name={name}
Comment={comment}
Encoding=UTF-8

[X-GNOME-Metatheme]
GtkTheme={name}
MetacityTheme={name}
IconTheme=NoxForge
CursorTheme=NoxForge-Cursors
ButtonLayout=close,minimize,maximize:
"""


def kate_syntax_theme(tokens: dict[str, object], variant: str = "standard") -> str:
    syntax = tokens["syntax"][variant]
    colors = tokens["colors"]
    obsidian_colors = tokens["variants"]["obsidian"]
    bg = obsidian_colors["background"] if variant == "obsidian" else colors["background"]
    surface = obsidian_colors["surface"] if variant == "obsidian" else colors["surface"]
    surface_sunken = obsidian_colors["surfaceSunken"] if variant == "obsidian" else colors["surfaceSunken"]
    surface_raised = obsidian_colors["surfaceRaised"] if variant == "obsidian" else colors["surfaceRaised"]
    surface_selected = obsidian_colors["surfaceSelected"] if variant == "obsidian" else colors["surfaceSelected"]
    name = "NoxForgeObsidian" if variant == "obsidian" else "NoxForge"

    theme_data = {
        "metadata": {
            "name": name,
            "revision": 1,
        },
        "editor-colors": {
            "BackgroundColor": bg,
            "CodeFolding": colors["border"],
            "CurrentLine": surface,
            "CurrentLineNumber": colors["accent"],
            "IconBorder": surface_sunken,
            "IndentationLine": colors["border"],
            "LineNumbers": colors["textDisabled"],
            "MarkBookmark": colors["detailCyan"],
            "MarkBreakpointActive": colors["negative"],
            "MarkBreakpointDisabled": colors["textDisabled"],
            "MarkBreakpointReached": colors["neutral"],
            "MarkError": colors["negative"],
            "MarkExecution": colors["detailCyan"],
            "MarkWarning": colors["neutral"],
            "ModifiedLines": colors["neutral"],
            "ReplaceHighlight": colors["accentSoft"],
            "SavedLines": colors["accent"],
            "SearchHighlight": surface_selected,
            "Separator": colors["border"],
            "SpellingMistakeLine": colors["negative"],
            "TabMarker": colors["outlineMuted"],
            "TemplateBackground": surface_raised,
            "TemplateFocusedEditablePlaceholder": colors["accentSoft"],
            "TemplateReadOnlyPlaceholder": surface_sunken,
            "TextSelection": surface_selected,
            "WordWrapMarker": colors["border"],
        },
        "text-styles": {
            "Alert": {"bold": True, "selected-text-color": syntax["error"], "text-color": syntax["error"]},
            "Annotation": {"selected-text-color": syntax["type"], "text-color": syntax["type"]},
            "Attribute": {"selected-text-color": syntax["string"], "text-color": syntax["string"]},
            "BaseN": {"selected-text-color": syntax["number"], "text-color": syntax["number"]},
            "BuiltIn": {"selected-text-color": syntax["string"], "text-color": syntax["string"]},
            "Char": {"selected-text-color": syntax["string"], "text-color": syntax["string"]},
            "Comment": {"italic": True, "selected-text-color": syntax["comment"], "text-color": syntax["comment"]},
            "CommentVar": {"selected-text-color": colors["textSecondary"], "text-color": colors["textSecondary"]},
            "Constant": {"bold": True, "selected-text-color": syntax["number"], "text-color": syntax["number"]},
            "ControlFlow": {"bold": True, "selected-text-color": syntax["keyword"], "text-color": syntax["keyword"]},
            "DataType": {"selected-text-color": syntax["type"], "text-color": syntax["type"]},
            "DecVal": {"selected-text-color": syntax["number"], "text-color": syntax["number"]},
            "Documentation": {"selected-text-color": colors["textSecondary"], "text-color": colors["textSecondary"]},
            "Error": {"selected-text-color": syntax["error"], "text-color": syntax["error"], "underline": True},
            "Extension": {"selected-text-color": syntax["string"], "text-color": syntax["string"]},
            "Float": {"selected-text-color": syntax["number"], "text-color": syntax["number"]},
            "Function": {"selected-text-color": syntax["function"], "text-color": syntax["function"]},
            "Import": {"selected-text-color": syntax["keyword"], "text-color": syntax["keyword"]},
            "Information": {"selected-text-color": syntax["string"], "text-color": syntax["string"]},
            "Keyword": {"bold": True, "selected-text-color": syntax["keyword"], "text-color": syntax["keyword"]},
            "Normal": {"selected-text-color": syntax["function"], "text-color": syntax["function"]},
            "Operator": {"selected-text-color": syntax["operator"], "text-color": syntax["operator"]},
            "Others": {"selected-text-color": syntax["string"], "text-color": syntax["string"]},
            "Preprocessor": {"selected-text-color": syntax["type"], "text-color": syntax["type"]},
            "RegionMarker": {"selected-text-color": colors["outlineMuted"], "text-color": colors["outlineMuted"]},
            "SpecialChar": {"selected-text-color": syntax["string"], "text-color": syntax["string"]},
            "SpecialString": {"selected-text-color": syntax["string"], "text-color": syntax["string"]},
            "String": {"selected-text-color": syntax["string"], "text-color": syntax["string"]},
            "Variable": {"selected-text-color": syntax["variable"], "text-color": syntax["variable"]},
            "VerbatimString": {"selected-text-color": syntax["string"], "text-color": syntax["string"]},
            "Warning": {"selected-text-color": syntax["number"], "text-color": syntax["number"]},
        },
    }
    return json.dumps(theme_data, indent=2) + "\n"


def vscode_theme(tokens: dict[str, object], variant: str = "standard") -> str:
    syntax = tokens["syntax"][variant]
    colors = tokens["colors"]
    obsidian_colors = tokens["variants"]["obsidian"]
    bg = obsidian_colors["background"] if variant == "obsidian" else colors["background"]
    surface = obsidian_colors["surface"] if variant == "obsidian" else colors["surface"]
    surface_sunken = obsidian_colors["surfaceSunken"] if variant == "obsidian" else colors["surfaceSunken"]
    surface_raised = obsidian_colors["surfaceRaised"] if variant == "obsidian" else colors["surfaceRaised"]
    surface_selected = obsidian_colors["surfaceSelected"] if variant == "obsidian" else colors["surfaceSelected"]
    name = "NoxForge Obsidian" if variant == "obsidian" else "NoxForge Dark"

    theme_data = {
        "name": name,
        "type": "dark",
        "colors": {
            "editor.background": bg,
            "editor.foreground": colors["textPrimary"],
            "editor.lineHighlightBackground": surface,
            "editor.selectionBackground": surface_selected,
            "editorCursor.foreground": colors["accent"],
            "editorWhitespace.foreground": colors["outlineMuted"],
            "editorIndentGuide.background": colors["border"],
            "editorIndentGuide.activeBackground": colors["borderStrong"],
            "editorLineNumber.foreground": colors["textDisabled"],
            "editorLineNumber.activeForeground": colors["accent"],
            "sideBar.background": surface_sunken,
            "sideBar.foreground": colors["textSecondary"],
            "sideBar.border": colors["border"],
            "sideBarTitle.foreground": colors["textPrimary"],
            "sideBarSectionHeader.background": surface,
            "sideBarSectionHeader.foreground": colors["textPrimary"],
            "activityBar.background": bg,
            "activityBar.foreground": colors["accent"],
            "activityBar.inactiveForeground": colors["textDisabled"],
            "activityBar.border": colors["border"],
            "statusBar.background": surface_sunken,
            "statusBar.foreground": colors["textSecondary"],
            "statusBar.border": colors["border"],
            "statusBarItem.prominentBackground": colors["accent"],
            "statusBarItem.prominentForeground": colors["accentInk"],
            "titleBar.activeBackground": surface_sunken,
            "titleBar.activeForeground": colors["textPrimary"],
            "titleBar.border": colors["border"],
            "tab.activeBackground": surface,
            "tab.activeForeground": colors["textPrimary"],
            "tab.activeBorderTop": colors["accent"],
            "tab.inactiveBackground": surface_sunken,
            "tab.inactiveForeground": colors["textSecondary"],
            "tab.border": colors["border"],
            "input.background": surface_sunken,
            "input.foreground": colors["textPrimary"],
            "input.border": colors["border"],
            "inputOption.activeBorder": colors["accent"],
            "dropdown.background": surface_raised,
            "dropdown.foreground": colors["textPrimary"],
            "dropdown.border": colors["border"],
            "button.background": surface_raised,
            "button.foreground": colors["textPrimary"],
            "button.hoverBackground": colors["surfaceHover"],
            "terminal.background": bg,
            "terminal.foreground": colors["textPrimary"],
            "terminal.ansiBlack": tokens["terminal"]["ansi"]["black"]["normal"],
            "terminal.ansiRed": tokens["terminal"]["ansi"]["red"]["normal"],
            "terminal.ansiGreen": tokens["terminal"]["ansi"]["green"]["normal"],
            "terminal.ansiYellow": tokens["terminal"]["ansi"]["yellow"]["normal"],
            "terminal.ansiBlue": tokens["terminal"]["ansi"]["blue"]["normal"],
            "terminal.ansiMagenta": tokens["terminal"]["ansi"]["magenta"]["normal"],
            "terminal.ansiCyan": tokens["terminal"]["ansi"]["cyan"]["normal"],
            "terminal.ansiWhite": tokens["terminal"]["ansi"]["white"]["normal"],
            "terminal.ansiBrightBlack": tokens["terminal"]["ansi"]["black"]["faint"],
            "terminal.ansiBrightRed": tokens["terminal"]["ansi"]["red"]["faint"],
            "terminal.ansiBrightGreen": tokens["terminal"]["ansi"]["green"]["faint"],
            "terminal.ansiBrightYellow": tokens["terminal"]["ansi"]["yellow"]["faint"],
            "terminal.ansiBrightBlue": tokens["terminal"]["ansi"]["blue"]["faint"],
            "terminal.ansiBrightMagenta": tokens["terminal"]["ansi"]["magenta"]["faint"],
            "terminal.ansiBrightCyan": tokens["terminal"]["ansi"]["cyan"]["faint"],
            "terminal.ansiBrightWhite": tokens["terminal"]["ansi"]["white"]["intense"],
        },
        "tokenColors": [
            {
                "scope": ["comment", "punctuation.definition.comment"],
                "settings": {
                    "foreground": syntax["comment"],
                    "fontStyle": "italic",
                },
            },
            {
                "scope": ["keyword", "storage.type", "storage.modifier", "keyword.control"],
                "settings": {
                    "foreground": syntax["keyword"],
                    "fontStyle": "bold",
                },
            },
            {
                "scope": ["string", "punctuation.definition.string"],
                "settings": {
                    "foreground": syntax["string"],
                },
            },
            {
                "scope": ["entity.name.function", "support.function", "meta.function-call"],
                "settings": {
                    "foreground": syntax["function"],
                },
            },
            {
                "scope": ["entity.name.type", "entity.name.class", "support.type", "support.class"],
                "settings": {
                    "foreground": syntax["type"],
                },
            },
            {
                "scope": ["constant.numeric", "constant.language"],
                "settings": {
                    "foreground": syntax["number"],
                },
            },
            {
                "scope": ["keyword.operator", "punctuation.separator"],
                "settings": {
                    "foreground": syntax["operator"],
                },
            },
            {
                "scope": ["variable", "entity.name.variable"],
                "settings": {
                    "foreground": syntax["variable"],
                },
            },
            {
                "scope": ["invalid", "invalid.illegal"],
                "settings": {
                    "foreground": syntax["error"],
                },
            },
        ],
    }
    return json.dumps(theme_data, indent=2) + "\n"


def vscode_package_json(tokens: dict[str, object]) -> str:
    version = tokens["version"]
    assert isinstance(version, str)
    manifest = {
        "name": "noxforge-theme",
        "displayName": "NoxForge Theme",
        "description": "NoxForge Graphite, Electric Lime and Obsidian True-Black theme for VS Code and Cursor.",
        "version": version,
        "publisher": "loofiboss",
        "engines": {
            "vscode": "^1.74.0",
        },
        "categories": [
            "Themes",
        ],
        "contributes": {
            "themes": [
                {
                    "label": "NoxForge Dark",
                    "uiTheme": "vs-dark",
                    "path": "./themes/noxforge-dark-color-theme.json",
                },
                {
                    "label": "NoxForge Obsidian",
                    "uiTheme": "vs-dark",
                    "path": "./themes/noxforge-obsidian-color-theme.json",
                },
            ],
        },
    }
    return json.dumps(manifest, indent=2) + "\n"


def ghostty_theme(tokens: dict[str, object], variant: str = "standard") -> str:
    ansi = tokens["terminal"]["ansi"]
    bg = tokens["terminal"]["backgrounds"][variant]["background"]
    fg = tokens["terminal"]["foreground"]["normal"]
    accent = tokens["colors"]["accent"]
    surface_selected = (
        tokens["variants"]["obsidian"]["surfaceSelected"]
        if variant == "obsidian"
        else tokens["colors"]["surfaceSelected"]
    )
    return f"""# SPDX-License-Identifier: MIT
# Generated by scripts/generate_design_system.py for NoxForge {variant.capitalize()} Ghostty.
background = {bg}
foreground = {fg}
cursor-color = {accent}
cursor-text = {bg}
selection-background = {surface_selected}
selection-foreground = {fg}
palette = 0={ansi["black"]["normal"]}
palette = 1={ansi["red"]["normal"]}
palette = 2={ansi["green"]["normal"]}
palette = 3={ansi["yellow"]["normal"]}
palette = 4={ansi["blue"]["normal"]}
palette = 5={ansi["magenta"]["normal"]}
palette = 6={ansi["cyan"]["normal"]}
palette = 7={ansi["white"]["normal"]}
palette = 8={ansi["black"]["faint"]}
palette = 9={ansi["red"]["faint"]}
palette = 10={ansi["green"]["faint"]}
palette = 11={ansi["yellow"]["faint"]}
palette = 12={ansi["blue"]["faint"]}
palette = 13={ansi["magenta"]["faint"]}
palette = 14={ansi["cyan"]["faint"]}
palette = 15={ansi["white"]["intense"]}
"""


def alacritty_theme(tokens: dict[str, object], variant: str = "standard") -> str:
    ansi = tokens["terminal"]["ansi"]
    bg = tokens["terminal"]["backgrounds"][variant]["background"]
    fg = tokens["terminal"]["foreground"]["normal"]
    accent = tokens["colors"]["accent"]
    surface_selected = (
        tokens["variants"]["obsidian"]["surfaceSelected"]
        if variant == "obsidian"
        else tokens["colors"]["surfaceSelected"]
    )
    return f"""# SPDX-License-Identifier: MIT
# Generated by scripts/generate_design_system.py for NoxForge {variant.capitalize()} Alacritty.

[colors.primary]
background = "{bg}"
foreground = "{fg}"

[colors.cursor]
text = "{bg}"
cursor = "{accent}"

[colors.selection]
text = "{fg}"
background = "{surface_selected}"

[colors.normal]
black = "{ansi["black"]["normal"]}"
red = "{ansi["red"]["normal"]}"
green = "{ansi["green"]["normal"]}"
yellow = "{ansi["yellow"]["normal"]}"
blue = "{ansi["blue"]["normal"]}"
magenta = "{ansi["magenta"]["normal"]}"
cyan = "{ansi["cyan"]["normal"]}"
white = "{ansi["white"]["normal"]}"

[colors.bright]
black = "{ansi["black"]["faint"]}"
red = "{ansi["red"]["faint"]}"
green = "{ansi["green"]["faint"]}"
yellow = "{ansi["yellow"]["faint"]}"
blue = "{ansi["blue"]["faint"]}"
magenta = "{ansi["magenta"]["faint"]}"
cyan = "{ansi["cyan"]["faint"]}"
white = "{ansi["white"]["intense"]}"
"""


def kitty_theme(tokens: dict[str, object], variant: str = "standard") -> str:
    ansi = tokens["terminal"]["ansi"]
    bg = tokens["terminal"]["backgrounds"][variant]["background"]
    fg = tokens["terminal"]["foreground"]["normal"]
    accent = tokens["colors"]["accent"]
    surface_selected = (
        tokens["variants"]["obsidian"]["surfaceSelected"]
        if variant == "obsidian"
        else tokens["colors"]["surfaceSelected"]
    )
    return f"""# SPDX-License-Identifier: MIT
# Generated by scripts/generate_design_system.py for NoxForge {variant.capitalize()} Kitty.

background {bg}
foreground {fg}
cursor {accent}
cursor_text_color {bg}
selection_background {surface_selected}
selection_foreground {fg}

color0 {ansi["black"]["normal"]}
color1 {ansi["red"]["normal"]}
color2 {ansi["green"]["normal"]}
color3 {ansi["yellow"]["normal"]}
color4 {ansi["blue"]["normal"]}
color5 {ansi["magenta"]["normal"]}
color6 {ansi["cyan"]["normal"]}
color7 {ansi["white"]["normal"]}

color8 {ansi["black"]["faint"]}
color9 {ansi["red"]["faint"]}
color10 {ansi["green"]["faint"]}
color11 {ansi["yellow"]["faint"]}
color12 {ansi["blue"]["faint"]}
color13 {ansi["magenta"]["faint"]}
color14 {ansi["cyan"]["faint"]}
color15 {ansi["white"]["intense"]}
"""


def foot_theme(tokens: dict[str, object], variant: str = "standard") -> str:
    ansi = tokens["terminal"]["ansi"]
    bg = tokens["terminal"]["backgrounds"][variant]["background"].lstrip("#")
    fg = tokens["terminal"]["foreground"]["normal"].lstrip("#")
    accent = tokens["colors"]["accent"].lstrip("#")
    surface_selected = (
        tokens["variants"]["obsidian"]["surfaceSelected"]
        if variant == "obsidian"
        else tokens["colors"]["surfaceSelected"]
    ).lstrip("#")
    return f"""# SPDX-License-Identifier: MIT
# Generated by scripts/generate_design_system.py for NoxForge {variant.capitalize()} Foot.

[colors]
background={bg}
foreground={fg}
regular0={ansi["black"]["normal"].lstrip("#")}
regular1={ansi["red"]["normal"].lstrip("#")}
regular2={ansi["green"]["normal"].lstrip("#")}
regular3={ansi["yellow"]["normal"].lstrip("#")}
regular4={ansi["blue"]["normal"].lstrip("#")}
regular5={ansi["magenta"]["normal"].lstrip("#")}
regular6={ansi["cyan"]["normal"].lstrip("#")}
regular7={ansi["white"]["normal"].lstrip("#")}
bright0={ansi["black"]["faint"].lstrip("#")}
bright1={ansi["red"]["faint"].lstrip("#")}
bright2={ansi["green"]["faint"].lstrip("#")}
bright3={ansi["yellow"]["faint"].lstrip("#")}
bright4={ansi["blue"]["faint"].lstrip("#")}
bright5={ansi["magenta"]["faint"].lstrip("#")}
bright6={ansi["cyan"]["faint"].lstrip("#")}
bright7={ansi["white"]["intense"].lstrip("#")}
selection-background={surface_selected}
selection-foreground={fg}
"""


def neovim_theme(tokens: dict[str, object], variant: str = "standard") -> str:
    colors = (
        tokens["colorsObsidian"]
        if variant == "obsidian" and "colorsObsidian" in tokens
        else tokens["colors"]
    )
    bg = tokens["terminal"]["backgrounds"][variant]["background"]
    fg = colors["textPrimary"]
    fg_sec = colors["textSecondary"]
    fg_dis = colors["textDisabled"]
    accent = colors["accent"]
    accent_soft = colors["accentSoft"]
    surface = colors["surface"]
    sunken = colors["surfaceSunken"]
    border = colors["border"]
    border_strong = colors["borderStrong"]
    cyan = colors["detailCyan"]
    violet = colors["detailViolet"]
    negative = colors["negative"]
    warning = colors["neutral"]
    syntax = tokens["syntax"][variant]
    colors_name = "noxforge_obsidian" if variant == "obsidian" else "noxforge"

    return f"""-- SPDX-License-Identifier: MIT
-- Generated by scripts/generate_design_system.py for NoxForge {variant.capitalize()} Neovim.
vim.cmd("highlight clear")
if vim.fn.exists("syntax_on") == 1 then
  vim.cmd("syntax reset")
end

vim.g.colors_name = "{colors_name}"

local colors = {{
  bg = "{bg}",
  sunken = "{sunken}",
  surface = "{surface}",
  border = "{border}",
  border_strong = "{border_strong}",
  fg = "{fg}",
  fg_sec = "{fg_sec}",
  fg_dis = "{fg_dis}",
  accent = "{accent}",
  accent_soft = "{accent_soft}",
  cyan = "{cyan}",
  violet = "{violet}",
  negative = "{negative}",
  warning = "{warning}",
  keyword = "{syntax['keyword']}",
  func = "{syntax['function']}",
  str = "{syntax['string']}",
  type = "{syntax['type']}",
  num = "{syntax['number']}",
  comment = "{syntax['comment']}",
  op = "{syntax['operator']}",
}}

local highlights = {{
  Normal = {{ fg = colors.fg, bg = colors.bg }},
  NormalFloat = {{ fg = colors.fg, bg = colors.surface }},
  FloatBorder = {{ fg = colors.border_strong, bg = colors.surface }},
  ColorColumn = {{ bg = colors.sunken }},
  Cursor = {{ fg = colors.bg, bg = colors.accent }},
  CursorLine = {{ bg = colors.sunken }},
  CursorColumn = {{ bg = colors.sunken }},
  LineNr = {{ fg = colors.fg_dis }},
  CursorLineNr = {{ fg = colors.accent, bold = true }},
  VertSplit = {{ fg = colors.border, bg = colors.bg }},
  WinSeparator = {{ fg = colors.border, bg = colors.bg }},
  StatusLine = {{ fg = colors.fg, bg = colors.surface }},
  StatusLineNC = {{ fg = colors.fg_sec, bg = colors.sunken }},
  Pmenu = {{ fg = colors.fg, bg = colors.surface }},
  PmenuSel = {{ fg = colors.fg, bg = colors.accent_soft, bold = true }},
  PmenuSbar = {{ bg = colors.sunken }},
  PmenuThumb = {{ bg = colors.border_strong }},
  Visual = {{ bg = colors.accent_soft }},
  Search = {{ fg = colors.bg, bg = colors.accent }},
  IncSearch = {{ fg = colors.bg, bg = colors.accent }},
  MatchParen = {{ fg = colors.accent, underline = true }},
  Comment = {{ fg = colors.comment, italic = true }},
  Constant = {{ fg = colors.num }},
  String = {{ fg = colors.str }},
  Character = {{ fg = colors.str }},
  Number = {{ fg = colors.num }},
  Boolean = {{ fg = colors.accent, bold = true }},
  Float = {{ fg = colors.num }},
  Identifier = {{ fg = colors.fg }},
  Function = {{ fg = colors.func }},
  Statement = {{ fg = colors.keyword, bold = true }},
  Conditional = {{ fg = colors.keyword, bold = true }},
  Repeat = {{ fg = colors.keyword, bold = true }},
  Label = {{ fg = colors.keyword }},
  Operator = {{ fg = colors.op }},
  Keyword = {{ fg = colors.keyword, bold = true }},
  Exception = {{ fg = colors.negative, bold = true }},
  PreProc = {{ fg = colors.violet }},
  Type = {{ fg = colors.type }},
  Special = {{ fg = colors.cyan }},
  Underlined = {{ underline = true }},
  Error = {{ fg = colors.negative, bold = true }},
  Todo = {{ fg = colors.accent, bold = true }},
  DiagnosticError = {{ fg = colors.negative }},
  DiagnosticWarn = {{ fg = colors.warning }},
  DiagnosticInfo = {{ fg = colors.cyan }},
  DiagnosticHint = {{ fg = colors.accent }},
}}

for group, opts in pairs(highlights) do
  vim.api.nvim_set_hl(0, group, opts)
end
"""


def helix_theme(tokens: dict[str, object], variant: str = "standard") -> str:
    colors = (
        tokens["colorsObsidian"]
        if variant == "obsidian" and "colorsObsidian" in tokens
        else tokens["colors"]
    )
    bg = tokens["terminal"]["backgrounds"][variant]["background"]
    fg = colors["textPrimary"]
    fg_sec = colors["textSecondary"]
    fg_dis = colors["textDisabled"]
    accent = colors["accent"]
    accent_soft = colors["accentSoft"]
    surface = colors["surface"]
    sunken = colors["surfaceSunken"]
    border = colors["border"]
    cyan = colors["detailCyan"]
    violet = colors["detailViolet"]
    negative = colors["negative"]
    warning = colors["neutral"]
    syntax = tokens["syntax"][variant]

    return f"""# SPDX-License-Identifier: MIT
# Generated by scripts/generate_design_system.py for NoxForge {variant.capitalize()} Helix.

"attribute" = "{syntax['type']}"
"keyword" = {{ fg = "{syntax['keyword']}", modifiers = ["bold"] }}
"keyword.directive" = "{syntax['type']}"
"namespace" = "{syntax['type']}"
"punctuation" = "{syntax['operator']}"
"punctuation.delimiter" = "{syntax['operator']}"
"operator" = "{syntax['operator']}"
"special" = "{syntax['string']}"
"variable" = "{syntax['variable']}"
"variable.builtin" = "{accent}"
"variable.parameter" = "{syntax['variable']}"
"variable.other.member" = "{syntax['variable']}"
"type" = "{syntax['type']}"
"type.builtin" = "{syntax['type']}"
"constructor" = "{syntax['function']}"
"function" = "{syntax['function']}"
"function.builtin" = "{syntax['function']}"
"function.macro" = "{syntax['function']}"
"tag" = "{syntax['keyword']}"
"comment" = {{ fg = "{syntax['comment']}", modifiers = ["italic"] }}
"string" = "{syntax['string']}"
"constant" = "{syntax['number']}"
"constant.numeric" = "{syntax['number']}"
"constant.builtin" = "{syntax['number']}"
"constant.character.escape" = "{syntax['string']}"

"ui.background" = {{ bg = "{bg}" }}
"ui.cursor" = {{ fg = "{bg}", bg = "{accent}" }}
"ui.cursor.match" = {{ fg = "{accent}", underline = {{ style = "line" }} }}
"ui.cursor.primary" = {{ fg = "{bg}", bg = "{accent}" }}
"ui.gutter" = {{ bg = "{bg}" }}
"ui.linenr" = {{ fg = "{fg_dis}" }}
"ui.linenr.selected" = {{ fg = "{accent}", modifiers = ["bold"] }}
"ui.statusline" = {{ fg = "{fg}", bg = "{surface}" }}
"ui.statusline.inactive" = {{ fg = "{fg_sec}", bg = "{sunken}" }}
"ui.popup" = {{ fg = "{fg}", bg = "{surface}" }}
"ui.window" = {{ fg = "{border}" }}
"ui.help" = {{ fg = "{fg}", bg = "{surface}" }}
"ui.text" = "{fg}"
"ui.text.focus" = "{fg}"
"ui.selection" = {{ bg = "{accent_soft}" }}
"ui.selection.primary" = {{ bg = "{accent_soft}" }}
"ui.menu" = {{ fg = "{fg}", bg = "{surface}" }}
"ui.menu.selected" = {{ fg = "{fg}", bg = "{accent_soft}", modifiers = ["bold"] }}

"diagnostic.error" = {{ fg = "{negative}" }}
"diagnostic.warning" = {{ fg = "{warning}" }}
"diagnostic.info" = {{ fg = "{cyan}" }}
"diagnostic.hint" = {{ fg = "{accent}" }}

"warning" = "{warning}"
"error" = "{negative}"
"info" = "{cyan}"
"hint" = "{accent}"
"""


def outputs(tokens: dict[str, object]) -> dict[Path, str]:
    colors_text = color_scheme(tokens)
    obsidian_colors_text = obsidian_color_scheme(tokens)
    generated = {
        ROOT / "src/style/noxforgepalette.h": cpp_header(tokens),
        ROOT / "color-schemes/NoxForgeDark.colors": colors_text,
        ROOT / f"plasma/desktoptheme/{THEME_ID}/colors": colors_text,
        ROOT / f"plasma/desktoptheme/{THEME_OBSIDIAN_ID}/colors": obsidian_colors_text,
        ROOT / "color-schemes/NoxForgeObsidian.colors": obsidian_colors_text,
        ROOT / "konsole/NoxForge.colorscheme": konsole_scheme(tokens, "standard"),
        ROOT / "konsole/NoxForgeObsidian.colorscheme": konsole_scheme(tokens, "obsidian"),
        ROOT / "themes/NoxForge/gtk-3.0/gtk.css": gtk_theme_css(tokens, "standard", "3.0"),
        ROOT / "themes/NoxForge/gtk-4.0/gtk.css": gtk_theme_css(tokens, "standard", "4.0"),
        ROOT / "themes/NoxForge/index.theme": gtk_index_theme("standard"),
        ROOT / "themes/NoxForgeObsidian/gtk-3.0/gtk.css": gtk_theme_css(tokens, "obsidian", "3.0"),
        ROOT / "themes/NoxForgeObsidian/gtk-4.0/gtk.css": gtk_theme_css(tokens, "obsidian", "4.0"),
        ROOT / "themes/NoxForgeObsidian/index.theme": gtk_index_theme("obsidian"),
        ROOT / "syntax/kate/NoxForge.theme": kate_syntax_theme(tokens, "standard"),
        ROOT / "syntax/kate/NoxForgeObsidian.theme": kate_syntax_theme(tokens, "obsidian"),
        ROOT / "editors/vscode/package.json": vscode_package_json(tokens),
        ROOT / "editors/vscode/themes/noxforge-dark-color-theme.json": vscode_theme(tokens, "standard"),
        ROOT / "editors/vscode/themes/noxforge-obsidian-color-theme.json": vscode_theme(tokens, "obsidian"),
        ROOT / "editors/neovim/colors/noxforge.lua": neovim_theme(tokens, "standard"),
        ROOT / "editors/neovim/colors/noxforge_obsidian.lua": neovim_theme(tokens, "obsidian"),
        ROOT / "editors/helix/themes/noxforge.toml": helix_theme(tokens, "standard"),
        ROOT / "editors/helix/themes/noxforge_obsidian.toml": helix_theme(tokens, "obsidian"),
        ROOT / "terminals/ghostty/noxforge": ghostty_theme(tokens, "standard"),
        ROOT / "terminals/ghostty/noxforge-obsidian": ghostty_theme(tokens, "obsidian"),
        ROOT / "terminals/alacritty/noxforge.toml": alacritty_theme(tokens, "standard"),
        ROOT / "terminals/alacritty/noxforge-obsidian.toml": alacritty_theme(tokens, "obsidian"),
        ROOT / "terminals/kitty/noxforge.conf": kitty_theme(tokens, "standard"),
        ROOT / "terminals/kitty/noxforge-obsidian.conf": kitty_theme(tokens, "obsidian"),
        ROOT / "terminals/foot/noxforge.ini": foot_theme(tokens, "standard"),
        ROOT / "terminals/foot/noxforge-obsidian.ini": foot_theme(tokens, "obsidian"),
    }
    generated.update({path: qml_tokens(tokens, variant) for path, variant in QML_TARGETS})
    motion_policy = qml_motion_policy()
    generated.update({path: motion_policy for path in MOTION_POLICY_TARGETS})
    mark = brand_mark(tokens)
    generated.update({path: mark for path in MARK_TARGETS})
    generated[MONO_MARK_TARGET] = monochrome_brand_mark(tokens)
    lockup = brand_lockup(tokens)
    generated.update({path: lockup for path in LOCKUP_TARGETS})
    return generated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when generated files drift")
    args = parser.parse_args()
    generated = outputs(load_tokens())
    drift: list[str] = []
    for path, content in generated.items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                drift.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    if drift:
        print("generated design consumers are stale: " + ", ".join(drift), file=sys.stderr)
        return 1
    if not args.check:
        print(f"Generated {len(generated)} design-system consumers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
