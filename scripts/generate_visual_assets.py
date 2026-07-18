#!/usr/bin/env python3
"""Generate original NoxForge Aurorae and representative icon SVGs."""

from __future__ import annotations

import gzip
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AURORAE = ROOT / "aurorae/io.github.loofiboss.noxforge.desktop"
ICONS = ROOT / "icons/NoxForge"

ICON_SPECS = {
    "actions/document-new.svg": '<path d="M6 3h8l4 4v14H6zM14 3v5h4"/><path class="accent" d="M9 14h6M12 11v6"/>',
    "actions/document-open.svg": '<path d="M3 7h7l2 2h9l-2 10H5z"/><path class="accent" d="M11 13h5M14 10l3 3-3 3"/>',
    "actions/document-save.svg": '<path d="M4 3h13l3 3v15H4zM8 3v6h8V3M8 15h8v6"/><path class="accent" d="M17 3v5"/>',
    "actions/edit-copy.svg": '<path d="M8 8h11v12H8zM5 16H3V4h11v2"/><path class="accent" d="M15 8l4 4"/>',
    "actions/edit-paste.svg": '<path d="M7 5H4v16h14v-3M9 3h6v4H9zM8 9h12v9H8z"/><path class="accent" d="M16 9l4 4"/>',
    "actions/edit-delete.svg": '<path d="M5 7h14M9 7V4h6v3M7 7l1 14h8l1-14M10 11v6M14 11v6"/><path class="accent" d="M4 7h4"/>',
    "actions/system-search.svg": '<circle cx="10" cy="10" r="6"/><path d="M14.5 14.5L21 21"/><path class="accent" d="M6 8l2-2h3"/>',
    "actions/configure.svg": '<path d="M4 6h16M4 12h16M4 18h16"/><circle cx="9" cy="6" r="2"/><circle cx="15" cy="12" r="2"/><circle cx="11" cy="18" r="2"/><path class="accent" d="M9 4v4"/>',
    "places/folder.svg": '<path d="M3 6h7l2 2h9v11H3z"/><path class="accent" d="M3 9h18"/>',
    "places/folder-open.svg": '<path d="M3 7h7l2 2h9l-2 10H5L3 12z"/><path class="accent" d="M5 12h16"/>',
    "places/user-home.svg": '<path d="M3 11l9-8 9 8M6 9v12h12V9M10 21v-6h4v6"/><path class="accent" d="M12 3l4 4"/>',
    "places/user-desktop.svg": '<rect x="3" y="4" width="18" height="13" rx="1"/><path d="M9 21h6M12 17v4"/><path class="accent" d="M4 5h5"/>',
    "places/network-workgroup.svg": '<circle cx="12" cy="5" r="2.5"/><circle cx="5" cy="18" r="2.5"/><circle cx="19" cy="18" r="2.5"/><path d="M12 7.5v4M12 11.5L6 15.5M12 11.5l6 4"/><path class="accent" d="M9 12h6"/>',
    "devices/computer.svg": '<rect x="3" y="3" width="13" height="11" rx="1"/><path d="M7 18h5M9.5 14v4M18 7h3v14h-7v-5"/><path class="accent" d="M19 9v4"/>',
    "devices/drive-harddisk.svg": '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8" cy="12" r="2"/><path d="M12 10h6M12 14h6"/><path class="accent" d="M16 17h2"/>',
    "devices/audio-card.svg": '<path d="M4 5h13v14H4zM17 9h3v6h-3M7 8h6M7 12h6M7 16h3"/><path class="accent" d="M12 16h2"/>',
    "devices/input-keyboard.svg": '<rect x="2" y="6" width="20" height="12" rx="2"/><path d="M5 10h2M9 10h2M13 10h2M17 10h2M5 14h2M9 14h8M19 14h1"/><path class="accent" d="M9 14h8"/>',
    "devices/input-mouse.svg": '<rect x="7" y="2" width="10" height="20" rx="5"/><path d="M12 2v7M7 9h10"/><path class="accent" d="M12 4v3"/>',
    "devices/phone.svg": '<rect x="6" y="2" width="12" height="20" rx="2"/><path d="M9 5h6M10 19h4"/><path class="accent" d="M16 2v5"/>',
    "status/network-wireless.svg": '<path d="M3 9a13 13 0 0 1 18 0M6 12a9 9 0 0 1 12 0M9 15a5 5 0 0 1 6 0"/><circle class="accent-fill" cx="12" cy="19" r="1.5"/>',
    "status/network-wired.svg": '<path d="M4 4h16v10h-6v3h3v3H7v-3h3v-3H4z"/><path class="accent" d="M8 8h8"/>',
    "status/audio-volume-high.svg": '<path d="M3 9h4l5-4v14l-5-4H3zM16 9a5 5 0 0 1 0 6M18 6a9 9 0 0 1 0 12"/><path class="accent" d="M12 6v4"/>',
    "status/battery-good.svg": '<rect x="3" y="6" width="17" height="12" rx="2"/><path d="M20 10h2v4h-2"/><path class="accent" d="M7 12h8"/>',
    "status/dialog-warning.svg": '<path d="M12 3L22 20H2zM12 8v6"/><circle class="accent-fill" cx="12" cy="17" r="1"/>',
}


def icon_svg(body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
  <style>
    .accent {{ stroke: #A3FF47; }}
    .accent-fill {{ fill: #A3FF47; stroke: none; }}
  </style>
  <g fill="none" stroke="#E8F0F2" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
    {body}
  </g>
</svg>
'''


def decoration_frame(prefix: str, x: int, y: int, css_class: str, opacity: float, *, active: bool) -> str:
    def name(position: str) -> str:
        return f"{prefix}-{position}"

    attr = f'class="{css_class}" fill="currentColor" fill-opacity="{opacity:g}"'
    top = f'<g id="{name("top")}"><rect x="{x + 6}" y="{y}" width="28" height="6" {attr}/>'
    if active:
        top += f'<path d="M{x + 8} {y + 1}h10" class="ColorScheme-Highlight" stroke="currentColor" stroke-width="1"/>'
    top += "</g>"
    return "\n".join(
        [
            f'<path id="{name("topleft")}" d="M{x + 4} {y}H{x + 6}V{y + 6}H{x}V{y + 4}Z" {attr}/>',
            top,
            f'<path id="{name("topright")}" d="M{x + 34} {y}A6 6 0 0 1 {x + 40} {y + 6}H{x + 34}Z" {attr}/>',
            f'<rect id="{name("left")}" x="{x}" y="{y + 6}" width="6" height="28" {attr}/>',
            f'<rect id="{name("center")}" x="{x + 6}" y="{y + 6}" width="28" height="28" {attr}/>',
            f'<rect id="{name("right")}" x="{x + 34}" y="{y + 6}" width="6" height="28" {attr}/>',
            f'<path id="{name("bottomleft")}" d="M{x} {y + 34}H{x + 6}V{y + 40}A6 6 0 0 1 {x} {y + 34}Z" {attr}/>',
            f'<rect id="{name("bottom")}" x="{x + 6}" y="{y + 34}" width="28" height="6" {attr}/>',
            f'<path id="{name("bottomright")}" d="M{x + 34} {y + 34}H{x + 40}A6 6 0 0 1 {x + 34} {y + 40}Z" {attr}/>',
        ]
    )


def decoration_svg() -> str:
    active = decoration_frame("decoration", 0, 0, "ColorScheme-Background", 1.0, active=True)
    inactive = decoration_frame("decoration-inactive", 52, 0, "ColorScheme-ViewBackground", 0.96, active=False)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="80" viewBox="0 0 160 80">
  <defs>
    <style id="current-color-scheme" type="text/css"><![CDATA[
      .ColorScheme-Background {{ color: #141B21; }}
      .ColorScheme-ViewBackground {{ color: #0E1318; }}
      .ColorScheme-Highlight {{ color: #A3FF47; }}
    ]]></style>
  </defs>
  {active}
  {inactive}
  <rect id="decoration-maximized-center" x="104" y="0" width="28" height="28" class="ColorScheme-Background" fill="currentColor"/>
  <rect id="decoration-maximized-inactive-center" x="104" y="36" width="28" height="28" class="ColorScheme-ViewBackground" fill="currentColor"/>
</svg>
'''


BUTTON_STATES = (
    ("active", "ColorScheme-Text", 0.0),
    ("inactive", "ColorScheme-Text", 0.0),
    ("hover", "ColorScheme-Highlight", 0.18),
    ("hover-inactive", "ColorScheme-Text", 0.1),
    ("pressed", "ColorScheme-Highlight", 0.3),
    ("pressed-inactive", "ColorScheme-Text", 0.16),
    ("deactivated", "ColorScheme-Text", 0.0),
    ("deactivated-inactive", "ColorScheme-Text", 0.0),
)

GLYPHS = {
    "close": '<path d="M8 8l8 8M16 8l-8 8"/>',
    "minimize": '<path d="M7 15h10"/>',
    "maximize": '<path d="M7 7h10v10H7zM7 10l3-3"/>',
    "restore": '<path d="M8 10h8v7H8zM10 10V7h7v7h-1"/>',
}


def button_svg(kind: str) -> str:
    groups = []
    for index, (state, color_class, opacity) in enumerate(BUTTON_STATES):
        x = index * 32
        foreground = "#FF6B7A" if kind == "close" and state in {"hover", "pressed"} else "currentColor"
        groups.append(
            f'''<g id="{state}-center" transform="translate({x} 0)" class="{color_class}" color="#E8F0F2">
      <rect width="24" height="24" rx="5" fill="currentColor" fill-opacity="{opacity:g}"/>
      <g fill="none" stroke="{foreground}" stroke-width="1.7" stroke-linecap="square" stroke-linejoin="miter">{GLYPHS[kind]}</g>
    </g>'''
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="256" height="24" viewBox="0 0 256 24">
  <defs>
    <style id="current-color-scheme" type="text/css"><![CDATA[
      .ColorScheme-Text {{ color: #E8F0F2; }}
      .ColorScheme-Highlight {{ color: #A3FF47; }}
    ]]></style>
  </defs>
  {"\n  ".join(groups)}
</svg>
'''


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def write_aurorae_svg(name: str, content: str) -> None:
    write(AURORAE / f"{name}.svg", content)
    (AURORAE / f"{name}.svgz").write_bytes(gzip.compress(content.encode("utf-8"), mtime=0))


def main() -> None:
    for relative, body in sorted(ICON_SPECS.items()):
        write(ICONS / "scalable" / relative, icon_svg(body))
    write_aurorae_svg("decoration", decoration_svg())
    for kind in GLYPHS:
        write_aurorae_svg(kind, button_svg(kind))
    print(f"Generated {len(ICON_SPECS)} icons and 5 editable/compressed Aurorae asset pairs")


if __name__ == "__main__":
    main()
