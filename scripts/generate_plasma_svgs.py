#!/usr/bin/env python3
"""Generate original NoxForge Plasma Style SVG assets."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop"
TOKENS = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))
COLORS = TOKENS["colors"]
GLYPHS = json.loads((ROOT / "design/plasma-glyphs.json").read_text(encoding="utf-8"))
CHECK_MODE = False
DRIFT: list[str] = []

SVG_HEADER = f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="480" viewBox="0 0 640 480">
  <defs>
    <style id="current-color-scheme" type="text/css"><![CDATA[
      .ColorScheme-Background {{ color: {COLORS['surface']}; }}
      .ColorScheme-ViewBackground {{ color: {COLORS['background']}; }}
      .ColorScheme-ButtonBackground {{ color: {COLORS['surfaceRaised']}; }}
      .ColorScheme-Text {{ color: {COLORS['textPrimary']}; }}
      .ColorScheme-Highlight {{ color: {COLORS['accent']}; }}
      .ColorScheme-ViewHover {{ color: {COLORS['detailCyan']}; }}
      .ColorScheme-ButtonHover {{ color: {COLORS['detailCyan']}; }}
      .ColorScheme-ButtonFocus {{ color: {COLORS['accent']}; }}
      .NoxForge-Selected {{ color: {COLORS['surfaceSelected']}; }}
      .NoxForge-Border {{ color: {COLORS['border']}; }}
    ]]></style>
  </defs>
"""


@dataclass(frozen=True)
class Paint:
    css_class: str
    opacity: float = 1.0


def element_id(prefix: str, suffix: str) -> str:
    return f"{prefix}-{suffix}" if prefix else suffix


def paint_attrs(paint: Paint) -> str:
    return f'class="{paint.css_class}" fill="currentColor" fill-opacity="{paint.opacity:g}"'


def frame(prefix: str, x: int, y: int, paint: Paint, *, notch: bool = False, marker: bool = False) -> str:
    """Return a self-contained 6/12/6 nine-slice frame."""
    attrs = paint_attrs(paint)
    top_left = (
        f'<path id="{element_id(prefix, "topleft")}" d="M{x + 4} {y}H{x + 6}V{y + 6}H{x}V{y + 4}Z" {attrs}/>'
        if notch
        else f'<path id="{element_id(prefix, "topleft")}" d="M{x + 6} {y}V{y + 6}H{x}V{y + 6}A6 6 0 0 1 {x + 6} {y}Z" {attrs}/>'
    )
    left = f'<rect id="{element_id(prefix, "left")}" x="{x}" y="{y + 6}" width="6" height="12" {attrs}/>'
    if marker:
        left = (
            f'<g id="{element_id(prefix, "left")}"><rect x="{x}" y="{y + 6}" width="6" height="12" {attrs}/>'
            f'<rect x="{x}" y="{y + 7}" width="3" height="10" class="ColorScheme-Highlight" fill="currentColor"/></g>'
        )
    return "\n".join(
        [
            top_left,
            f'<rect id="{element_id(prefix, "top")}" x="{x + 6}" y="{y}" width="12" height="6" {attrs}/>',
            f'<path id="{element_id(prefix, "topright")}" d="M{x + 18} {y}A6 6 0 0 1 {x + 24} {y + 6}H{x + 18}Z" {attrs}/>',
            left,
            f'<rect id="{element_id(prefix, "center")}" x="{x + 6}" y="{y + 6}" width="12" height="12" {attrs}/>',
            f'<rect id="{element_id(prefix, "right")}" x="{x + 18}" y="{y + 6}" width="6" height="12" {attrs}/>',
            f'<path id="{element_id(prefix, "bottomleft")}" d="M{x} {y + 18}H{x + 6}V{y + 24}A6 6 0 0 1 {x} {y + 18}Z" {attrs}/>',
            f'<rect id="{element_id(prefix, "bottom")}" x="{x + 6}" y="{y + 18}" width="12" height="6" {attrs}/>',
            f'<path id="{element_id(prefix, "bottomright")}" d="M{x + 18} {y + 18}H{x + 24}A6 6 0 0 1 {x + 18} {y + 24}Z" {attrs}/>',
        ]
    )


def margins(prefix: str, x: int, y: int, size: int = 6) -> str:
    hidden = 'fill="#000" fill-opacity="0"'
    return "\n".join(
        [
            f'<rect id="{element_id(prefix, "hint-top-margin")}" x="{x}" y="{y}" width="1" height="{size}" {hidden}/>',
            f'<rect id="{element_id(prefix, "hint-right-margin")}" x="{x + 2}" y="{y}" width="{size}" height="1" {hidden}/>',
            f'<rect id="{element_id(prefix, "hint-bottom-margin")}" x="{x + 9}" y="{y}" width="1" height="{size}" {hidden}/>',
            f'<rect id="{element_id(prefix, "hint-left-margin")}" x="{x + 11}" y="{y}" width="{size}" height="1" {hidden}/>',
            f'<rect id="{element_id(prefix, "hint-top-inset")}" x="{x + 18}" y="{y}" width="1" height="{size}" {hidden}/>',
            f'<rect id="{element_id(prefix, "hint-right-inset")}" x="{x + 20}" y="{y}" width="{size}" height="1" {hidden}/>',
            f'<rect id="{element_id(prefix, "hint-bottom-inset")}" x="{x + 27}" y="{y}" width="1" height="{size}" {hidden}/>',
            f'<rect id="{element_id(prefix, "hint-left-inset")}" x="{x + 29}" y="{y}" width="{size}" height="1" {hidden}/>',
            f'<rect id="{element_id(prefix, "hint-stretch-borders")}" x="{x + 36}" y="{y}" width="1" height="1" {hidden}/>',
        ]
    )


def svg(body: str) -> str:
    return SVG_HEADER + "  " + body.replace("\n", "\n  ") + "\n</svg>\n"


def background(paint: Paint, *, notch: bool = False, mask: bool = True) -> str:
    parts = [frame("", 0, 0, paint, notch=notch), margins("", 0, 32)]
    if mask:
        parts.extend([frame("mask", 40, 0, Paint("ColorScheme-Text"), notch=notch), margins("mask", 40, 32)])
    return svg("\n".join(parts))


def state_sheet(states: list[tuple[str, Paint]], *, notch_states: set[str] | None = None,
                marker_states: set[str] | None = None) -> str:
    parts: list[str] = []
    notch_states = notch_states or set()
    marker_states = marker_states or set()
    for index, (name, paint) in enumerate(states):
        x = (index % 8) * 40
        y = (index // 8) * 64
        parts.extend([frame(name, x, y, paint, notch=name in notch_states,
                            marker=name in marker_states), margins(name, x, y + 32, 4)])
    return svg("\n".join(parts))


def heading() -> str:
    return state_sheet(
        [
            ("header", Paint("ColorScheme-ButtonBackground", 0.98)),
            ("footer", Paint("ColorScheme-ButtonBackground", 0.98)),
        ],
        notch_states={"header"},
    )


def symbols(items: list[tuple[str, str, str]]) -> str:
    """Return a symbol sheet of original 24px line geometry."""
    body = []
    for index, (name, path_data, css_class) in enumerate(items):
        x = (index % 12) * 32
        y = (index // 12) * 32
        body.append(
            f'<path id="{name}" d="{path_data}" transform="translate({x} {y})" '
            f'class="{css_class}" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="square" stroke-linejoin="miter"/>'
        )
    return svg("\n".join(body))


def control_sheet(states: list[tuple[str, Paint]]) -> str:
    return state_sheet(states, notch_states={name for name, _ in states if name in {"focus", "checked", "pressed"}})


def semantic_symbols(names: list[str]) -> str:
    """Draw compact original symbols from the versioned contract for shell-owned semantic element IDs."""
    body: list[str] = []
    for index, name in enumerate(names):
        x = (index % 12) * 32
        y = (index // 12) * 32
        css_class = "ColorScheme-Highlight" if any(word in name for word in ("active", "hover", "pressed", "event")) else "ColorScheme-Text"
        path_d = GLYPHS.get(name, "M12 12l1 1")
        body.append(
            f'<g id="{name}" transform="translate({x} {y})" class="{css_class}" '
            'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="square" stroke-linejoin="miter">'
            f'<path d="{path_d}"/></g>'
        )
    return svg("\n".join(body))


def write(relative: str, content: str) -> None:
    path = THEME / relative
    if CHECK_MODE:
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            DRIFT.append(relative)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> None:
    write("dialogs/background.svg", background(Paint("ColorScheme-Background", 0.98), notch=True))
    write("widgets/panel-background.svg", background(Paint("ColorScheme-Background", 0.96)))
    write("widgets/background.svg", background(Paint("ColorScheme-Background", 0.98), notch=True))
    write("widgets/tooltip.svg", background(Paint("ColorScheme-ButtonBackground", 0.98), notch=False))
    write(
        "widgets/button.svg",
        state_sheet(
            [
                ("normal", Paint("ColorScheme-ButtonBackground")),
                ("hover", Paint("ColorScheme-ButtonHover", 0.22)),
                ("focus", Paint("NoxForge-Selected")),
                ("pressed", Paint("NoxForge-Selected")),
                ("toolbutton-hover", Paint("ColorScheme-ButtonHover", 0.2)),
                ("toolbutton-focus", Paint("NoxForge-Selected")),
                ("toolbutton-pressed", Paint("NoxForge-Selected")),
            ],
            notch_states={"focus", "pressed", "toolbutton-focus", "toolbutton-pressed"},
            marker_states={"focus", "pressed", "toolbutton-focus", "toolbutton-pressed"},
        ),
    )
    write(
        "widgets/tasks.svg",
        state_sheet(
            [
                ("normal", Paint("ColorScheme-ButtonBackground", 0.45)),
                ("hover", Paint("ColorScheme-ViewHover", 0.22)),
                ("focus", Paint("NoxForge-Selected")),
                ("attention", Paint("ColorScheme-ViewHover", 0.42)),
                ("minimized", Paint("ColorScheme-ButtonBackground", 0.24)),
                ("progress", Paint("NoxForge-Selected")),
            ] + [
                (f"{orientation}-{state}", paint)
                for orientation in ("north", "south", "east", "west")
                for state, paint in (
                    ("normal", Paint("ColorScheme-ButtonBackground", 0.45)),
                    ("hover", Paint("ColorScheme-ViewHover", 0.22)),
                    ("focus", Paint("NoxForge-Selected")),
                    ("attention", Paint("ColorScheme-ViewHover", 0.42)),
                    ("minimized", Paint("ColorScheme-ButtonBackground", 0.24)),
                    ("progress", Paint("NoxForge-Selected")),
                )
            ],
            notch_states={"focus", "progress"},
            marker_states={"focus", "progress"} | {
                f"{orientation}-{state}" for orientation in ("north", "south", "east", "west")
                for state in ("focus", "progress")
            },
        ),
    )
    write(
        "widgets/viewitem.svg",
        state_sheet(
            [
                ("normal", Paint("ColorScheme-ViewBackground", 0.08)),
                ("hover", Paint("ColorScheme-ViewHover", 0.18)),
                ("selected", Paint("NoxForge-Selected")),
                ("selected+hover", Paint("NoxForge-Selected")),
            ],
            notch_states={"selected", "selected+hover"},
            marker_states={"selected", "selected+hover"},
        ),
    )
    write(
        "widgets/lineedit.svg",
        state_sheet(
            [
                ("base", Paint("ColorScheme-ViewBackground", 0.96)),
                ("hover", Paint("ColorScheme-ViewHover", 0.16)),
                ("focus", Paint("NoxForge-Selected")),
            ],
            notch_states={"focus"},
            marker_states={"focus"},
        ),
    )
    write("widgets/plasmoidheading.svg", heading())
    write("widgets/toolbar.svg", background(Paint("ColorScheme-ButtonBackground", 0.82), notch=False, mask=False))
    write(
        "widgets/listitem.svg",
        control_sheet(
            [
                ("normal", Paint("ColorScheme-ViewBackground", 0.04)),
                ("hover", Paint("ColorScheme-ButtonHover", 0.14)),
                ("pressed", Paint("ColorScheme-Highlight", 0.18)),
                ("section", Paint("ColorScheme-ButtonBackground", 0.78)),
            ]
        ),
    )
    write(
        "widgets/menubaritem.svg",
        control_sheet(
            [
                ("normal", Paint("ColorScheme-ButtonBackground", 0.04)),
                ("hover", Paint("ColorScheme-ButtonHover", 0.16)),
                ("pressed", Paint("ColorScheme-Highlight", 0.2)),
            ]
        ),
    )
    write(
        "widgets/frame.svg",
        control_sheet(
            [
                ("plain", Paint("ColorScheme-Background", 0.86)),
                ("raised", Paint("ColorScheme-ButtonBackground", 0.96)),
                ("sunken", Paint("ColorScheme-ViewBackground", 0.96)),
            ]
        ),
    )
    write(
        "widgets/tabbar.svg",
        control_sheet(
            [
                ("north-active-tab", Paint("ColorScheme-Highlight", 0.18)),
                ("south-active-tab", Paint("ColorScheme-Highlight", 0.18)),
                ("east-active-tab", Paint("ColorScheme-Highlight", 0.18)),
                ("west-active-tab", Paint("ColorScheme-Highlight", 0.18)),
            ]
        ),
    )
    write(
        "widgets/scrollbar.svg",
        control_sheet(
            [
                ("background-horizontal", Paint("ColorScheme-ViewBackground", 0.35)),
                ("background-vertical", Paint("ColorScheme-ViewBackground", 0.35)),
                ("slider", Paint("ColorScheme-Text", 0.36)),
                ("mouseover-slider", Paint("ColorScheme-Highlight", 0.62)),
            ]
        ).replace("</svg>", '<rect id="hint-scrollbar-size" x="220" y="220" width="10" height="10" fill="#000" fill-opacity="0"/></svg>'),
    )
    write(
        "widgets/slider.svg",
        control_sheet(
            [
                ("groove", Paint("ColorScheme-Text", 0.2)),
                ("groove-highlight", Paint("ColorScheme-Highlight", 0.78)),
            ]
        )
        .replace("</svg>", '<rect id="hint-handle-size" x="160" y="160" width="18" height="18" fill="#000" fill-opacity="0"/><circle id="horizontal-slider-handle" cx="180" cy="180" r="8" class="ColorScheme-Text" fill="currentColor"/><circle id="horizontal-slider-hover" cx="204" cy="180" r="8" class="ColorScheme-Highlight" fill="currentColor"/><circle id="horizontal-slider-focus" cx="228" cy="180" r="8" class="ColorScheme-Highlight" fill="currentColor"/><circle id="vertical-slider-handle" cx="252" cy="180" r="8" class="ColorScheme-Text" fill="currentColor"/><circle id="vertical-slider-hover" cx="276" cy="180" r="8" class="ColorScheme-Highlight" fill="currentColor"/><circle id="vertical-slider-focus" cx="300" cy="180" r="8" class="ColorScheme-Highlight" fill="currentColor"/></svg>'),
    )
    write(
        "widgets/switch.svg",
        control_sheet(
            [
                ("inactive", Paint("ColorScheme-Text", 0.18)),
                ("active", Paint("ColorScheme-Highlight", 0.72)),
            ]
        )
        .replace("</svg>", '<rect id="hint-handle-size" x="160" y="160" width="16" height="16" fill="#000" fill-opacity="0"/><circle id="handle" cx="180" cy="180" r="8" class="ColorScheme-Text" fill="currentColor"/><circle id="handle-hover" cx="204" cy="180" r="8" class="ColorScheme-Highlight" fill="currentColor"/><circle id="handle-focus" cx="228" cy="180" r="8" class="ColorScheme-Highlight" fill="currentColor"/><circle id="handle-pressed" cx="252" cy="180" r="7" class="ColorScheme-Highlight" fill="currentColor"/></svg>'),
    )
    write(
        "widgets/radiobutton.svg",
        symbols(
            [
                ("normal", "M4 12a8 8 0 1 0 16 0 8 8 0 1 0-16 0", "ColorScheme-Text"),
                ("hover", "M4 12a8 8 0 1 0 16 0 8 8 0 1 0-16 0", "ColorScheme-ButtonHover"),
                ("focus", "M4 12a8 8 0 1 0 16 0 8 8 0 1 0-16 0", "ColorScheme-Highlight"),
                ("checked", "M4 12a8 8 0 1 0 16 0 8 8 0 1 0-16 0M9 12h6", "ColorScheme-Highlight"),
            ]
        ),
    )
    write(
        "widgets/checkmarks.svg",
        symbols(
            [
                ("checkbox", "M5 12l4 4L19 6", "ColorScheme-Highlight"),
                ("radiobutton", "M12 7a5 5 0 1 0 0 10 5 5 0 1 0 0-10", "ColorScheme-Highlight"),
            ]
        ),
    )
    write(
        "widgets/arrows.svg",
        symbols(
            [
                ("up-arrow", "M6 15l6-6 6 6", "ColorScheme-Text"),
                ("down-arrow", "M6 9l6 6 6-6", "ColorScheme-Text"),
                ("left-arrow", "M15 6l-6 6 6 6", "ColorScheme-Text"),
                ("right-arrow", "M9 6l6 6-6 6", "ColorScheme-Text"),
            ]
        ),
    )
    write(
        "widgets/actionbutton.svg",
        symbols(
            [
                ("normal", "M5 12h14", "ColorScheme-Text"),
                ("hover", "M5 12h14", "ColorScheme-ButtonHover"),
                ("focus", "M5 12h14", "ColorScheme-Highlight"),
                ("pressed", "M7 12h10", "ColorScheme-Highlight"),
                ("16-16-normal", "M6 12h12", "ColorScheme-Text"),
                ("16-16-hover", "M6 12h12", "ColorScheme-ButtonHover"),
                ("16-16-focus", "M6 12h12", "ColorScheme-Highlight"),
                ("16-16-pressed", "M7 12h10", "ColorScheme-Highlight"),
                ("22-22-normal", "M5 12h14", "ColorScheme-Text"),
                ("22-22-hover", "M5 12h14", "ColorScheme-ButtonHover"),
                ("22-22-focus", "M5 12h14", "ColorScheme-Highlight"),
                ("22-22-pressed", "M7 12h10", "ColorScheme-Highlight"),
                ("24-24-normal", "M4 12h16", "ColorScheme-Text"),
                ("24-24-hover", "M4 12h16", "ColorScheme-ButtonHover"),
                ("24-24-focus", "M4 12h16", "ColorScheme-Highlight"),
                ("24-24-pressed", "M6 12h12", "ColorScheme-Highlight"),
            ]
        ),
    )
    for relative, paint, mask in (
        ("opaque/dialogs/background.svg", Paint("ColorScheme-Background"), False),
        ("opaque/widgets/panel-background.svg", Paint("ColorScheme-Background"), False),
        ("opaque/widgets/tooltip.svg", Paint("ColorScheme-ButtonBackground"), False),
        ("solid/dialogs/background.svg", Paint("ColorScheme-Background"), False),
        ("solid/widgets/background.svg", Paint("ColorScheme-Background"), False),
        ("solid/widgets/panel-background.svg", Paint("ColorScheme-Background"), False),
        ("solid/widgets/tooltip.svg", Paint("ColorScheme-ButtonBackground"), False),
        ("translucent/dialogs/background.svg", Paint("ColorScheme-Background", 0.94), False),
        ("translucent/widgets/background.svg", Paint("ColorScheme-Background", 0.92), False),
        ("translucent/widgets/panel-background.svg", Paint("ColorScheme-Background", 0.9), False),
        ("translucent/widgets/tooltip.svg", Paint("ColorScheme-ButtonBackground", 0.94), False),
    ):
        write(relative, background(paint, notch="dialogs/" in relative, mask=mask))

    symbol_assets = {
        "widgets/calendar.svg": ["event"],
        "widgets/busywidget.svg": ["stopped", "busywidget", "22-22-busywidget", "16-16-busywidget", "hint-rotation-angle"],
        "widgets/clock.svg": ["ClockFace", "HourHand", "MinuteHand", "SecondHand", "HandCenterScrew", "Glass"],
        "widgets/configuration-icons.svg": [
            "menu", "configure", "rotate", "move", "size-vertical", "size-horizontal",
            "size-diagonal-tr2bl", "size-diagonal-tl2br", "maximize", "unmaximize", "status",
            "collapse", "return-to-source", "restore", "help", "delete", "add", "remove",
            "filter", "close", "showbackground",
        ],
        "widgets/containment-controls.svg": [
            "vertical-centerindicator", "horizontal-centerindicator", "south-maxslider",
            "south-offsetslider", "south-center", "south-bottom", "south-top", "north-center",
            "north-bottom", "north-top", "west-center", "west-left", "west-right", "east-center",
            "east-left", "east-right", "south-minslider", "north-maxslider", "north-offsetslider",
            "north-minslider", "east-maxslider", "east-offsetslider", "east-minslider",
            "west-maxslider", "west-offsetslider", "west-minslider",
        ],
        "widgets/action-overlays.svg": [
            "add-normal", "remove-normal", "add-hover", "add-pressed", "remove-hover",
            "remove-pressed", "open-normal", "open-hover", "open-pressed",
        ],
        "widgets/branding.svg": ["brilliant"],
        "widgets/line.svg": ["vertical-line", "horizontal-line"],
        "widgets/analog_meter.svg": ["background", "label1", "label0", "pointer", "rotateminmax", "rotatecenter", "foreground", "pointer-shadow"],
        "widgets/notes.svg": ["yellow-notes", "green-notes", "red-notes", "blue-notes", "white-notes", "pink-notes", "orange-notes", "black-notes", "transluscent-notes"],
        "widgets/timer.svg": [str(value) for value in range(10)] + ["separator", "separatorB", "separatorC"],
    }
    for relative, names in symbol_assets.items():
        write(relative, semantic_symbols(names))

    write("widgets/dragger.svg", state_sheet([
        ("vertical", Paint("ColorScheme-Text", 0.4)),
        ("horizontal", Paint("ColorScheme-Text", 0.4)),
    ]))
    write("widgets/glowbar.svg", state_sheet([
        (edge, Paint("ColorScheme-Highlight", 0.72)) for edge in ("north", "south", "east", "west")
    ], notch_states={"north", "south", "east", "west"}))
    write("widgets/margins-highlight.svg", state_sheet([
        (edge, Paint("ColorScheme-Highlight", 0.24)) for edge in ("north", "south", "east", "west")
    ]))
    write("widgets/monitor.svg", state_sheet([
        ("monitor", Paint("ColorScheme-ButtonBackground", 0.96)),
        ("monitor-active", Paint("NoxForge-Selected")),
    ], notch_states={"monitor-active"}, marker_states={"monitor-active"}))
    write("weather/wind-arrows.svg", semantic_symbols([
        "wind-north", "wind-north-east", "wind-east", "wind-south-east",
        "wind-south", "wind-south-west", "wind-west", "wind-north-west",
    ]))

    write("widgets/plot-background.svg", background(Paint("ColorScheme-ViewBackground"), notch=False, mask=False))
    write("widgets/translucentbackground.svg", background(Paint("ColorScheme-Background", 0.9)))
    write("widgets/pager.svg", state_sheet([
        ("normal", Paint("ColorScheme-ButtonBackground", 0.7)),
        ("hover", Paint("ColorScheme-ButtonHover", 0.2)),
        ("active", Paint("ColorScheme-Highlight", 0.24)),
    ], notch_states={"active"}))
    write("widgets/media-delegate.svg", state_sheet([
        ("picture", Paint("ColorScheme-ButtonBackground", 0.9)),
        ("picture-selected", Paint("ColorScheme-Highlight", 0.22)),
    ], notch_states={"picture-selected"}))
    write("widgets/picker.svg", background(Paint("ColorScheme-ButtonBackground", 0.96)))
    write("widgets/scrollwidget.svg", state_sheet([("border", Paint("ColorScheme-Background", 0.92))]))
    for relative in ("widgets/bar_meter_horizontal.svg", "widgets/bar_meter_vertical.svg"):
        write(relative, state_sheet([
            ("bar-inactive", Paint("ColorScheme-Text", 0.18)),
            ("bar-active", Paint("ColorScheme-Highlight", 0.78)),
        ]))
    if CHECK_MODE and DRIFT:
        raise SystemExit("stale Plasma SVG assets: " + ", ".join(DRIFT))
    if not CHECK_MODE:
        print(f"Generated {len(list(THEME.rglob('*.svg')))} original Plasma Style SVG assets")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    CHECK_MODE = arguments.check
    main()
