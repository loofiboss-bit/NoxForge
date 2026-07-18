#!/usr/bin/env python3
"""Generate original NoxForge Plasma Style SVG assets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop"
SVG_HEADER = """<svg xmlns="http://www.w3.org/2000/svg" width="640" height="480" viewBox="0 0 640 480">
  <defs>
    <style id="current-color-scheme" type="text/css"><![CDATA[
      .ColorScheme-Background { color: #141B21; }
      .ColorScheme-ViewBackground { color: #0E1318; }
      .ColorScheme-ButtonBackground { color: #1A232B; }
      .ColorScheme-Text { color: #E8F0F2; }
      .ColorScheme-Highlight { color: #A3FF47; }
      .ColorScheme-ViewHover { color: #22D3EE; }
      .ColorScheme-ButtonHover { color: #22D3EE; }
      .ColorScheme-ButtonFocus { color: #A3FF47; }
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


def frame(prefix: str, x: int, y: int, paint: Paint, *, notch: bool = False) -> str:
    """Return a self-contained 6/12/6 nine-slice frame."""
    attrs = paint_attrs(paint)
    top_left = (
        f'<path id="{element_id(prefix, "topleft")}" d="M{x + 4} {y}H{x + 6}V{y + 6}H{x}V{y + 4}Z" {attrs}/>'
        if notch
        else f'<path id="{element_id(prefix, "topleft")}" d="M{x + 6} {y}V{y + 6}H{x}V{y + 6}A6 6 0 0 1 {x + 6} {y}Z" {attrs}/>'
    )
    return "\n".join(
        [
            top_left,
            f'<rect id="{element_id(prefix, "top")}" x="{x + 6}" y="{y}" width="12" height="6" {attrs}/>',
            f'<path id="{element_id(prefix, "topright")}" d="M{x + 18} {y}A6 6 0 0 1 {x + 24} {y + 6}H{x + 18}Z" {attrs}/>',
            f'<rect id="{element_id(prefix, "left")}" x="{x}" y="{y + 6}" width="6" height="12" {attrs}/>',
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
        ]
    )


def svg(body: str) -> str:
    return SVG_HEADER + "  " + body.replace("\n", "\n  ") + "\n</svg>\n"


def background(paint: Paint, *, notch: bool = True, mask: bool = True) -> str:
    parts = [frame("", 0, 0, paint, notch=notch), margins("", 0, 32)]
    if mask:
        parts.extend([frame("mask", 40, 0, Paint("ColorScheme-Text"), notch=notch), margins("mask", 40, 32)])
    return svg("\n".join(parts))


def state_sheet(states: list[tuple[str, Paint]], *, notch_states: set[str] | None = None) -> str:
    parts: list[str] = []
    notch_states = notch_states or set()
    for index, (name, paint) in enumerate(states):
        x = (index % 8) * 40
        y = (index // 8) * 64
        parts.extend([frame(name, x, y, paint, notch=name in notch_states), margins(name, x, y + 32, 4)])
    return svg("\n".join(parts))


def heading() -> str:
    return state_sheet(
        [
            ("header", Paint("ColorScheme-ButtonBackground", 0.98)),
            ("footer", Paint("ColorScheme-ButtonBackground", 0.98)),
        ],
        notch_states={"header"},
    )


def write(relative: str, content: str) -> None:
    path = THEME / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> None:
    write("dialogs/background.svg", background(Paint("ColorScheme-Background", 0.98)))
    write("widgets/panel-background.svg", background(Paint("ColorScheme-Background", 0.96)))
    write("widgets/background.svg", background(Paint("ColorScheme-Background", 0.98)))
    write("widgets/tooltip.svg", background(Paint("ColorScheme-ButtonBackground", 0.98), notch=False))
    write(
        "widgets/button.svg",
        state_sheet(
            [
                ("normal", Paint("ColorScheme-ButtonBackground")),
                ("hover", Paint("ColorScheme-ButtonHover", 0.22)),
                ("focus", Paint("ColorScheme-ButtonFocus", 0.28)),
                ("pressed", Paint("ColorScheme-Highlight", 0.38)),
                ("toolbutton-hover", Paint("ColorScheme-ButtonHover", 0.2)),
                ("toolbutton-focus", Paint("ColorScheme-ButtonFocus", 0.25)),
                ("toolbutton-pressed", Paint("ColorScheme-Highlight", 0.35)),
            ],
            notch_states={"pressed", "toolbutton-pressed"},
        ),
    )
    write(
        "widgets/tasks.svg",
        state_sheet(
            [
                ("normal", Paint("ColorScheme-ButtonBackground", 0.45)),
                ("hover", Paint("ColorScheme-ViewHover", 0.22)),
                ("focus", Paint("ColorScheme-Highlight", 0.32)),
                ("attention", Paint("ColorScheme-ViewHover", 0.42)),
                ("minimized", Paint("ColorScheme-ButtonBackground", 0.24)),
                ("progress", Paint("ColorScheme-Highlight", 0.5)),
            ],
            notch_states={"focus", "progress"},
        ),
    )
    write(
        "widgets/viewitem.svg",
        state_sheet(
            [
                ("normal", Paint("ColorScheme-ViewBackground", 0.08)),
                ("hover", Paint("ColorScheme-ViewHover", 0.18)),
                ("selected", Paint("ColorScheme-Highlight", 0.32)),
                ("selected+hover", Paint("ColorScheme-Highlight", 0.42)),
            ],
            notch_states={"selected", "selected+hover"},
        ),
    )
    write(
        "widgets/lineedit.svg",
        state_sheet(
            [
                ("base", Paint("ColorScheme-ViewBackground", 0.96)),
                ("hover", Paint("ColorScheme-ViewHover", 0.16)),
                ("focus", Paint("ColorScheme-Highlight", 0.24)),
            ],
            notch_states={"focus"},
        ),
    )
    write("widgets/plasmoidheading.svg", heading())
    print("Generated 9 original Plasma Style SVG assets")


if __name__ == "__main__":
    main()
