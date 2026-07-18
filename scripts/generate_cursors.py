#!/usr/bin/env python3
"""Generate original multi-size NoxForge Xcursor files without symlinks."""

from __future__ import annotations

import json
import math
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "cursors/NoxForge-Cursors"
SIZES = (24, 32, 48)
XCURSOR_IMAGE_TYPE = 0xFFFD0002

COLORS = {
    "outline": 0xFFE8F0F2,
    "fill": 0xFF141B21,
    "accent": 0xFFA3FF47,
    "transparent": 0x00000000,
}

ALIASES = {
    "arrow": "default", "left_ptr": "default", "top_left_arrow": "default", "wayland-cursor": "default",
    "pointer": "hand", "hand1": "hand", "hand2": "hand", "pointing_hand": "hand", "link": "hand",
    "xterm": "text", "ibeam": "text", "vertical-text": "text",
    "watch": "wait", "half-busy": "progress", "left_ptr_watch": "progress",
    "cross": "crosshair", "tcross": "crosshair", "cell": "crosshair",
    "h_double_arrow": "ew-resize", "sb_h_double_arrow": "ew-resize", "size_hor": "ew-resize", "col-resize": "ew-resize", "split_h": "ew-resize", "e-resize": "ew-resize", "w-resize": "ew-resize",
    "v_double_arrow": "ns-resize", "sb_v_double_arrow": "ns-resize", "size_ver": "ns-resize", "row-resize": "ns-resize", "split_v": "ns-resize", "n-resize": "ns-resize", "s-resize": "ns-resize",
    "size_fdiag": "nwse-resize", "size-fdiag": "nwse-resize", "nw-resize": "nwse-resize", "se-resize": "nwse-resize",
    "size_bdiag": "nesw-resize", "size-bdiag": "nesw-resize", "ne-resize": "nesw-resize", "sw-resize": "nesw-resize",
    "fleur": "move", "size_all": "move", "all-scroll": "move", "openhand": "grab", "closedhand": "grabbing",
    "not-allowed": "forbidden", "no-drop": "forbidden", "crossed_circle": "forbidden", "dnd-no-drop": "forbidden",
    "dnd-copy": "copy", "alias": "copy", "dnd-move": "move", "dnd-none": "forbidden",
    "question_arrow": "help", "left_ptr_help": "help", "whats_this": "help",
    "pencil": "color-picker",
    "left_side": "w-resize", "right_side": "e-resize", "top_side": "n-resize", "bottom_side": "s-resize",
    "top_left_corner": "nwse-resize", "bottom_right_corner": "nwse-resize", "top_right_corner": "nesw-resize", "bottom_left_corner": "nesw-resize",
    "center_ptr": "default", "right_ptr": "default", "context-menu": "default", "draft": "default", "pirate": "forbidden", "plus": "copy", "circle": "forbidden", "x-cursor": "forbidden",
}

CANONICAL = (
    "default", "hand", "text", "wait", "progress", "crosshair", "ew-resize", "ns-resize",
    "nwse-resize", "nesw-resize", "move", "forbidden", "copy", "help", "zoom-in", "zoom-out",
    "color-picker", "grab", "grabbing", "up-arrow", "down-arrow", "left-arrow", "right-arrow",
)


def point_in_polygon(x: float, y: float, points: list[tuple[float, float]]) -> bool:
    inside = False
    previous = points[-1]
    for current in points:
        x1, y1 = previous
        x2, y2 = current
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
        previous = current
    return inside


def distance_to_segment(x: float, y: float, start: tuple[float, float], end: tuple[float, float]) -> float:
    x1, y1 = start
    x2, y2 = end
    length_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
    if length_sq == 0:
        return math.hypot(x - x1, y - y1)
    ratio = max(0.0, min(1.0, ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / length_sq))
    return math.hypot(x - (x1 + ratio * (x2 - x1)), y - (y1 + ratio * (y2 - y1)))


def pixel(kind: str, x: float, y: float, size: int, frame: int = 0) -> int:
    scale = size / 24
    px, py = x / scale, y / scale
    center = 12.0
    if kind in {"default", "help", "copy"}:
        outer = [(3, 2), (3, 20), (8, 16), (11, 22), (15, 20), (12, 14), (21, 14)]
        inner = [(5, 5), (5, 16), (8.5, 13), (11.5, 19), (13, 18), (10, 12), (17, 12)]
        if point_in_polygon(px, py, inner): return COLORS["fill"]
        if point_in_polygon(px, py, outer): return COLORS["outline"]
        if kind == "help" and 15 <= px <= 20 and 3 <= py <= 8: return COLORS["accent"]
        if kind == "copy" and 15 <= px <= 20 and 15 <= py <= 20: return COLORS["accent"]
    elif kind == "hand":
        if (7 <= px <= 16 and 9 <= py <= 20) or (9 <= px <= 11 and 3 <= py <= 14) or (12 <= px <= 14 and 6 <= py <= 12) or (15 <= px <= 17 and 8 <= py <= 13):
            if 8 <= px <= 15 and 10 <= py <= 18: return COLORS["fill"]
            return COLORS["outline"]
        if 9 <= px <= 11 and 3 <= py <= 6: return COLORS["accent"]
    elif kind == "text":
        if abs(px - center) <= 1.2 or (5 <= px <= 19 and (abs(py - 4) <= 1.2 or abs(py - 20) <= 1.2)):
            return COLORS["accent"] if abs(px - center) <= 1.2 and 8 <= py <= 12 else COLORS["outline"]
    elif kind in {"wait", "progress"}:
        radius = math.hypot(px - center, py - center)
        if 6 <= radius <= 9:
            angle = (math.atan2(py - center, px - center) + math.tau) % math.tau
            phase = frame * math.tau / 12
            distance = (angle - phase + math.tau) % math.tau
            return COLORS["accent"] if distance < math.tau / 4 else COLORS["outline"]
        if kind == "progress" and point_in_polygon(px, py, [(2, 2), (2, 14), (6, 11), (8, 16), (11, 14), (8, 9), (14, 9)]): return COLORS["fill"]
    elif kind == "crosshair":
        if (abs(px - center) <= 1 and 3 <= py <= 21) or (abs(py - center) <= 1 and 3 <= px <= 21):
            return COLORS["accent"] if 10 <= px <= 14 and 10 <= py <= 14 else COLORS["outline"]
    elif kind in {"ew-resize", "ns-resize", "nwse-resize", "nesw-resize", "move"}:
        segments = []
        if kind in {"ew-resize", "move"}: segments.append(((3, 12), (21, 12)))
        if kind in {"ns-resize", "move"}: segments.append(((12, 3), (12, 21)))
        if kind == "nwse-resize": segments.append(((4, 4), (20, 20)))
        if kind == "nesw-resize": segments.append(((20, 4), (4, 20)))
        if any(distance_to_segment(px, py, start, end) <= 1.5 for start, end in segments): return COLORS["outline"]
        if math.hypot(px - center, py - center) <= 2.5: return COLORS["accent"]
    elif kind == "forbidden":
        radius = math.hypot(px - center, py - center)
        if 7 <= radius <= 10 or distance_to_segment(px, py, (6, 6), (18, 18)) <= 1.4:
            return COLORS["accent"] if distance_to_segment(px, py, (6, 6), (18, 18)) <= 1.4 else COLORS["outline"]
    elif kind in {"zoom-in", "zoom-out"}:
        radius = math.hypot(px - 9.5, py - 9.5)
        if 5 <= radius <= 7 or distance_to_segment(px, py, (14, 14), (21, 21)) <= 1.4:
            return COLORS["outline"]
        if abs(py - 9.5) <= 1 and 6 <= px <= 13:
            return COLORS["accent"]
        if kind == "zoom-in" and abs(px - 9.5) <= 1 and 6 <= py <= 13:
            return COLORS["accent"]
    elif kind == "color-picker":
        if distance_to_segment(px, py, (5, 19), (18, 6)) <= 2.2:
            return COLORS["outline"]
        if point_in_polygon(px, py, [(16, 4), (20, 8), (18, 10), (14, 6)]):
            return COLORS["accent"]
        if 3 <= px <= 7 and 18 <= py <= 21:
            return COLORS["accent"]
    elif kind in {"grab", "grabbing"}:
        fingers_top = 5 if kind == "grab" else 8
        if (7 <= px <= 18 and 9 <= py <= 20) or any(
            left <= px <= left + 2 and fingers_top + offset <= py <= 13
            for left, offset in ((7, 3), (10, 0), (13, 1), (16, 3))
        ):
            return COLORS["accent"] if kind == "grabbing" and 9 <= px <= 16 and 11 <= py <= 15 else COLORS["outline"]
    elif kind in {"up-arrow", "down-arrow", "left-arrow", "right-arrow"}:
        polygons = {
            "up-arrow": [(12, 3), (20, 15), (14, 15), (14, 21), (10, 21), (10, 15), (4, 15)],
            "down-arrow": [(12, 21), (4, 9), (10, 9), (10, 3), (14, 3), (14, 9), (20, 9)],
            "left-arrow": [(3, 12), (15, 4), (15, 10), (21, 10), (21, 14), (15, 14), (15, 20)],
            "right-arrow": [(21, 12), (9, 4), (9, 10), (3, 10), (3, 14), (9, 14), (9, 20)],
        }
        if point_in_polygon(px, py, polygons[kind]):
            return COLORS["accent"] if math.hypot(px - center, py - center) <= 2.5 else COLORS["outline"]
    return COLORS["transparent"]


def hotspot(kind: str, size: int) -> tuple[int, int]:
    scale = size / 24
    base = (3, 2) if kind in {"default", "help", "copy"} else (12, 12)
    if kind == "hand": base = (10, 4)
    if kind == "text": base = (12, 12)
    return round(base[0] * scale), round(base[1] * scale)


def image_chunk(kind: str, size: int, frame: int = 0) -> bytes:
    pixels = [pixel(kind, x + 0.5, y + 0.5, size, frame) for y in range(size) for x in range(size)]
    xhot, yhot = hotspot(kind, size)
    delay = 80 if kind in {"wait", "progress"} else 0
    header = struct.pack("<9I", 36, XCURSOR_IMAGE_TYPE, size, 1, size, size, xhot, yhot, delay)
    return header + struct.pack(f"<{len(pixels)}I", *pixels)


def cursor_bytes(kind: str) -> bytes:
    frames = range(12) if kind in {"wait", "progress"} else range(1)
    chunks = [(size, image_chunk(kind, size, frame)) for size in SIZES for frame in frames]
    toc_size = len(chunks) * 12
    position = 16 + toc_size
    tocs = []
    for size, chunk in chunks:
        tocs.append(struct.pack("<3I", XCURSOR_IMAGE_TYPE, size, position))
        position += len(chunk)
    return struct.pack("<4I", 0x72756358, 16, 0x00010000, len(chunks)) + b"".join(tocs) + b"".join(chunk for _, chunk in chunks)


def source_svg(kind: str) -> str:
    glyphs = {
        "default": '<path d="M3 2v18l5-4 3 6 4-2-3-6h9z"/><rect class="accent" x="3" y="2" width="2" height="2"/>',
        "help": '<path d="M3 2v18l5-4 3 6 4-2-3-6h9z"/><path class="accent-line" d="M15 5c0-3 5-3 5 0 0 2-2 2-2 4M18 11v1"/>',
        "copy": '<path d="M3 2v18l5-4 3 6 4-2-3-6h9z"/><path class="accent-line" d="M15 18h6M18 15v6"/>',
        "hand": '<path d="M8 20V9c0-2 3-2 3 0V4c0-2 3-2 3 0v5-2c0-2 3-2 3 0v3-1c0-2 3-2 3 0v7c0 4-3 6-6 6h-2c-2 0-4-1-4-2z"/><path class="accent-line" d="M14 4v5"/>',
        "text": '<path d="M6 4h12M12 4v16M6 20h12"/><path class="accent-line" d="M12 8v5"/>',
        "crosshair": '<path d="M12 3v18M3 12h18"/><rect class="accent" x="10" y="10" width="4" height="4"/>',
        "ew-resize": '<path d="M3 12h18M3 12l5-5M3 12l5 5M21 12l-5-5M21 12l-5 5"/><circle class="accent" cx="12" cy="12" r="2"/>',
        "ns-resize": '<path d="M12 3v18M12 3L7 8M12 3l5 5M12 21l-5-5M12 21l5-5"/><circle class="accent" cx="12" cy="12" r="2"/>',
        "nwse-resize": '<path d="M4 4l16 16M4 4v7M4 4h7M20 20v-7M20 20h-7"/><circle class="accent" cx="12" cy="12" r="2"/>',
        "nesw-resize": '<path d="M20 4L4 20M20 4v7M20 4h-7M4 20v-7M4 20h7"/><circle class="accent" cx="12" cy="12" r="2"/>',
        "move": '<path d="M12 2v20M2 12h20M12 2L8 6M12 2l4 4M12 22l-4-4M12 22l4-4M2 12l4-4M2 12l4 4M22 12l-4-4M22 12l-4 4"/><circle class="accent" cx="12" cy="12" r="2"/>',
        "forbidden": '<circle cx="12" cy="12" r="9"/><path class="accent-line" d="M6 6l12 12"/>',
        "zoom-in": '<circle cx="9.5" cy="9.5" r="6.5"/><path d="M14 14l7 7"/><path class="accent-line" d="M6 9.5h7M9.5 6v7"/>',
        "zoom-out": '<circle cx="9.5" cy="9.5" r="6.5"/><path d="M14 14l7 7"/><path class="accent-line" d="M6 9.5h7"/>',
        "color-picker": '<path d="M5 19L18 6l2 2L7 21H3z"/><path class="accent-line" d="M15 5l4 4M4 20h3"/>',
        "grab": '<path d="M7 19V9c0-2 3-2 3 0V6c0-2 3-2 3 0v3-2c0-2 3-2 3 0v3-1c0-2 3-2 3 0v7c0 4-3 6-7 6-2 0-4-1-5-3z"/>',
        "grabbing": '<path d="M7 19v-8c0-2 3-2 3 0V9c0-2 3-2 3 0v2-1c0-2 3-2 3 0v2-1c0-2 3-2 3 0v5c0 4-3 6-7 6-2 0-4-1-5-3z"/><path class="accent-line" d="M9 13h8"/>',
        "up-arrow": '<path d="M12 3l8 12h-6v6h-4v-6H4z"/>',
        "down-arrow": '<path d="M12 21L4 9h6V3h4v6h6z"/>',
        "left-arrow": '<path d="M3 12l12-8v6h6v4h-6v6z"/>',
        "right-arrow": '<path d="M21 12L9 4v6H3v4h6v6z"/>',
        "wait": '<circle cx="12" cy="12" r="8"/><path class="accent-line" d="M12 4a8 8 0 0 1 6 3"/>',
        "progress": '<path d="M3 2v13l4-3 3 6 3-2-3-6h7z"/><path d="M14 4a7 7 0 1 1-1 13"/><path class="accent-line" d="M14 4a7 7 0 0 1 5 3"/>',
    }
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24">
  <title>NoxForge {kind} cursor source</title>
  <g fill="#141B21" stroke="#E8F0F2" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    {glyphs[kind]}
  </g>
  <style>.accent {{ fill: #A3FF47; stroke: none; }} .accent-line {{ fill: none; stroke: #A3FF47; }}</style>
</svg>
'''


def main() -> None:
    check = "--check" in sys.argv[1:]
    cursor_dir = THEME / "cursors"
    source_dir = THEME / "source"
    cursor_dir.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(parents=True, exist_ok=True)
    data = {kind: cursor_bytes(kind) for kind in CANONICAL}
    outputs: dict[Path, bytes] = {}
    for kind, content in data.items():
        outputs[cursor_dir / kind] = content
        outputs[source_dir / f"{kind}.svg"] = source_svg(kind).encode()
    for alias, target in ALIASES.items():
        while target not in data:
            target = ALIASES[target]
        outputs[cursor_dir / alias] = data[target]
    outputs[THEME / "index.theme"] = (
        "[Icon Theme]\nName=NoxForge\nComment=Original Industrial Precision cursors\n",
    )[0].encode()
    outputs[THEME / "coverage.json"] = (
        json.dumps(
            {
                "schemaVersion": 2,
                "sizes": list(SIZES),
                "canonical": list(CANONICAL),
                "aliases": ALIASES,
                "animations": {"wait": {"frames": 12, "delayMs": 80}, "progress": {"frames": 12, "delayMs": 80}},
            },
            indent=2,
            sort_keys=True,
        ) + "\n"
    ).encode()
    drift = [path for path, content in outputs.items() if not path.exists() or path.read_bytes() != content]
    if check:
        if drift:
            print("Cursor generator drift: " + ", ".join(str(path.relative_to(ROOT)) for path in drift), file=sys.stderr)
            raise SystemExit(1)
        print(f"Verified {len(outputs)} generated cursor artifacts")
        return
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print(f"Generated {len(CANONICAL) + len(ALIASES)} physical Xcursor files at {SIZES}")


if __name__ == "__main__":
    main()
