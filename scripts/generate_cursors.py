#!/usr/bin/env python3
"""Generate original multi-size NoxForge Xcursor files without symlinks."""

from __future__ import annotations

import json
import math
import struct
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
    "fleur": "move", "size_all": "move", "all-scroll": "move", "grab": "move", "grabbing": "move", "openhand": "move", "closedhand": "move",
    "not-allowed": "forbidden", "no-drop": "forbidden", "crossed_circle": "forbidden", "dnd-no-drop": "forbidden",
    "dnd-copy": "copy", "alias": "copy", "dnd-move": "move", "dnd-none": "forbidden",
    "question_arrow": "help", "left_ptr_help": "help", "whats_this": "help",
    "zoom-in": "crosshair", "zoom-out": "crosshair", "color-picker": "crosshair", "pencil": "crosshair",
    "left_side": "w-resize", "right_side": "e-resize", "top_side": "n-resize", "bottom_side": "s-resize",
    "top_left_corner": "nwse-resize", "bottom_right_corner": "nwse-resize", "top_right_corner": "nesw-resize", "bottom_left_corner": "nesw-resize",
    "up-arrow": "ns-resize", "down-arrow": "ns-resize", "left-arrow": "ew-resize", "right-arrow": "ew-resize",
    "center_ptr": "default", "right_ptr": "default", "context-menu": "default", "draft": "default", "pirate": "forbidden", "plus": "copy", "circle": "forbidden", "x-cursor": "forbidden",
}

CANONICAL = (
    "default", "hand", "text", "wait", "progress", "crosshair", "ew-resize", "ns-resize",
    "nwse-resize", "nesw-resize", "move", "forbidden", "copy", "help",
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


def pixel(kind: str, x: float, y: float, size: int) -> int:
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
            angle = math.atan2(py - center, px - center)
            return COLORS["accent"] if angle < -0.3 else COLORS["outline"]
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
    return COLORS["transparent"]


def hotspot(kind: str, size: int) -> tuple[int, int]:
    scale = size / 24
    base = (3, 2) if kind in {"default", "help", "copy"} else (12, 12)
    if kind == "hand": base = (10, 4)
    if kind == "text": base = (12, 12)
    return round(base[0] * scale), round(base[1] * scale)


def image_chunk(kind: str, size: int) -> bytes:
    pixels = [pixel(kind, x + 0.5, y + 0.5, size) for y in range(size) for x in range(size)]
    xhot, yhot = hotspot(kind, size)
    header = struct.pack("<9I", 36, XCURSOR_IMAGE_TYPE, size, 1, size, size, xhot, yhot, 0)
    return header + struct.pack(f"<{len(pixels)}I", *pixels)


def cursor_bytes(kind: str) -> bytes:
    chunks = [image_chunk(kind, size) for size in SIZES]
    toc_size = len(chunks) * 12
    position = 16 + toc_size
    tocs = []
    for size, chunk in zip(SIZES, chunks):
        tocs.append(struct.pack("<3I", XCURSOR_IMAGE_TYPE, size, position))
        position += len(chunk)
    return struct.pack("<4I", 0x72756358, 16, 0x00010000, len(chunks)) + b"".join(tocs) + b"".join(chunks)


def source_svg(kind: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24">
  <title>NoxForge {kind} cursor source</title>
  <rect width="24" height="24" fill="#0E1318"/>
  <path d="M3 2v18l5-4 3 6 4-2-3-6h9z" fill="#141B21" stroke="#E8F0F2" stroke-width="1.5"/>
  <rect x="3" y="2" width="2" height="2" fill="#A3FF47"/>
</svg>
'''


def main() -> None:
    cursor_dir = THEME / "cursors"
    source_dir = THEME / "source"
    cursor_dir.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(parents=True, exist_ok=True)
    data = {kind: cursor_bytes(kind) for kind in CANONICAL}
    for kind, content in data.items():
        (cursor_dir / kind).write_bytes(content)
        (source_dir / f"{kind}.svg").write_text(source_svg(kind), encoding="utf-8", newline="\n")
    for alias, target in ALIASES.items():
        while target not in data:
            target = ALIASES[target]
        (cursor_dir / alias).write_bytes(data[target])
    (THEME / "index.theme").write_text(
        "[Icon Theme]\nName=NoxForge\nComment=Original Industrial Precision cursors\n",
        encoding="utf-8",
        newline="\n",
    )
    (THEME / "coverage.json").write_text(
        json.dumps({"schemaVersion": 1, "sizes": list(SIZES), "canonical": list(CANONICAL), "aliases": ALIASES}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Generated {len(CANONICAL) + len(ALIASES)} physical Xcursor files at {SIZES}")


if __name__ == "__main__":
    main()
