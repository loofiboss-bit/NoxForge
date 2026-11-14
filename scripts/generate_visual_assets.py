#!/usr/bin/env python3
"""Generate original NoxForge Aurorae and representative icon SVGs."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AURORAE = ROOT / "aurorae/io.github.loofiboss.noxforge.desktop"
AURORAE_OBSIDIAN = ROOT / "aurorae/io.github.loofiboss.noxforge.obsidian.desktop"
ICONS = ROOT / "icons/NoxForge"
TOKENS = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))
ARTWORK = json.loads((ROOT / "design/artwork-contract.json").read_text(encoding="utf-8"))
EDGE_POLISH = json.loads((ROOT / "design/edge-polish-contract.json").read_text(encoding="utf-8"))
COLORS = TOKENS["colors"]
CHECK = "--check" in sys.argv[1:]
DRIFT: list[Path] = []

ICON_SPECS = {
    "actions/document-new.svg": (
        '<path class="glass-fill" d="M6 3h8l5 5v12a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/>'
        '<path d="M6 3h8l5 5v12a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zM14 3v5h5"/>'
        '<circle class="accent-soft" cx="12" cy="14" r="4"/>'
        '<path class="accent" d="M9.5 14h5M12 11.5v5"/>'
    ),
    "actions/document-open.svg": (
        '<path class="glass-fill" d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v1H3z"/>'
        '<path class="accent-soft" d="M3 10h18l-2 8.5a1.2 1.2 0 0 1-1.2 1H6.2a1.2 1.2 0 0 1-1.2-1z"/>'
        '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v1M3 10h18l-2 8.5a1.2 1.2 0 0 1-1.2 1H6.2a1.2 1.2 0 0 1-1.2-1z"/>'
        '<path class="accent" d="M9 14.5h6M12.5 12l2.5 2.5-2.5 2.5"/>'
    ),
    "actions/document-save.svg": (
        '<path class="glass-fill" d="M4 4a1 1 0 0 1 1-1h11l4 4v12a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z"/>'
        '<rect class="accent-soft" x="7.5" y="13.5" width="9" height="6.5" rx="1"/>'
        '<path d="M4 4a1 1 0 0 1 1-1h11l4 4v12a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1zM8 3v5h8V3M7.5 13.5h9V20h-9z"/>'
        '<path class="accent" d="M13.5 4.8v2M9.5 16.5h5"/>'
    ),
    "actions/edit-copy.svg": (
        '<rect class="accent-soft" x="8" y="8" width="12" height="12" rx="2.2"/>'
        '<rect x="8" y="8" width="12" height="12" rx="2.2"/>'
        '<path d="M5.5 16H5a1.5 1.5 0 0 1-1.5-1.5V5A1.5 1.5 0 0 1 5 3.5h9.5A1.5 1.5 0 0 1 16 5v.5"/>'
        '<path class="accent" d="M11 12h6M11 15.5h4"/>'
    ),
    "actions/edit-paste.svg": (
        '<path class="glass-fill" d="M5.5 4.5h13a1.5 1.5 0 0 1 1.5 1.5v13.5a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 19.5V6a1.5 1.5 0 0 1 1.5-1.5z"/>'
        '<rect class="accent-soft" x="8" y="10" width="11" height="10" rx="2"/>'
        '<path d="M8 5H5.5A1.5 1.5 0 0 0 4 6.5v12A1.5 1.5 0 0 0 5.5 20H8"/>'
        '<rect x="8.5" y="3" width="7" height="3.2" rx="1.2"/>'
        '<rect class="accent" x="8" y="10" width="11" height="10" rx="2"/>'
    ),
    "actions/edit-delete.svg": (
        '<path class="negative-soft" d="M6.5 6.5h11l-.9 12.5a1.5 1.5 0 0 1-1.5 1.4H8.9a1.5 1.5 0 0 1-1.5-1.4z"/>'
        '<path d="M4.5 6.5h15M9.5 6.5V4.5a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1v2M6.5 6.5l.9 12.5a1.5 1.5 0 0 0 1.5 1.4h6.2a1.5 1.5 0 0 0 1.5-1.4l.9-12.5"/>'
        '<path class="negative" d="M10 10.5v6M14 10.5v6"/>'
    ),
    "actions/system-search.svg": (
        '<circle class="accent-soft" cx="10.5" cy="10.5" r="6.5"/>'
        '<circle cx="10.5" cy="10.5" r="6.5"/>'
        '<path d="M15.4 15.4L20.5 20.5"/>'
        '<path class="accent" d="M8 8.2a3.8 3.8 0 0 1 4.2-.8"/>'
    ),
    "actions/configure.svg": (
        '<circle class="accent-soft" cx="8.5" cy="6" r="2.1"/>'
        '<circle class="accent-soft" cx="15.5" cy="12" r="2.1"/>'
        '<circle class="accent-soft" cx="10.5" cy="18" r="2.1"/>'
        '<path d="M4 6h2.4M10.6 6H20M4 12h9.4M17.6 12H20M4 18h4.4M12.6 18H20"/>'
        '<circle class="accent" cx="8.5" cy="6" r="2.1"/>'
        '<circle cx="15.5" cy="12" r="2.1"/>'
        '<circle class="accent" cx="10.5" cy="18" r="2.1"/>'
    ),
    "places/folder.svg": (
        '<path class="glass-fill" d="M3 6.5A2.5 2.5 0 0 1 5.5 4H9l2 2.2h7.5A2.5 2.5 0 0 1 21 8.7V18a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
        '<rect class="accent-soft" x="3.4" y="9" width="17.2" height="10.6" rx="1.6"/>'
        '<path d="M3 6.5A2.5 2.5 0 0 1 5.5 4H9l2 2.2h7.5A2.5 2.5 0 0 1 21 8.7V18a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
        '<path class="accent" stroke-width="1.4" d="M6 10h12"/>'
    ),
    "places/folder-open.svg": (
        '<path class="glass-fill" d="M3 6.5A2.5 2.5 0 0 1 5.5 4H9l2 2.2h7.5A2.5 2.5 0 0 1 21 8.7V10H3z"/>'
        '<path class="accent-soft" d="M3 10h18l-1.8 8.6a1.5 1.5 0 0 1-1.5 1.2H6.3a1.5 1.5 0 0 1-1.5-1.2z"/>'
        '<path d="M3 6.5A2.5 2.5 0 0 1 5.5 4H9l2 2.2h7.5A2.5 2.5 0 0 1 21 8.7V10M3 10h18l-1.8 8.6a1.5 1.5 0 0 1-1.5 1.2H6.3a1.5 1.5 0 0 1-1.5-1.2z"/>'
        '<path class="accent" stroke-width="1.4" d="M7.5 14h9"/>'
    ),
    "places/user-home.svg": (
        '<path class="glass-fill" d="M3.5 10.8L12 3.5l8.5 7.3v8.2a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2z"/>'
        '<path class="accent-soft" d="M9.5 21v-5.5a2.5 2.5 0 0 1 5 0V21z"/>'
        '<path d="M3.5 10.8L12 3.5l8.5 7.3v8.2a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2z"/>'
        '<path class="accent" d="M9.5 21v-5.5a2.5 2.5 0 0 1 5 0V21"/>'
    ),
    "places/user-desktop.svg": (
        '<rect class="glass-fill" x="3" y="4" width="18" height="12.5" rx="2.4"/>'
        '<rect class="accent-soft" x="6" y="13" width="12" height="2" rx="1"/>'
        '<rect x="3" y="4" width="18" height="12.5" rx="2.4"/>'
        '<path d="M8.5 20h7M12 16.5V20"/>'
        '<path class="accent" d="M7.5 13.8h9"/>'
    ),
    "places/network-workgroup.svg": (
        '<circle class="accent-soft" cx="12" cy="5.5" r="2.5"/>'
        '<circle class="accent-soft" cx="5.5" cy="18" r="2.5"/>'
        '<circle class="accent-soft" cx="18.5" cy="18" r="2.5"/>'
        '<path d="M12 8v3.5M12 11.5l-4.8 4.4M12 11.5l4.8 4.4"/>'
        '<circle class="accent" cx="12" cy="5.5" r="2.5"/>'
        '<circle cx="5.5" cy="18" r="2.5"/><circle cx="18.5" cy="18" r="2.5"/>'
        '<circle class="accent-fill" cx="12" cy="11.5" r="1.4"/>'
    ),
    "devices/computer.svg": (
        '<rect class="glass-fill" x="2.5" y="3.5" width="13.5" height="11" rx="2.2"/>'
        '<rect class="accent-soft" x="17.5" y="7" width="4.5" height="13.5" rx="1.4"/>'
        '<rect x="2.5" y="3.5" width="13.5" height="11" rx="2.2"/>'
        '<path d="M6.5 18.5h5.5M9.2 14.5v4"/>'
        '<rect x="17.5" y="7" width="4.5" height="13.5" rx="1.4"/>'
        '<circle class="accent-fill" cx="19.75" cy="16.8" r="0.9"/>'
        '<path class="accent" stroke-width="1.4" d="M5 7h4"/>'
    ),
    "devices/drive-harddisk.svg": (
        '<rect class="glass-fill" x="3" y="5" width="18" height="14" rx="2.6"/>'
        '<circle class="accent-soft" cx="8.5" cy="12" r="2.8"/>'
        '<rect x="3" y="5" width="18" height="14" rx="2.6"/>'
        '<circle cx="8.5" cy="12" r="2.4"/>'
        '<path d="M13.5 9.5h4.5M13.5 12.5h3"/>'
        '<circle class="accent-fill" cx="17" cy="15.8" r="1.1"/>'
    ),
    "devices/audio-card.svg": (
        '<rect class="glass-fill" x="3.5" y="5" width="14" height="14" rx="2"/>'
        '<rect class="accent-soft" x="6.5" y="8" width="5" height="5" rx="1"/>'
        '<rect x="3.5" y="5" width="14" height="14" rx="2"/>'
        '<path d="M17.5 8.5h3M17.5 12h3M17.5 15.5h3M7 16h5"/>'
        '<rect class="accent" x="6.5" y="8" width="5" height="5" rx="1"/>'
    ),
    "devices/input-keyboard.svg": (
        '<rect class="glass-fill" x="2" y="6" width="20" height="12" rx="2.6"/>'
        '<rect class="accent-soft" x="7" y="13.3" width="10" height="2.4" rx="1"/>'
        '<rect x="2" y="6" width="20" height="12" rx="2.6"/>'
        '<path d="M5.5 10h2M9.5 10h2M13.5 10h2M17.5 10h1.5M5.5 14.5h1.2M17.3 14.5h1.5"/>'
        '<path class="accent" d="M8.5 14.5h7"/>'
    ),
    "devices/input-mouse.svg": (
        '<rect class="glass-fill" x="7" y="2.5" width="10" height="19" rx="5"/>'
        '<rect x="7" y="2.5" width="10" height="19" rx="5"/>'
        '<path d="M7 9.5h10M12 2.5V9.5"/>'
        '<rect class="accent-fill" x="11" y="4.5" width="2" height="3.5" rx="1"/>'
    ),
    "devices/phone.svg": (
        '<rect class="glass-fill" x="6" y="2.5" width="12" height="19" rx="3"/>'
        '<rect class="accent-soft" x="8" y="5" width="8" height="11" rx="1.2"/>'
        '<rect x="6" y="2.5" width="12" height="19" rx="3"/>'
        '<path class="accent" stroke-width="1.4" d="M10.2 4.8h3.6"/>'
        '<circle class="accent-fill" cx="12" cy="18.3" r="1"/>'
    ),
    "status/network-wireless.svg": (
        '<circle class="accent-soft" cx="12" cy="18.8" r="3.2"/>'
        '<path d="M3 8.8a12.8 12.8 0 0 1 18 0M6.2 12a8.4 8.4 0 0 1 11.6 0"/>'
        '<path class="accent" d="M9.2 15.5a4.2 4.2 0 0 1 5.6 0"/>'
        '<circle class="accent-fill" cx="12" cy="18.8" r="1.6"/>'
    ),
    "status/network-wired.svg": (
        '<rect class="glass-fill" x="4" y="4" width="16" height="10" rx="2"/>'
        '<rect class="accent-soft" x="7" y="6.5" width="10" height="5" rx="1"/>'
        '<rect x="4" y="4" width="16" height="10" rx="2"/>'
        '<path d="M12 14v5M7.5 19h9"/>'
        '<path class="accent" d="M8.5 8h7M10 10.5h4"/>'
    ),
    "status/audio-volume-high.svg": (
        '<path class="accent-soft" d="M3.5 9.8A1.5 1.5 0 0 1 5 8.3h2.3l4.2-3.5a.8.8 0 0 1 1.3.6v13.2a.8.8 0 0 1-1.3.6L7.3 15.7H5a1.5 1.5 0 0 1-1.5-1.5z"/>'
        '<path d="M3.5 9.8A1.5 1.5 0 0 1 5 8.3h2.3l4.2-3.5a.8.8 0 0 1 1.3.6v13.2a.8.8 0 0 1-1.3.6L7.3 15.7H5a1.5 1.5 0 0 1-1.5-1.5z"/>'
        '<path class="accent" d="M15.4 9.2a4.2 4.2 0 0 1 0 5.6M17.8 6.8a7.4 7.4 0 0 1 0 10.4M20.2 4.4a10.8 10.8 0 0 1 0 15.2"/>'
    ),
    "status/battery-good.svg": (
        '<rect class="glass-fill" x="2.5" y="6" width="16.5" height="12" rx="3"/>'
        '<rect class="dimmed-fill" x="4.5" y="8" width="12.5" height="8" rx="1.6"/>'
        '<rect x="2.5" y="6" width="16.5" height="12" rx="3"/>'
        '<path d="M19 9.7h1.1a1.4 1.4 0 0 1 1.4 1.4v1.8a1.4 1.4 0 0 1-1.4 1.4H19"/>'
        '<rect class="accent-soft" x="4.5" y="8" width="9.8" height="8" rx="1.5"/>'
        '<rect class="accent-fill" x="4.5" y="8" width="8.5" height="8" rx="1.5"/>'
        '<path class="accent" stroke-width="1.2" stroke-opacity="0.6" d="M5.5 9h6.5"/>'
    ),
    "status/dialog-warning.svg": (
        '<path class="warning-soft" d="M12 3.5L21.5 19.5a1.2 1.2 0 0 1-1 1.8H3.5a1.2 1.2 0 0 1-1-1.8z"/>'
        '<path class="warning" d="M12 3.5L21.5 19.5a1.2 1.2 0 0 1-1 1.8H3.5a1.2 1.2 0 0 1-1-1.8zM12 9v5"/>'
        '<circle class="warning-fill" cx="12" cy="17.2" r="1.15"/>'
    ),
}

CORE_ICON_SPECS = {
    "actions/edit-cut.svg": (
        '<circle class="accent-soft" cx="7" cy="17" r="2.8"/>'
        '<circle class="accent-soft" cx="17" cy="17" r="2.8"/>'
        '<path d="M6.5 5.5l11 11M17.5 5.5l-11 11"/>'
        '<circle class="accent" cx="7" cy="17" r="2.8"/><circle class="accent" cx="17" cy="17" r="2.8"/>'
    ),
    "actions/edit-undo.svg": (
        '<circle class="accent-soft" cx="7.5" cy="11.5" r="3.5"/>'
        '<path class="accent" d="M9 7L4.5 11.5 9 16"/>'
        '<path d="M5 11.5h8.5a5.5 5.5 0 0 1 5.5 5.5v.5"/>'
    ),
    "actions/edit-redo.svg": (
        '<circle class="accent-soft" cx="16.5" cy="11.5" r="3.5"/>'
        '<path class="accent" d="M15 7l4.5 4.5L15 16"/>'
        '<path d="M19 11.5h-8.5A5.5 5.5 0 0 0 5 17v.5"/>'
    ),
    "actions/edit-select-all.svg": (
        '<rect class="glass-fill" x="4" y="4" width="16" height="16" rx="3"/>'
        '<rect x="4" y="4" width="16" height="16" rx="3" stroke-dasharray="3.5 2.5"/>'
        '<rect class="accent-soft" x="7.5" y="7.5" width="9" height="9" rx="1.8"/>'
        '<path class="accent" d="M9.5 12l1.8 1.8L15 10"/>'
    ),
    "actions/go-next.svg": (
        '<circle class="accent-soft" cx="12" cy="12" r="7.5"/>'
        '<path d="M6 12h11.5"/><path class="accent" d="M13 7l5 5-5 5"/>'
    ),
    "actions/list-add.svg": (
        '<path d="M4.5 7h10M4.5 12h8M4.5 17h6.5"/>'
        '<circle class="accent-soft" cx="17.5" cy="15.5" r="4"/>'
        '<path class="accent" d="M17.5 12.5v6M14.5 15.5h6"/>'
    ),
    "actions/media-playback-start.svg": (
        '<path class="accent-soft" d="M7.5 5.3a1 1 0 0 1 1.5-.85l10.2 6.7a1 1 0 0 1 0 1.7L9 19.55a1 1 0 0 1-1.5-.85z"/>'
        '<path class="accent" d="M7.5 5.3a1 1 0 0 1 1.5-.85l10.2 6.7a1 1 0 0 1 0 1.7L9 19.55a1 1 0 0 1-1.5-.85z"/>'
    ),
    "actions/view-refresh.svg": (
        '<circle class="accent-soft" cx="12" cy="12" r="7.5"/>'
        '<path d="M19.5 8.2A8 8 0 1 0 19 16"/>'
        '<path class="accent" d="M19.5 4.2v4h-4"/>'
    ),
    "categories/applications-system.svg": (
        '<rect class="glass-fill" x="3.5" y="3.5" width="7.5" height="7.5" rx="2"/>'
        '<rect class="accent-soft" x="13" y="3.5" width="7.5" height="7.5" rx="2"/>'
        '<rect class="glass-fill" x="3.5" y="13" width="7.5" height="7.5" rx="2"/>'
        '<rect class="glass-fill" x="13" y="13" width="7.5" height="7.5" rx="2"/>'
        '<rect x="3.5" y="3.5" width="7.5" height="7.5" rx="2"/>'
        '<rect class="accent" x="13" y="3.5" width="7.5" height="7.5" rx="2"/>'
        '<rect x="3.5" y="13" width="7.5" height="7.5" rx="2"/>'
        '<rect x="13" y="13" width="7.5" height="7.5" rx="2"/>'
    ),
    "categories/applications-development.svg": (
        '<rect class="glass-fill" x="3" y="4.5" width="18" height="15" rx="2.8"/>'
        '<path d="M8.5 8l-4 4 4 4M15.5 8l4 4-4 4"/>'
        '<path class="accent" d="M13.2 6.5l-2.4 11"/>'
    ),
    "categories/applications-graphics.svg": (
        '<path class="accent-soft" d="M4.5 19.5l3.5-10 8-6 3.5 3.5-6 8z"/>'
        '<path d="M4.5 19.5l3.5-10 8-6 3.5 3.5-6 8zM9.5 9.5l5 5"/>'
        '<circle class="accent-fill" cx="15.5" cy="8.5" r="1.4"/>'
        '<path class="accent" d="M4.5 19.5l3-1"/>'
    ),
    "categories/applications-internet.svg": (
        '<circle class="glass-fill" cx="12" cy="12" r="9"/>'
        '<ellipse class="accent-soft" cx="12" cy="12" rx="4" ry="9"/>'
        '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/>'
        '<ellipse class="accent" cx="12" cy="12" rx="4" ry="9"/>'
    ),
    "categories/applications-multimedia.svg": (
        '<rect class="glass-fill" x="3" y="4.5" width="18" height="15" rx="2.6"/>'
        '<path class="accent-soft" d="M10 8.8l6.2 3.2-6.2 3.2z"/>'
        '<rect x="3" y="4.5" width="18" height="15" rx="2.6"/>'
        '<path class="accent" d="M10 8.8l6.2 3.2-6.2 3.2z"/>'
    ),
    "devices/camera-photo.svg": (
        '<path class="glass-fill" d="M3 8.5a1.5 1.5 0 0 1 1.5-1.5H7l1.8-2.5h6.4L17 7h2.5A1.5 1.5 0 0 1 21 8.5v10a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 18.5z"/>'
        '<circle class="accent-soft" cx="12" cy="13.2" r="3.8"/>'
        '<path d="M3 8.5a1.5 1.5 0 0 1 1.5-1.5H7l1.8-2.5h6.4L17 7h2.5A1.5 1.5 0 0 1 21 8.5v10a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 18.5z"/>'
        '<circle class="accent" cx="12" cy="13.2" r="3.8"/>'
        '<circle class="accent-fill" cx="17.5" cy="9.8" r="0.9"/>'
    ),
    "devices/printer.svg": (
        '<rect class="glass-fill" x="3" y="9" width="18" height="8" rx="2"/>'
        '<rect class="accent-soft" x="6.5" y="14" width="11" height="7" rx="1"/>'
        '<path d="M6.5 9V3.5h11V9M6 17H4a1.5 1.5 0 0 1-1.5-1.5v-5A1.5 1.5 0 0 1 4 9h16a1.5 1.5 0 0 1 1.5 1.5v5A1.5 1.5 0 0 1 20 17h-2"/>'
        '<rect x="6.5" y="14" width="11" height="7" rx="1"/>'
        '<circle class="accent-fill" cx="17.5" cy="11.8" r="1"/>'
    ),
    "devices/audio-headphones.svg": (
        '<rect class="accent-soft" x="3.5" y="13.5" width="4" height="6.5" rx="1.6"/>'
        '<rect class="accent-soft" x="16.5" y="13.5" width="4" height="6.5" rx="1.6"/>'
        '<path d="M4 15v-2.5a8 8 0 0 1 16 0V15"/>'
        '<rect class="accent" x="3.5" y="13.5" width="4" height="6.5" rx="1.6"/>'
        '<rect class="accent" x="16.5" y="13.5" width="4" height="6.5" rx="1.6"/>'
    ),
    "devices/media-removable.svg": (
        '<path class="glass-fill" d="M6.5 10.5h11l2 3v6a1.5 1.5 0 0 1-1.5 1.5H6a1.5 1.5 0 0 1-1.5-1.5v-6z"/>'
        '<rect class="accent-soft" x="7" y="3" width="10" height="7.5" rx="1"/>'
        '<path d="M7 10.5V3h10v7.5M6.5 10.5h11l2 3v6a1.5 1.5 0 0 1-1.5 1.5H6a1.5 1.5 0 0 1-1.5-1.5v-6z"/>'
        '<path class="accent" d="M10 6.5h1.2M12.8 6.5H14"/>'
    ),
    "emblems/emblem-favorite.svg": (
        '<path class="accent-soft" d="M12 3.2l2.7 5.5 6.1.9-4.4 4.3 1 6.1-5.4-2.9-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>'
        '<path class="accent" d="M12 3.2l2.7 5.5 6.1.9-4.4 4.3 1 6.1-5.4-2.9-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>'
    ),
    "emblems/emblem-important.svg": (
        '<circle class="warning-soft" cx="12" cy="12" r="9"/>'
        '<circle cx="12" cy="12" r="9"/><path class="warning" d="M12 7.5v5.5"/>'
        '<circle class="warning-fill" cx="12" cy="16.5" r="1.2"/>'
    ),
    "emblems/emblem-shared.svg": (
        '<circle class="accent-soft" cx="6" cy="12" r="3"/>'
        '<circle class="accent-soft" cx="18" cy="6" r="3"/>'
        '<circle class="accent-soft" cx="18" cy="18" r="3"/>'
        '<path d="M8.6 10.6l6.8-3.2M8.6 13.4l6.8 3.2"/>'
        '<circle class="accent" cx="6" cy="12" r="2.8"/>'
        '<circle cx="18" cy="6" r="2.8"/><circle cx="18" cy="18" r="2.8"/>'
    ),
    "mimetypes/text-x-generic.svg": (
        '<path class="glass-fill" d="M6 3h8.5L19 7.5V20a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/>'
        '<path d="M6 3h8.5L19 7.5V20a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zM14.5 3v4.5H19"/>'
        '<path class="accent" d="M8.5 11.5h7"/><path d="M8.5 14.8h7M8.5 18h4.5"/>'
    ),
    "mimetypes/application-pdf.svg": (
        '<path class="glass-fill" d="M6 3h8.5L19 7.5V20a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/>'
        '<circle class="accent-soft" cx="12" cy="14" r="3.8"/>'
        '<path d="M6 3h8.5L19 7.5V20a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zM14.5 3v4.5H19"/>'
        '<path class="accent" d="M8.5 16.5c2-6 5-6 7 0M9.5 14h5"/>'
    ),
    "mimetypes/package-x-generic.svg": (
        '<path class="glass-fill" d="M3.5 7.5L12 3.5l8.5 4v9L12 20.5l-8.5-4z"/>'
        '<path class="accent-soft" d="M3.5 7.5L12 11.5l8.5-4L12 3.5z"/>'
        '<path d="M3.5 7.5L12 3.5l8.5 4v9L12 20.5l-8.5-4zM3.5 7.5l8.5 4 8.5-4M12 11.5v9"/>'
        '<path class="accent" d="M7.8 5.5l8.4 4"/>'
    ),
    "mimetypes/image-x-generic.svg": (
        '<rect class="glass-fill" x="3" y="4" width="18" height="16" rx="2.4"/>'
        '<path class="accent-soft" d="M4.5 18l4.5-4.5 3 2.5 3.5-4.5 4.5 6.5z"/>'
        '<rect x="3" y="4" width="18" height="16" rx="2.4"/>'
        '<circle class="accent-fill" cx="8.2" cy="9" r="1.6"/>'
        '<path d="M4.5 18l4.5-4.5 3 2.5 3.5-4.5 4.5 6.5"/>'
    ),
    "mimetypes/audio-x-generic.svg": (
        '<circle class="accent-soft" cx="6.5" cy="17.5" r="2.8"/>'
        '<circle class="accent-soft" cx="16.5" cy="15.5" r="2.8"/>'
        '<path class="accent" d="M9.3 17.5V6l9.7-2v11.5M9.3 9.8l9.7-2"/>'
        '<circle cx="6.5" cy="17.5" r="2.8"/><circle cx="16.5" cy="15.5" r="2.8"/>'
    ),
    "mimetypes/video-x-generic.svg": (
        '<rect class="glass-fill" x="3" y="5" width="18" height="14" rx="2.4"/>'
        '<path class="accent-soft" d="M10 9l5.5 3-5.5 3z"/>'
        '<rect x="3" y="5" width="18" height="14" rx="2.4"/>'
        '<path d="M3 9h2.5M18.5 9H21M3 15h2.5M18.5 15H21"/>'
        '<path class="accent" d="M10 9l5.5 3-5.5 3z"/>'
    ),
    "places/folder-documents.svg": (
        '<path class="glass-fill" d="M3 6.5A2.5 2.5 0 0 1 5.5 4H9l2 2.2h7.5A2.5 2.5 0 0 1 21 8.7V18a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
        '<rect class="accent-soft" x="3.4" y="9" width="17.2" height="10.6" rx="1.6"/>'
        '<path d="M3 6.5A2.5 2.5 0 0 1 5.5 4H9l2 2.2h7.5A2.5 2.5 0 0 1 21 8.7V18a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
        '<path class="accent" d="M8.5 12.2h7M8.5 15.6h5"/>'
    ),
    "places/user-trash.svg": (
        '<path class="glass-fill" d="M6.5 6.5h11l-.9 12.5a1.5 1.5 0 0 1-1.5 1.4H8.9a1.5 1.5 0 0 1-1.5-1.4z"/>'
        '<path d="M4.5 6.5h15M9.5 6.5V4.5a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1v2M6.5 6.5l.9 12.5a1.5 1.5 0 0 0 1.5 1.4h6.2a1.5 1.5 0 0 0 1.5-1.4l.9-12.5"/>'
        '<path class="accent" d="M10 10.5v6M14 10.5v6"/>'
    ),
    "preferences/preferences-system.svg": (
        '<circle class="accent-soft" cx="8.5" cy="6" r="2.1"/>'
        '<circle class="accent-soft" cx="15.5" cy="12" r="2.1"/>'
        '<circle class="accent-soft" cx="10.5" cy="18" r="2.1"/>'
        '<path d="M4 6h2.4M10.6 6H20M4 12h9.4M17.6 12H20M4 18h4.4M12.6 18H20"/>'
        '<circle class="accent" cx="8.5" cy="6" r="2.1"/>'
        '<circle cx="15.5" cy="12" r="2.1"/>'
        '<circle class="accent" cx="10.5" cy="18" r="2.1"/>'
    ),
    "preferences/preferences-desktop-theme.svg": (
        '<rect class="glass-fill" x="3" y="4" width="18" height="13.5" rx="2.4"/>'
        '<rect class="accent-soft" x="5.5" y="7" width="13" height="3.2" rx="1"/>'
        '<rect x="3" y="4" width="18" height="13.5" rx="2.4"/>'
        '<path d="M8.5 21h7M12 17.5V21"/>'
        '<path class="accent" d="M6.5 8.6h5M6.5 12.6h9"/>'
    ),
    "preferences/preferences-desktop-display.svg": (
        '<rect class="glass-fill" x="3" y="4" width="18" height="12.5" rx="2.4"/>'
        '<rect class="accent-soft" x="6" y="7" width="7" height="5" rx="1"/>'
        '<rect x="3" y="4" width="18" height="12.5" rx="2.4"/>'
        '<path d="M8.5 20h7M12 16.5V20"/>'
        '<rect class="accent" x="6" y="7" width="7" height="5" rx="1"/>'
    ),
    "preferences/preferences-desktop-keyboard.svg": (
        '<rect class="glass-fill" x="2" y="8" width="20" height="12" rx="2.6"/>'
        '<rect class="accent-soft" x="7" y="15.3" width="10" height="2.4" rx="1"/>'
        '<rect x="2" y="8" width="20" height="12" rx="2.6"/>'
        '<path d="M12 3v5M9 5.5l3 2.5 3-2.5M5.5 12h2M9.5 12h2M13.5 12h2M17.5 12h1.5"/>'
        '<path class="accent" d="M8 16.5h8"/>'
    ),
    "preferences/preferences-system-network.svg": (
        '<circle class="glass-fill" cx="12" cy="12" r="9"/>'
        '<ellipse class="accent-soft" cx="12" cy="12" rx="4" ry="9"/>'
        '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/>'
        '<ellipse class="accent" cx="12" cy="12" rx="4" ry="9"/>'
    ),
    "preferences/preferences-system-power-management.svg": (
        '<circle class="accent-soft" cx="12" cy="12.5" r="8"/>'
        '<path d="M7 6.8a7.8 7.8 0 1 0 10 0"/>'
        '<path class="accent" d="M12 3v7.5"/>'
    ),
    "status/dialog-information.svg": (
        '<circle class="accent-soft" cx="12" cy="12" r="9"/>'
        '<circle cx="12" cy="12" r="9"/>'
        '<path class="accent" d="M12 11v5.5"/>'
        '<circle class="accent-fill" cx="12" cy="7.5" r="1.15"/>'
    ),
    "status/dialog-error.svg": (
        '<circle class="negative-soft" cx="12" cy="12" r="9"/>'
        '<circle class="negative" cx="12" cy="12" r="9"/>'
        '<path class="negative" d="M8.8 8.8l6.4 6.4M15.2 8.8l-6.4 6.4"/>'
    ),
    "status/network-offline.svg": (
        '<path class="dimmed" d="M3 8.8a12.8 12.8 0 0 1 18 0M6.2 12a8.4 8.4 0 0 1 11.6 0M9.2 15.5a4.2 4.2 0 0 1 5.6 0"/>'
        '<circle class="dimmed-fill" cx="12" cy="18.8" r="1.5"/>'
        '<path class="negative" d="M4.5 4.5l15 15"/>'
    ),
    "status/security-high.svg": (
        '<path class="accent-soft" d="M12 3l7.5 2.8v5.8c0 4.8-3.2 7.8-7.5 9.6-4.3-1.8-7.5-4.8-7.5-9.6V5.8z"/>'
        '<path d="M12 3l7.5 2.8v5.8c0 4.8-3.2 7.8-7.5 9.6-4.3-1.8-7.5-4.8-7.5-9.6V5.8z"/>'
        '<path class="accent" d="M8.8 12l2.2 2.2 4.4-4.6"/>'
    ),
    "status/software-update-available.svg": (
        '<circle class="accent-soft" cx="12" cy="11.5" r="7.5"/>'
        '<path class="accent" d="M12 4.5v10M8 10.5l4 4 4-4"/>'
        '<path d="M5.5 19.5h13"/>'
    ),
}

STATE_ICON_SPECS = {
    "actions/go-previous.svg": '<circle class="accent-soft" cx="12" cy="12" r="7.5"/><path d="M18 12H6.5"/><path class="accent" d="M11 7l-5 5 5 5"/>',
    "actions/go-up.svg": '<circle class="accent-soft" cx="12" cy="12" r="7.5"/><path d="M12 18V6.5"/><path class="accent" d="M7 11l5-5 5 5"/>',
    "actions/go-down.svg": '<circle class="accent-soft" cx="12" cy="12" r="7.5"/><path d="M12 6v11.5"/><path class="accent" d="M7 13l5 5 5-5"/>',
    "actions/media-playback-pause.svg": (
        '<rect class="accent-soft" x="6.5" y="5.5" width="3.5" height="13" rx="1"/>'
        '<rect class="accent-soft" x="14" y="5.5" width="3.5" height="13" rx="1"/>'
        '<rect class="accent" x="6.5" y="5.5" width="3.5" height="13" rx="1"/>'
        '<rect x="14" y="5.5" width="3.5" height="13" rx="1"/>'
    ),
    "actions/media-playback-stop.svg": (
        '<rect class="accent-soft" x="6" y="6" width="12" height="12" rx="2.4"/>'
        '<rect x="6" y="6" width="12" height="12" rx="2.4"/>'
        '<rect class="accent-fill" x="9.5" y="9.5" width="5" height="5" rx="1"/>'
    ),
    "actions/media-skip-backward.svg": (
        '<path class="accent-soft" d="M18 5.5l-8.5 6.5 8.5 6.5z"/>'
        '<path d="M18 5.5l-8.5 6.5 8.5 6.5z"/><path class="accent" d="M6 5.5v13"/>'
    ),
    "actions/zoom-in.svg": (
        '<circle class="accent-soft" cx="10.5" cy="10.5" r="6.5"/>'
        '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.4 15.4L20.5 20.5"/>'
        '<path class="accent" d="M7.5 10.5h6M10.5 7.5v6"/>'
    ),
    "actions/zoom-out.svg": (
        '<circle class="accent-soft" cx="10.5" cy="10.5" r="6.5"/>'
        '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.4 15.4L20.5 20.5"/>'
        '<path class="accent" d="M7.5 10.5h6"/>'
    ),
    "applets/bluetooth-active.svg": (
        '<circle class="accent-soft" cx="12" cy="12" r="8.5"/>'
        '<path class="accent" d="M12 3.5v17l4.5-4.25-9-8.5M12 3.5l4.5 4.25-9 8.5"/>'
    ),
    "applets/bluetooth-disabled.svg": (
        '<path class="dimmed" d="M12 3.5v17l4.5-4.25-9-8.5M12 3.5l4.5 4.25-9 8.5"/>'
        '<path class="negative" d="M4.5 4.5l15 15"/>'
    ),
    "applets/redshift-status-day.svg": (
        '<circle class="accent-soft" cx="12" cy="12" r="4.5"/>'
        '<circle cx="12" cy="12" r="4.5"/>'
        '<path class="accent" d="M12 2.5v2.3M12 19.2v2.3M2.5 12h2.3M19.2 12h2.3M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M18.7 5.3l-1.6 1.6M6.9 17.1l-1.6 1.6"/>'
    ),
    "applets/redshift-status-off.svg": (
        '<circle class="dimmed-fill" cx="12" cy="12" r="7"/>'
        '<circle class="dimmed" cx="12" cy="12" r="7"/>'
        '<path class="negative" d="M5 5l14 14"/>'
    ),
    "applets/redshift-status-on.svg": (
        '<path class="accent-soft" d="M17.5 14.5a6.8 6.8 0 1 1-8-9.5 5.6 5.6 0 0 0 8 9.5z"/>'
        '<path class="accent" d="M17.5 14.5a6.8 6.8 0 1 1-8-9.5 5.6 5.6 0 0 0 8 9.5z"/>'
    ),
    "status/audio-volume-low.svg": (
        '<path class="accent-soft" d="M3.5 9.8A1.5 1.5 0 0 1 5 8.3h2.3l4.2-3.5a.8.8 0 0 1 1.3.6v13.2a.8.8 0 0 1-1.3.6L7.3 15.7H5a1.5 1.5 0 0 1-1.5-1.5z"/>'
        '<path d="M3.5 9.8A1.5 1.5 0 0 1 5 8.3h2.3l4.2-3.5a.8.8 0 0 1 1.3.6v13.2a.8.8 0 0 1-1.3.6L7.3 15.7H5a1.5 1.5 0 0 1-1.5-1.5z"/>'
        '<path class="accent" d="M15.4 9.2a4.2 4.2 0 0 1 0 5.6"/>'
    ),
    "status/audio-volume-medium.svg": (
        '<path class="accent-soft" d="M3.5 9.8A1.5 1.5 0 0 1 5 8.3h2.3l4.2-3.5a.8.8 0 0 1 1.3.6v13.2a.8.8 0 0 1-1.3.6L7.3 15.7H5a1.5 1.5 0 0 1-1.5-1.5z"/>'
        '<path d="M3.5 9.8A1.5 1.5 0 0 1 5 8.3h2.3l4.2-3.5a.8.8 0 0 1 1.3.6v13.2a.8.8 0 0 1-1.3.6L7.3 15.7H5a1.5 1.5 0 0 1-1.5-1.5z"/>'
        '<path class="accent" d="M15.4 9.2a4.2 4.2 0 0 1 0 5.6M17.8 6.8a7.4 7.4 0 0 1 0 10.4"/>'
    ),
    "status/audio-volume-muted.svg": (
        '<path class="glass-fill" d="M3.5 9.8A1.5 1.5 0 0 1 5 8.3h2.3l4.2-3.5a.8.8 0 0 1 1.3.6v13.2a.8.8 0 0 1-1.3.6L7.3 15.7H5a1.5 1.5 0 0 1-1.5-1.5z"/>'
        '<path d="M3.5 9.8A1.5 1.5 0 0 1 5 8.3h2.3l4.2-3.5a.8.8 0 0 1 1.3.6v13.2a.8.8 0 0 1-1.3.6L7.3 15.7H5a1.5 1.5 0 0 1-1.5-1.5z"/>'
        '<path class="negative" d="M16 9l5 6M21 9l-5 6"/>'
    ),
    "status/battery-low.svg": (
        '<rect class="glass-fill" x="2.5" y="6" width="16.5" height="12" rx="3"/>'
        '<rect class="warning-soft" x="4.5" y="8" width="12.5" height="8" rx="1.6"/>'
        '<rect x="2.5" y="6" width="16.5" height="12" rx="3"/>'
        '<path d="M19 9.7h1.1a1.4 1.4 0 0 1 1.4 1.4v1.8a1.4 1.4 0 0 1-1.4 1.4H19"/>'
        '<rect class="warning-fill" x="4.5" y="8" width="3.6" height="8" rx="1.4"/>'
    ),
    "status/battery-caution.svg": (
        '<rect class="glass-fill" x="2.5" y="6" width="16.5" height="12" rx="3"/>'
        '<rect class="negative-soft" x="4.5" y="8" width="12.5" height="8" rx="1.6"/>'
        '<rect x="2.5" y="6" width="16.5" height="12" rx="3"/>'
        '<path d="M19 9.7h1.1a1.4 1.4 0 0 1 1.4 1.4v1.8a1.4 1.4 0 0 1-1.4 1.4H19"/>'
        '<path class="negative" d="M10.8 8.8v3.6"/><circle class="negative-fill" cx="10.8" cy="14.8" r="1"/>'
    ),
    "status/battery-charging.svg": (
        '<rect class="glass-fill" x="2.5" y="6" width="16.5" height="12" rx="3"/>'
        '<rect class="accent-soft" x="4.5" y="8" width="12.5" height="8" rx="1.6"/>'
        '<rect x="2.5" y="6" width="16.5" height="12" rx="3"/>'
        '<path d="M19 9.7h1.1a1.4 1.4 0 0 1 1.4 1.4v1.8a1.4 1.4 0 0 1-1.4 1.4H19"/>'
        '<path class="accent-fill" d="M12.2 7.5l-4 5h3l-1 4 4-5.2h-3z"/>'
    ),
    "status/network-wireless-disconnected.svg": (
        '<path class="dimmed" d="M2.17 9.17a13.9 13.9 0 0 1 19.66 0M4.5 11.5a10.6 10.6 0 0 1 15 0M6.84 13.84a7.3 7.3 0 0 1 10.32 0M9.17 16.17a4 4 0 0 1 5.66 0"/>'
        '<circle class="dimmed-fill" cx="12" cy="19" r="1.5"/>'
        '<path class="negative" stroke-width="2" d="M4.5 4.5l15 15"/>'
    ),
    "status/network-wired-disconnected.svg": (
        '<rect class="glass-fill" x="4" y="4" width="16" height="10" rx="2"/>'
        '<rect class="dimmed" x="4" y="4" width="16" height="10" rx="2"/>'
        '<path class="dimmed" d="M12 14v5M7.5 19h9"/>'
        '<path class="negative" d="M4.5 4.5l15 15"/>'
    ),
}

V5_RUNTIME_ICON_SPECS = {
    "actions/application-exit.svg": (
        '<path class="negative-soft" d="M4.5 4.5h6v15h-6z"/>'
        '<path d="M10.5 4.5H5.5A1.5 1.5 0 0 0 4 6v12a1.5 1.5 0 0 0 1.5 1.5h5"/>'
        '<path class="accent" d="M15 8l4 4-4 4M9.5 12H19"/>'
    ),
    "actions/help-about.svg": (
        '<circle class="accent-soft" cx="12" cy="12" r="9"/>'
        '<circle cx="12" cy="12" r="9"/>'
        '<path class="accent" d="M12 11v5.2"/>'
        '<circle class="accent-fill" cx="12" cy="7.5" r="1.1"/>'
    ),
    "actions/help-contents.svg": (
        '<path class="glass-fill" d="M4.5 4.5h5.5a2 2 0 0 1 2 2v12.5a2 2 0 0 0-2-2H4.5z"/>'
        '<path class="accent-soft" d="M19.5 4.5H14a2 2 0 0 0-2 2v12.5a2 2 0 0 1 2-2h5.5z"/>'
        '<path d="M4.5 4.5h5.5a2 2 0 0 1 2 2v12.5a2 2 0 0 0-2-2H4.5z"/>'
        '<path class="accent" d="M19.5 4.5H14a2 2 0 0 0-2 2v12.5a2 2 0 0 1 2-2h5.5z"/>'
    ),
    "actions/system-run.svg": (
        '<rect class="glass-fill" x="3" y="4.5" width="18" height="15" rx="2.6"/>'
        '<rect x="3" y="4.5" width="18" height="15" rx="2.6"/>'
        '<path class="accent" d="M7.5 9l3.2 3-3.2 3"/>'
        '<path class="accent" stroke-width="1.6" d="M12.5 15h4"/>'
    ),
    "actions/view-filter.svg": (
        '<path class="accent-soft" d="M4 5.5h16l-6 6.8V18l-4 2v-7.7z"/>'
        '<path d="M4 5.5h16l-6 6.8V18l-4 2v-7.7z"/>'
        '<path class="accent" d="M7 8.5h10"/>'
    ),
    "actions/view-grid.svg": (
        '<rect class="accent-soft" x="3.5" y="3.5" width="7" height="7" rx="1.6"/>'
        '<rect class="glass-fill" x="13.5" y="3.5" width="7" height="7" rx="1.6"/>'
        '<rect class="glass-fill" x="3.5" y="13.5" width="7" height="7" rx="1.6"/>'
        '<rect class="glass-fill" x="13.5" y="13.5" width="7" height="7" rx="1.6"/>'
        '<rect class="accent" x="3.5" y="3.5" width="7" height="7" rx="1.6"/>'
        '<rect x="13.5" y="3.5" width="7" height="7" rx="1.6"/>'
        '<rect x="3.5" y="13.5" width="7" height="7" rx="1.6"/>'
        '<rect x="13.5" y="13.5" width="7" height="7" rx="1.6"/>'
    ),
    "actions/view-list-tree.svg": (
        '<rect class="accent-soft" x="10.5" y="5.5" width="9.5" height="4.5" rx="1.3"/>'
        '<rect class="glass-fill" x="10.5" y="14" width="9.5" height="4.5" rx="1.3"/>'
        '<path d="M5 4.5V16a.5.5 0 0 0 .5.5h5M5 7.8h5.5"/>'
        '<rect class="accent" x="10.5" y="5.5" width="9.5" height="4.5" rx="1.3"/>'
        '<rect x="10.5" y="14" width="9.5" height="4.5" rx="1.3"/>'
    ),
    "applets/keyboard-layout.svg": (
        '<rect class="glass-fill" x="2" y="6" width="20" height="12" rx="2.6"/>'
        '<rect class="accent-soft" x="6" y="13.3" width="12" height="2.4" rx="1"/>'
        '<rect x="2" y="6" width="20" height="12" rx="2.6"/>'
        '<path d="M5.5 10h2M9.5 10h2M13.5 10h2M17.5 10h1.5"/>'
        '<path class="accent" d="M7 14.5h10"/>'
    ),
    "categories/applications-accessories.svg": (
        '<rect class="glass-fill" x="5.5" y="3.5" width="13" height="17" rx="2.4"/>'
        '<rect class="accent-soft" x="8" y="6.5" width="8" height="4" rx="1"/>'
        '<rect x="5.5" y="3.5" width="13" height="17" rx="2.4"/>'
        '<rect class="accent" x="8" y="6.5" width="8" height="4" rx="1"/>'
        '<path d="M8.5 14h2M13.5 14h2M8.5 17h2M13.5 17h2"/>'
    ),
    "categories/applications-education.svg": (
        '<path class="accent-soft" d="M3 9.2L12 4.5l9 4.7-9 4.8z"/>'
        '<path d="M3 9.2L12 4.5l9 4.7-9 4.8zM6.5 11.4v4.6c3.2 2.4 7.8 2.4 11 0v-4.6"/>'
        '<path class="accent" d="M20 9.8v5"/>'
    ),
    "devices/drive-optical.svg": (
        '<circle class="glass-fill" cx="12" cy="12" r="8.5"/>'
        '<circle class="accent-soft" cx="12" cy="12" r="4"/>'
        '<circle cx="12" cy="12" r="8.5"/>'
        '<circle class="accent" cx="12" cy="12" r="2.6"/>'
        '<path class="accent" d="M12 6.2a5.8 5.8 0 0 1 5.2 3.2"/>'
    ),
    "devices/scanner.svg": (
        '<path class="glass-fill" d="M5 4.5h14l1.5 6.5H3.5zM3.5 11h17v8a1 1 0 0 1-1 1h-15a1 1 0 0 1-1-1z"/>'
        '<rect class="accent-soft" x="6" y="13.5" width="12" height="4" rx="1"/>'
        '<path d="M5 4.5h14l1.5 6.5H3.5zM3.5 11h17v8a1 1 0 0 1-1 1h-15a1 1 0 0 1-1-1z"/>'
        '<path class="accent" d="M6.5 15.5h11"/>'
    ),
    "devices/tablet.svg": (
        '<rect class="glass-fill" x="4" y="2.5" width="16" height="19" rx="2.6"/>'
        '<rect class="accent-soft" x="7" y="5.5" width="10" height="10.5" rx="1.2"/>'
        '<rect x="4" y="2.5" width="16" height="19" rx="2.6"/>'
        '<rect class="accent" x="7" y="5.5" width="10" height="10.5" rx="1.2"/>'
        '<circle class="accent-fill" cx="12" cy="18.6" r="1"/>'
    ),
    "preferences/preferences-desktop-accessibility.svg": (
        '<circle class="accent-soft" cx="12" cy="5.5" r="2.2"/>'
        '<circle class="accent" cx="12" cy="5.5" r="2.1"/>'
        '<path d="M5 9.5h14M12 9.5v4.5M8.2 20.5l3.8-6.5 3.8 6.5"/>'
    ),
    "preferences/preferences-desktop-display-randr.svg": (
        '<rect class="glass-fill" x="3" y="4" width="18" height="12.5" rx="2.4"/>'
        '<rect class="accent-soft" x="6" y="6.8" width="12" height="6.8" rx="1.2"/>'
        '<rect x="3" y="4" width="18" height="12.5" rx="2.4"/>'
        '<path d="M8.5 20h7M12 16.5V20"/>'
        '<path class="accent" d="M7.5 12l3-3M16.5 8.5L13.5 11.5M14.5 8.5h2v2M7.5 10v2h2"/>'
    ),
    "status/printer-error.svg": (
        '<rect class="glass-fill" x="3" y="9" width="18" height="8" rx="2"/>'
        '<path d="M6.5 9V3.5h11V9M6 17H4a1.5 1.5 0 0 1-1.5-1.5v-5A1.5 1.5 0 0 1 4 9h16a1.5 1.5 0 0 1 1.5 1.5v3.5"/>'
        '<path d="M6.5 14h6.5v7H6.5z"/>'
        '<circle class="negative-soft" cx="18" cy="17.5" r="3.5"/>'
        '<path class="negative" d="M16.3 15.8l3.4 3.4M19.7 15.8l-3.4 3.4"/>'
    ),
    "status/software-update-none.svg": (
        '<circle class="accent-soft" cx="12" cy="12" r="8"/>'
        '<path d="M19.5 8.2A8 8 0 1 0 19 16M19.5 4.2v4h-4"/>'
        '<path class="accent" d="M8.8 12.2l2.2 2.2 4.4-4.6"/>'
    ),
    "status/user-available.svg": (
        '<circle class="glass-fill" cx="10" cy="7.8" r="3.6"/>'
        '<circle cx="10" cy="7.8" r="3.6"/><path d="M3.5 20c0-4 2.8-6 6.5-6 2 0 3.7.6 4.9 1.7"/>'
        '<circle class="accent-soft" cx="17.8" cy="17.2" r="3.4"/>'
        '<circle class="accent" cx="17.8" cy="17.2" r="3.2"/>'
        '<path class="accent" stroke-width="1.5" d="M16.4 17.2l1 1 2.2-2.2"/>'
    ),
    "status/user-away.svg": (
        '<circle class="glass-fill" cx="10" cy="7.8" r="3.6"/>'
        '<circle cx="10" cy="7.8" r="3.6"/><path d="M3.5 20c0-4 2.8-6 6.5-6 2 0 3.7.6 4.9 1.7"/>'
        '<circle class="warning-soft" cx="17.8" cy="17.2" r="3.4"/>'
        '<circle class="warning" cx="17.8" cy="17.2" r="3.2"/>'
        '<path class="warning" stroke-width="1.5" d="M17.8 15.4v1.8l1.4 1"/>'
    ),
}

PHASE6_PRIORITY_ICON_SPECS = {
    "actions/dialog-cancel.svg": (
        '<rect class="negative-soft" x="4" y="4" width="16" height="16" rx="4.2"/>'
        '<rect class="negative" x="4" y="4" width="16" height="16" rx="4.2"/>'
        '<path class="negative" d="M8.8 8.8l6.4 6.4M15.2 8.8l-6.4 6.4"/>'
    ),
    "actions/dialog-ok.svg": (
        '<circle class="accent-soft" cx="12" cy="12" r="9"/>'
        '<circle cx="12" cy="12" r="9"/>'
        '<path class="accent" d="M8.2 12.2l2.6 2.6 5.2-5.4"/>'
    ),
    "applets/battery.svg": (
        '<rect class="glass-fill" x="2.5" y="6" width="16.5" height="12" rx="3"/>'
        '<rect class="accent-soft" x="4.5" y="8" width="12.5" height="8" rx="1.6"/>'
        '<rect x="2.5" y="6" width="16.5" height="12" rx="3"/>'
        '<path d="M19 9.7h1.1a1.4 1.4 0 0 1 1.4 1.4v1.8a1.4 1.4 0 0 1-1.4 1.4H19"/>'
        '<rect class="accent-fill" x="5" y="8.6" width="3" height="6.8" rx="0.8"/>'
        '<rect class="accent-fill" x="9.2" y="8.6" width="3" height="6.8" rx="0.8"/>'
        '<rect class="accent-fill" x="13.4" y="8.6" width="3" height="6.8" rx="0.8"/>'
    ),
    "applets/clock.svg": (
        '<circle class="glass-fill" cx="12" cy="12" r="9"/>'
        '<circle class="accent-soft" cx="12" cy="12" r="4"/>'
        '<circle cx="12" cy="12" r="9"/>'
        '<path class="accent" d="M12 7v5l3.5 2"/>'
        '<circle class="accent-fill" cx="12" cy="12" r="1.2"/>'
    ),
    "applets/network.svg": (
        '<circle class="accent-soft" cx="12" cy="12" r="8"/>'
        '<path d="M7.5 16l3.6-6.8M16.5 16l-3.6-6.8M8 17h8"/>'
        '<circle class="accent" cx="12" cy="6.8" r="2.2"/>'
        '<circle cx="6.2" cy="17" r="2.2"/><circle cx="17.8" cy="17" r="2.2"/>'
    ),
    "applets/notifications.svg": (
        '<path class="accent-soft" d="M6 16h12l-1.5-2.8V9.5a4.5 4.5 0 0 0-9 0v3.7z"/>'
        '<path d="M6 16h12l-1.5-2.8V9.5a4.5 4.5 0 0 0-9 0v3.7z"/>'
        '<path class="accent" d="M10 19a2 2 0 0 0 4 0"/>'
    ),
    "applets/systemtray.svg": (
        '<rect class="glass-fill" x="3.5" y="3.5" width="7.5" height="7.5" rx="2"/>'
        '<rect class="glass-fill" x="13" y="3.5" width="7.5" height="7.5" rx="2"/>'
        '<rect class="glass-fill" x="3.5" y="13" width="7.5" height="7.5" rx="2"/>'
        '<rect class="accent-soft" x="13" y="13" width="7.5" height="7.5" rx="2"/>'
        '<rect x="3.5" y="3.5" width="7.5" height="7.5" rx="2"/>'
        '<rect x="13" y="3.5" width="7.5" height="7.5" rx="2"/>'
        '<rect x="3.5" y="13" width="7.5" height="7.5" rx="2"/>'
        '<rect class="accent" x="13" y="13" width="7.5" height="7.5" rx="2"/>'
    ),
    "places/folder-download.svg": (
        '<path class="glass-fill" d="M3 6.5A2.5 2.5 0 0 1 5.5 4H9l2 2.2h7.5A2.5 2.5 0 0 1 21 8.7V18a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
        '<rect class="accent-soft" x="3.4" y="9" width="17.2" height="10.6" rx="1.6"/>'
        '<path d="M3 6.5A2.5 2.5 0 0 1 5.5 4H9l2 2.2h7.5A2.5 2.5 0 0 1 21 8.7V18a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
        '<path class="accent" d="M12 10.2v6M9.2 13.6L12 16.4l2.8-2.8"/>'
    ),
    "places/folder-pictures.svg": (
        '<path class="glass-fill" d="M3 6.5A2.5 2.5 0 0 1 5.5 4H9l2 2.2h7.5A2.5 2.5 0 0 1 21 8.7V18a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
        '<rect class="accent-soft" x="3.4" y="9" width="17.2" height="10.6" rx="1.6"/>'
        '<path d="M3 6.5A2.5 2.5 0 0 1 5.5 4H9l2 2.2h7.5A2.5 2.5 0 0 1 21 8.7V18a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
        '<circle class="accent-fill" cx="8.5" cy="11.8" r="1.2"/>'
        '<path class="accent" d="M6.5 17.2l3.8-3.2 2.4 1.8 2.8-3.4 2.5 4.8"/>'
    ),
    "places/folder-videos.svg": (
        '<path class="glass-fill" d="M3 6.5A2.5 2.5 0 0 1 5.5 4H9l2 2.2h7.5A2.5 2.5 0 0 1 21 8.7V18a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
        '<rect class="accent-soft" x="3.4" y="9" width="17.2" height="10.6" rx="1.6"/>'
        '<path d="M3 6.5A2.5 2.5 0 0 1 5.5 4H9l2 2.2h7.5A2.5 2.5 0 0 1 21 8.7V18a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
        '<path class="accent" d="M10 11l5.2 2.8-5.2 2.8z"/>'
    ),
    "preferences/preferences-desktop-color.svg": (
        '<circle class="glass-fill" cx="12" cy="12" r="9"/>'
        '<circle class="accent-soft" cx="15" cy="14.5" r="3"/>'
        '<path d="M12 3a9 9 0 1 0 0 18c1.6 0 2.5-.9 2.5-2.1 0-.7-.3-1.3-.3-2 0-1.1.9-1.9 2-1.9h1.6A4.2 4.2 0 0 0 21 12 9 9 0 0 0 12 3z"/>'
        '<circle class="accent-fill" cx="8.5" cy="9" r="1.2"/><circle cx="12.5" cy="7.5" r="1.1"/><circle cx="7.8" cy="13.5" r="1.1"/><circle class="accent" cx="16.2" cy="10.2" r="1.1"/>'
    ),
    "preferences/preferences-desktop-icons.svg": (
        '<rect class="glass-fill" x="3" y="4" width="18" height="16" rx="2.6"/>'
        '<rect class="accent-soft" x="6" y="7" width="4.5" height="4" rx="1"/>'
        '<rect x="3" y="4" width="18" height="16" rx="2.6"/>'
        '<rect class="accent" x="6" y="7" width="4.5" height="4" rx="1"/>'
        '<rect x="13.5" y="7" width="4.5" height="4" rx="1"/>'
        '<rect x="6" y="13.5" width="4.5" height="3.5" rx="1"/>'
        '<rect x="13.5" y="13.5" width="4.5" height="3.5" rx="1"/>'
    ),
    "preferences/preferences-desktop-mouse.svg": (
        '<rect class="glass-fill" x="6.5" y="2.5" width="9.5" height="19" rx="4.75"/>'
        '<rect x="6.5" y="2.5" width="9.5" height="19" rx="4.75"/>'
        '<path d="M6.5 9.5h9.5M11.25 2.5v7"/>'
        '<rect class="accent-fill" x="10.25" y="4.5" width="2" height="3.2" rx="1"/>'
        '<path class="accent" d="M19.5 7v10M18 9l1.5-2 1.5 2M18 15l1.5 2 1.5-2"/>'
    ),
    "preferences/preferences-system-bluetooth.svg": (
        '<circle class="glass-fill" cx="12" cy="12" r="9"/>'
        '<circle class="accent-soft" cx="12" cy="12" r="6"/>'
        '<circle cx="12" cy="12" r="9"/>'
        '<path class="accent" d="M12 6v12l3.8-3.2-7.6-5.6M12 6l3.8 3.2-7.6 5.6"/>'
    ),
    "preferences/preferences-system-sound.svg": (
        '<path class="accent-soft" d="M3.5 9.8A1.5 1.5 0 0 1 5 8.3h2.2l4-3.3a.8.8 0 0 1 1.3.6v12.8a.8.8 0 0 1-1.3.6l-4-3.3H5a1.5 1.5 0 0 1-1.5-1.5z"/>'
        '<path d="M3.5 9.8A1.5 1.5 0 0 1 5 8.3h2.2l4-3.3a.8.8 0 0 1 1.3.6v12.8a.8.8 0 0 1-1.3.6l-4-3.3H5a1.5 1.5 0 0 1-1.5-1.5z"/>'
        '<path d="M16 6.5v11M20 5v14"/>'
        '<circle class="accent-fill" cx="16" cy="10.5" r="1.6"/>'
        '<circle class="accent-fill" cx="20" cy="14" r="1.6"/>'
    ),
}

V7_CORE_ICON_SPECS = {
    "actions/draw-highlight.svg": (
        '<path class="accent-soft" d="M4.5 18.5l9.5-9.5 4.5 4.5-9.5 9.5H4.5z"/>'
        '<path d="M5 18l9-9 4.5 4.5-9 9H5zM14.5 6.5l2-2 3.5 3.5-2 2"/>'
        '<path class="accent" d="M4 21h9"/>'
    ),
    "actions/view-hidden.svg": (
        '<path class="glass-fill" d="M3 12c2.5-4 5.5-6 9-6s6.5 2 9 6c-2.5 4-5.5 6-9 6s-6.5-2-9-6z"/>'
        '<path d="M3 12c2.5-4 5.5-6 9-6s6.5 2 9 6c-2.5 4-5.5 6-9 6s-6.5-2-9-6z"/>'
        '<circle class="accent" cx="12" cy="12" r="2.8"/>'
        '<path class="negative" d="M4.5 4.5l15 15"/>'
    ),
    "actions/tools-report-bug.svg": (
        '<rect class="accent-soft" x="8" y="8" width="8" height="11" rx="4"/>'
        '<rect x="8" y="8" width="8" height="11" rx="4"/>'
        '<path d="M10 8V5.5a2 2 0 0 1 4 0V8M4.5 11.5H8M16 11.5h3.5M4.5 15.5H8M16 15.5h3.5M6 19.5l2.5-1.5M18 19.5l-2.5-1.5"/>'
        '<path class="accent" d="M12 11v5"/>'
    ),
    "actions/system-suspend.svg": (
        '<path class="accent-soft" d="M17.5 14.8a7.4 7.4 0 1 1-9.3-10A6.4 6.4 0 0 0 17.5 14.8z"/>'
        '<path class="accent" d="M17.5 14.8a7.4 7.4 0 1 1-9.3-10A6.4 6.4 0 0 0 17.5 14.8z"/>'
    ),
    "actions/system-reboot.svg": (
        '<circle class="accent-soft" cx="12" cy="12" r="7.5"/>'
        '<path d="M19.5 8.2A8 8 0 1 0 19 16"/>'
        '<path class="accent" d="M19.5 4.2v4h-4"/><circle class="accent-fill" cx="12" cy="12" r="1.4"/>'
    ),
    "actions/system-shutdown.svg": (
        '<circle class="negative-soft" cx="12" cy="12.5" r="8"/>'
        '<path d="M7 6.8a7.8 7.8 0 1 0 10 0"/>'
        '<path class="negative" d="M12 3v8"/>'
    ),
    "actions/system-lock-screen.svg": (
        '<rect class="glass-fill" x="5" y="10.5" width="14" height="10" rx="2.4"/>'
        '<rect x="5" y="10.5" width="14" height="10" rx="2.4"/>'
        '<path d="M8.5 10.5V7.5a3.5 3.5 0 0 1 7 0v3"/>'
        '<circle class="accent-soft" cx="12" cy="15.5" r="2.2"/>'
        '<path class="accent" d="M12 14.5v2.2"/>'
    ),
    "actions/system-log-out.svg": (
        '<rect class="accent-soft" x="4" y="4.5" width="6.5" height="15" rx="1.2"/>'
        '<path d="M10.5 4.5H5.5A1.5 1.5 0 0 0 4 6v12a1.5 1.5 0 0 0 1.5 1.5h5"/>'
        '<path class="accent" d="M15 8l4 4-4 4M9.5 12H19"/>'
    ),
}

V15_ICON_SPECS = {
    "status/network-wireless-connected-75.svg": (
        '<circle class="accent-soft" cx="12" cy="19" r="3.1"/>'
        '<path class="dimmed" d="M2.17 9.17a13.9 13.9 0 0 1 19.66 0"/>'
        '<path class="accent" d="M4.5 11.5a10.6 10.6 0 0 1 15 0M6.84 13.84a7.3 7.3 0 0 1 10.32 0M9.17 16.17a4 4 0 0 1 5.66 0"/>'
        '<circle class="accent-fill" cx="12" cy="19" r="1.55"/>'
    ),
    "status/network-wireless-connected-50.svg": (
        '<circle class="accent-soft" cx="12" cy="19" r="3.1"/>'
        '<path class="dimmed" d="M2.17 9.17a13.9 13.9 0 0 1 19.66 0M4.5 11.5a10.6 10.6 0 0 1 15 0"/>'
        '<path class="accent" d="M6.84 13.84a7.3 7.3 0 0 1 10.32 0M9.17 16.17a4 4 0 0 1 5.66 0"/>'
        '<circle class="accent-fill" cx="12" cy="19" r="1.55"/>'
    ),
    "status/network-wireless-connected-25.svg": (
        '<circle class="accent-soft" cx="12" cy="19" r="3.1"/>'
        '<path class="dimmed" d="M2.17 9.17a13.9 13.9 0 0 1 19.66 0M4.5 11.5a10.6 10.6 0 0 1 15 0M6.84 13.84a7.3 7.3 0 0 1 10.32 0"/>'
        '<path class="accent" d="M9.17 16.17a4 4 0 0 1 5.66 0"/>'
        '<circle class="accent-fill" cx="12" cy="19" r="1.55"/>'
    ),
    "status/network-wireless-connected-00.svg": (
        '<circle class="negative-soft" cx="12" cy="19" r="3.1"/>'
        '<path class="dimmed" d="M2.17 9.17a13.9 13.9 0 0 1 19.66 0M4.5 11.5a10.6 10.6 0 0 1 15 0M6.84 13.84a7.3 7.3 0 0 1 10.32 0M9.17 16.17a4 4 0 0 1 5.66 0"/>'
        '<circle class="negative-fill" cx="12" cy="19" r="1.55"/>'
    ),
    "status/network-wireless-acquiring.svg": (
        '<path class="dimmed nf-wave-3" d="M2.17 9.17a13.9 13.9 0 0 1 19.66 0"/>'
        '<path class="accent nf-wave-2" d="M6.84 13.84a7.3 7.3 0 0 1 10.32 0"/>'
        '<path class="dimmed nf-wave-1" d="M9.17 16.17a4 4 0 0 1 5.66 0"/>'
        '<circle class="accent-fill" cx="12" cy="19" r="1.55"/>'
    ),
    "status/network-wireless-locked.svg": (
        '<path d="M2.17 9.17a13.9 13.9 0 0 1 19.66 0M4.5 11.5a10.6 10.6 0 0 1 15 0M6.84 13.84a7.3 7.3 0 0 1 8.6 0"/>'
        '<circle class="accent-fill" cx="12" cy="19" r="1.55"/>'
        '<rect class="warning-soft" x="16" y="16" width="6" height="5" rx="1.2"/>'
        '<rect class="warning" x="16" y="16" width="6" height="5" rx="1.2"/>'
        '<path class="warning" d="M17.5 16v-1.8a1.5 1.5 0 0 1 3 0V16"/>'
    ),
    "status/network-wireless-hotspot.svg": (
        '<circle class="accent-soft" cx="12" cy="8.5" r="2.5"/>'
        '<path d="M12 10v8M9 18h6"/><path class="accent" d="M7.2 9.5a6.5 6.5 0 0 0 0 7M16.8 9.5a6.5 6.5 0 0 1 0 7"/>'
        '<path d="M4.2 7a10 10 0 0 0 0 12M19.8 7a10 10 0 0 1 0 12"/>'
        '<circle class="accent-fill" cx="12" cy="8.5" r="1.6"/>'
    ),
    "status/battery-000.svg": (
        '<rect class="glass-fill" x="2.5" y="6" width="16.5" height="12" rx="3"/>'
        '<rect class="negative-soft" x="4.5" y="8" width="12.5" height="8" rx="1.6"/>'
        '<rect x="2.5" y="6" width="16.5" height="12" rx="3"/>'
        '<path d="M19 9.7h1.1a1.4 1.4 0 0 1 1.4 1.4v1.8a1.4 1.4 0 0 1-1.4 1.4H19"/>'
        '<path class="negative" d="M10.8 8.8v3.6"/><circle class="negative-fill" cx="10.8" cy="14.8" r="1"/>'
    ),
    "status/battery-100.svg": (
        '<rect class="glass-fill" x="2.5" y="6" width="16.5" height="12" rx="3"/>'
        '<rect class="accent-soft" x="4.5" y="8" width="12.5" height="8" rx="1.6"/>'
        '<rect x="2.5" y="6" width="16.5" height="12" rx="3"/>'
        '<path d="M19 9.7h1.1a1.4 1.4 0 0 1 1.4 1.4v1.8a1.4 1.4 0 0 1-1.4 1.4H19"/>'
        '<rect class="accent-fill" x="4.5" y="8" width="12.5" height="8" rx="1.5"/>'
        '<path class="accent" stroke-width="1.2" stroke-opacity="0.6" d="M5.5 9h10.5"/>'
    ),
}


def _level_class(pct: int, *, fill: bool = False) -> str:
    suffix = "-fill" if fill else ""
    if pct <= 10:
        return f"ColorScheme-NegativeText negative{suffix}"
    if pct <= 20:
        return f"ColorScheme-NeutralText warning{suffix}"
    return f"ColorScheme-Highlight accent{suffix}"


def _build_v20_battery_specs() -> dict[str, str]:
    specs: dict[str, str] = {}
    shell = (
        '<rect class="glass-fill" x="2.5" y="6" width="16.5" height="12" rx="3"/>'
        '<rect class="dimmed-fill" x="4.5" y="8" width="12.5" height="8" rx="1.6"/>'
        '<rect x="2.5" y="6" width="16.5" height="12" rx="3"/>'
        '<path d="M19 9.7h1.1a1.4 1.4 0 0 1 1.4 1.4v1.8a1.4 1.4 0 0 1-1.4 1.4H19"/>'
    )
    bolt_anim = (
        '<path class="ColorScheme-Highlight accent nf-pulse" stroke-width="1.6" d="M12.4 8.1l-3.1 4h2.9l-1 3.9 3.4-4.3h-2.8z">'
        '<animate attributeName="opacity" values="1;0.45;1" dur="1.4s" repeatCount="indefinite"/></path>'
    )
    sym_mark = '<path class="symbolic-ring" d="M5 19.8h11.5"/>'
    for pct in range(0, 101, 10):
        tag = f"{pct:03d}"
        cls_fill = _level_class(pct, fill=True)
        cls_stroke = _level_class(pct, fill=False)
        soft_cls = "negative-soft" if pct <= 10 else ("warning-soft" if pct <= 20 else "accent-soft")
        bar_w = round(pct * 12.5 / 100, 2)
        if pct == 0:
            bar = (
                '<rect class="negative-soft" x="4.5" y="8" width="12.5" height="8" rx="1.6"/>'
                '<path class="ColorScheme-NegativeText negative" d="M10.8 8.8v3.6"/>'
                '<circle class="ColorScheme-NegativeText negative-fill" cx="10.8" cy="14.8" r="1"/>'
            )
        else:
            highlight = (
                f'<path class="{cls_stroke}" stroke-width="1.1" stroke-opacity="0.55" d="M5.4 9h{max(0.8, round(bar_w - 1.8, 2))}"/>'
                if pct >= 20
                else ""
            )
            bar = f'<rect class="{soft_cls}" x="4.5" y="8" width="12.5" height="8" rx="1.6"/><rect class="{cls_fill}" x="4.5" y="8" width="{bar_w}" height="8" rx="1.5"/>{highlight}'
        specs[f"status/battery-{tag}.svg"] = shell + bar
        specs[f"status/battery-{tag}-symbolic.svg"] = shell + bar + sym_mark
        chg_bar = (
            f'<rect class="{cls_fill}" x="4.5" y="8" width="{bar_w}" height="8" rx="1.5" fill-opacity="0.34"/>'
            if pct > 0
            else f'<path class="{cls_stroke}" d="M5.5 15h3"/>'
        )
        specs[f"status/battery-{tag}-charging.svg"] = f'{shell}{chg_bar}{bolt_anim}<path class="{cls_stroke}" stroke-width="1.3" d="M4.8 17h{max(1.2, bar_w)}"/>'
        specs[f"status/battery-{tag}-charging-symbolic.svg"] = f'{shell}{chg_bar}{bolt_anim}{sym_mark}<path class="{cls_stroke}" stroke-width="1.3" d="M4.8 17h{max(1.2, bar_w)}"/>'
        specs[f"status/battery-{tag}-profile-powersave.svg"] = f'{shell}{bar}<path class="ColorScheme-PositiveText accent" d="M15.8 17.5c1-2.6 3-3.2 5.2-3.2-.5 2.1-1.6 3.7-5.2 3.2z"/>'
        specs[f"status/battery-{tag}-profile-balanced.svg"] = f'{shell}{bar}<circle class="ColorScheme-Highlight accent-soft" cx="18.5" cy="18" r="2.8"/><circle class="ColorScheme-Highlight accent-fill" cx="18.5" cy="18" r="1.8"/>'
        specs[f"status/battery-{tag}-profile-performance.svg"] = f'{shell}{bar}<path class="ColorScheme-NeutralText warning" d="M15.5 20l2.5-3.2 2.5 3.2"/>'
    specs["status/battery-charging.svg"] = f'{shell}<rect class="accent-soft" x="4.5" y="8" width="12.5" height="8" rx="1.6"/><rect class="ColorScheme-Highlight accent-fill" x="4.5" y="8" width="7.5" height="8" rx="1.5" fill-opacity="0.38"/>{bolt_anim}'
    specs["status/battery-charging-symbolic.svg"] = specs["status/battery-charging.svg"] + sym_mark
    specs["status/battery-caution-charging.svg"] = f'{shell}<rect class="ColorScheme-NegativeText negative-fill" x="4.5" y="8" width="2.6" height="8" rx="1.2" fill-opacity="0.45"/>{bolt_anim}'
    specs["status/battery-low-charging.svg"] = f'{shell}<rect class="ColorScheme-NeutralText warning-fill" x="4.5" y="8" width="4" height="8" rx="1.2" fill-opacity="0.45"/>{bolt_anim}'
    specs["status/battery-good-charging.svg"] = f'{shell}<rect class="ColorScheme-Highlight accent-fill" x="4.5" y="8" width="10" height="8" rx="1.5" fill-opacity="0.38"/>{bolt_anim}'
    specs["status/battery-full-charging.svg"] = f'{shell}<rect class="ColorScheme-Highlight accent-fill" x="4.5" y="8" width="12.5" height="8" rx="1.5" fill-opacity="0.45"/>{bolt_anim}'
    specs["status/battery-empty.svg"] = shell + '<rect class="negative-soft" x="4.5" y="8" width="12.5" height="8" rx="1.6"/><path class="ColorScheme-NegativeText negative" d="M7 10v4"/>'
    specs["status/battery-empty-symbolic.svg"] = specs["status/battery-empty.svg"] + sym_mark
    specs["status/battery-full.svg"] = (
        f'{shell}<rect class="ColorScheme-Highlight accent-fill" x="4.6" y="8.4" width="2.5" height="7.2" rx="0.8"/>'
        '<rect class="ColorScheme-Highlight accent-fill" x="7.8" y="8.4" width="2.5" height="7.2" rx="0.8"/>'
        '<rect class="ColorScheme-Highlight accent-fill" x="11" y="8.4" width="2.5" height="7.2" rx="0.8"/>'
        '<rect class="ColorScheme-Highlight accent-fill" x="14.2" y="8.4" width="2.5" height="7.2" rx="0.8"/>'
    )
    specs["status/battery-full-symbolic.svg"] = specs["status/battery-full.svg"] + sym_mark
    specs["status/battery-missing.svg"] = shell + '<rect class="negative-soft" x="4.5" y="8" width="12.5" height="8" rx="1.6"/><path class="ColorScheme-NegativeText negative" d="M8.8 10l3.8 4M12.6 10l-3.8 4"/>'
    specs["status/battery-missing-symbolic.svg"] = specs["status/battery-missing.svg"] + sym_mark
    specs["status/battery-ups.svg"] = (
        '<rect class="glass-fill" x="5" y="3" width="14" height="18" rx="2.6"/>'
        '<rect x="5" y="3" width="14" height="18" rx="2.6"/>'
        '<rect class="accent-soft" x="7.5" y="6.2" width="9" height="4" rx="1"/>'
        '<rect class="ColorScheme-Highlight accent-fill" x="8" y="6.8" width="8" height="2.8" rx="0.9"/>'
        '<path class="ColorScheme-Highlight accent" d="M12.3 12.2l-2.3 2.8h4l-2.2 2.8"/>'
    )
    specs["devices/input-mouse-battery.svg"] = (
        '<rect class="glass-fill" x="3" y="4" width="8" height="16" rx="4"/>'
        '<rect x="3" y="4" width="8" height="16" rx="4"/><path d="M7 4v5M3 9h8"/>'
        '<rect class="glass-fill" x="14" y="6" width="7" height="12" rx="1.8"/>'
        '<rect x="14" y="6" width="7" height="12" rx="1.8"/>'
        '<rect class="ColorScheme-Highlight accent-fill" x="15.5" y="8.8" width="4" height="7.4" rx="0.9"/>'
        '<path d="M16 4.2h3"/>'
    )
    specs["devices/input-keyboard-battery.svg"] = (
        '<rect class="glass-fill" x="2" y="10" width="14" height="10" rx="2.2"/>'
        '<rect x="2" y="10" width="14" height="10" rx="2.2"/><path d="M5 14h2M9 14h4M5 17h8"/>'
        '<rect class="glass-fill" x="17.5" y="4" width="4.5" height="10" rx="1.4"/>'
        '<rect x="17.5" y="4" width="4.5" height="10" rx="1.4"/>'
        '<rect class="ColorScheme-Highlight accent-fill" x="18.7" y="7" width="2.1" height="5.2" rx="0.7"/>'
        '<path d="M19 2.5h1.5"/>'
    )
    specs["devices/phone-battery.svg"] = (
        '<rect class="glass-fill" x="3" y="3" width="10" height="18" rx="2.4"/>'
        '<rect x="3" y="3" width="10" height="18" rx="2.4"/><path d="M6.5 6h3"/>'
        '<rect class="glass-fill" x="15.5" y="7" width="6" height="11" rx="1.6"/>'
        '<rect x="15.5" y="7" width="6" height="11" rx="1.6"/>'
        '<rect class="ColorScheme-Highlight accent-fill" x="17" y="9.8" width="3" height="6.2" rx="0.8"/>'
        '<path d="M17.5 5.2h2"/>'
    )
    specs["devices/input-gaming-battery.svg"] = (
        '<path class="glass-fill" d="M4 13a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4l1 5-3-1h-8l-3 1z"/>'
        '<path d="M4 13a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4l1 5-3-1h-8l-3 1z"/><path d="M6.5 13h3M8 11.5v3"/>'
        '<rect class="glass-fill" x="18" y="6" width="4" height="10" rx="1.2"/>'
        '<rect x="18" y="6" width="4" height="10" rx="1.2"/>'
        '<rect class="ColorScheme-Highlight accent-fill" x="19" y="8.8" width="2" height="5.4" rx="0.7"/>'
    )
    specs["devices/preferences-system-bluetooth-battery.svg"] = (
        '<path class="accent" d="M9 5v14l3.8-3.6L5.5 9M9 5l3.8 3.6-7.3 6.4"/>'
        '<rect class="glass-fill" x="16.8" y="6" width="5.2" height="12" rx="1.4"/>'
        '<rect x="16.8" y="6" width="5.2" height="12" rx="1.4"/>'
        '<rect class="ColorScheme-Highlight accent-fill" x="18" y="8.8" width="2.8" height="7.2" rx="0.8"/>'
        '<path d="M18.4 4.2h2"/>'
    )
    return specs


def _wifi_arcs_markup(lit_arcs: int, cls: str, *, dot_cls: str | None = None) -> str:
    arcs = (
        "M9.17 16.17a4 4 0 0 1 5.66 0",
        "M6.84 13.84a7.3 7.3 0 0 1 10.32 0",
        "M4.5 11.5a10.6 10.6 0 0 1 15 0",
        "M2.17 9.17a13.9 13.9 0 0 1 19.66 0",
    )
    parts = []
    for idx, d in enumerate(arcs, start=1):
        c = cls if idx <= lit_arcs else "dimmed"
        parts.append(f'<path class="{c}" d="{d}"/>')
    dc = dot_cls or cls
    parts.append(f'<circle class="{dc}" cx="12" cy="19" r="1.55"/>')
    return "".join(parts)


def _build_v20_wireless_specs() -> dict[str, str]:
    specs: dict[str, str] = {}
    level_map = (
        ("0", 0, "ColorScheme-NegativeText negative", "ColorScheme-NegativeText negative-fill"),
        ("20", 1, "ColorScheme-NeutralText warning", "ColorScheme-NeutralText warning-fill"),
        ("40", 2, "ColorScheme-Highlight accent", "ColorScheme-Highlight accent-fill"),
        ("60", 2, "ColorScheme-Highlight accent", "ColorScheme-Highlight accent-fill"),
        ("80", 3, "ColorScheme-Highlight accent", "ColorScheme-Highlight accent-fill"),
        ("100", 4, "ColorScheme-Highlight accent", "ColorScheme-Highlight accent-fill"),
    )
    lock_badge = (
        '<rect class="warning-soft" x="16.2" y="15.5" width="5.8" height="4.8" rx="1.1"/>'
        '<rect class="ColorScheme-NeutralText warning" x="16.2" y="15.5" width="5.8" height="4.8" rx="1.1"/>'
        '<path class="ColorScheme-NeutralText warning" d="M17.6 15.5v-1.7a1.5 1.5 0 0 1 3 0v1.7"/>'
    )
    limit_badge = '<path class="ColorScheme-NeutralText warning" stroke-width="2" d="M19 13v4"/><circle class="ColorScheme-NeutralText warning-fill" cx="19" cy="19.5" r="1.1"/>'
    conn_ring = '<circle class="accent-soft" cx="12" cy="19" r="3.1"/><path class="ColorScheme-Highlight accent" stroke-width="1.3" d="M9.6 21.4h4.8"/>'
    sym_ring = '<path class="symbolic-ring" d="M8 21.8h8"/>'

    for label, arcs_lit, stroke_cls, dot_cls in level_map:
        base_body = _wifi_arcs_markup(arcs_lit, stroke_cls, dot_cls=dot_cls)
        if label == "60":
            # Ensure 60% differs visually from 40% (adds 3rd dashed outer hint arc)
            base_body = (
                f'<path class="{stroke_cls}" d="M9.17 16.17a4 4 0 0 1 5.66 0"/>'
                f'<path class="{stroke_cls}" d="M6.84 13.84a7.3 7.3 0 0 1 10.32 0"/>'
                f'<path class="{stroke_cls}" stroke-dasharray="3.2 2.2" d="M4.5 11.5a10.6 10.6 0 0 1 15 0"/>'
                f'<path class="dimmed" d="M2.17 9.17a13.9 13.9 0 0 1 19.66 0"/>'
                f'<circle class="{dot_cls}" cx="12" cy="19" r="1.55"/>'
            )
        specs[f"status/network-wireless-{label}.svg"] = base_body
        specs[f"status/network-wireless-{label}-symbolic.svg"] = base_body + sym_ring
        specs[f"status/network-wireless-{label}-locked.svg"] = base_body + lock_badge
        if label != "100":
            conn_tag = label.zfill(2)
            specs[f"status/network-wireless-connected-{conn_tag}.svg"] = base_body + conn_ring
            specs[f"status/network-wireless-connected-{conn_tag}-symbolic.svg"] = base_body + conn_ring + sym_ring
            specs[f"status/network-wireless-connected-{conn_tag}-locked.svg"] = base_body + conn_ring + lock_badge
            specs[f"status/network-wireless-connected-{conn_tag}-limited.svg"] = base_body + conn_ring + limit_badge

    for conn_pct, arcs_lit in (("25", 1), ("50", 2), ("75", 3)):
        b25 = _wifi_arcs_markup(arcs_lit, "ColorScheme-Highlight accent", dot_cls="ColorScheme-Highlight accent-fill")
        specs[f"status/network-wireless-connected-{conn_pct}-symbolic.svg"] = b25 + conn_ring + '<path class="symbolic-ring" d="M6 21.8h12"/>'
    specs["status/network-wireless-connected-100-symbolic.svg"] = _wifi_arcs_markup(4, "ColorScheme-Highlight accent", dot_cls="ColorScheme-Highlight accent-fill") + conn_ring + sym_ring
    specs["status/network-wireless-connected-100-locked.svg"] = _wifi_arcs_markup(4, "ColorScheme-Highlight accent", dot_cls="ColorScheme-Highlight accent-fill") + conn_ring + lock_badge
    specs["status/network-wireless-connected-100-limited.svg"] = _wifi_arcs_markup(4, "ColorScheme-Highlight accent", dot_cls="ColorScheme-Highlight accent-fill") + conn_ring + limit_badge

    sig_levels = (
        ("none", 0, "ColorScheme-NegativeText negative", "ColorScheme-NegativeText negative-fill"),
        ("weak", 1, "ColorScheme-NeutralText warning", "ColorScheme-NeutralText warning-fill"),
        ("ok", 2, "ColorScheme-Highlight accent", "ColorScheme-Highlight accent-fill"),
        ("good", 3, "ColorScheme-Highlight accent", "ColorScheme-Highlight accent-fill"),
        ("excellent", 4, "ColorScheme-Highlight accent", "ColorScheme-Highlight accent-fill"),
    )
    for sig_name, arcs_lit, sc, dc in sig_levels:
        sb = _wifi_arcs_markup(arcs_lit, sc, dot_cls=dc) + '<path class="dimmed" d="M10 21.3h4"/>'
        specs[f"status/network-wireless-signal-{sig_name}.svg"] = sb
        specs[f"status/network-wireless-signal-{sig_name}-symbolic.svg"] = sb + '<circle class="dimmed" cx="4" cy="20" r="0.8"/>'

    specs["status/network-wireless-acquiring.svg"] = (
        '<circle class="accent-soft nf-pulse" cx="12" cy="19" r="3.1"/>'
        '<path class="dimmed nf-wave-3" d="M2.17 9.17a13.9 13.9 0 0 1 19.66 0">'
        '<animate attributeName="opacity" values="0.2;1;0.2" begin="0.4s" dur="1.8s" repeatCount="indefinite"/></path>'
        '<path class="ColorScheme-Highlight accent nf-wave-2" d="M6.84 13.84a7.3 7.3 0 0 1 10.32 0">'
        '<animate attributeName="opacity" values="0.2;1;0.2" begin="0.2s" dur="1.8s" repeatCount="indefinite"/></path>'
        '<path class="ColorScheme-Highlight accent nf-wave-1" d="M9.17 16.17a4 4 0 0 1 5.66 0">'
        '<animate attributeName="opacity" values="0.2;1;0.2" begin="0s" dur="1.8s" repeatCount="indefinite"/></path>'
        '<circle class="ColorScheme-Highlight accent-fill nf-pulse" cx="12" cy="19" r="1.55"/>'
    )
    specs["status/network-wireless-acquiring-symbolic.svg"] = specs["status/network-wireless-acquiring.svg"] + sym_ring
    specs["status/network-wireless-limited.svg"] = _wifi_arcs_markup(3, "ColorScheme-Highlight accent", dot_cls="ColorScheme-Highlight accent-fill") + limit_badge
    specs["status/network-wireless-off.svg"] = _wifi_arcs_markup(0, "dimmed", dot_cls="dimmed") + '<path class="ColorScheme-NegativeText negative" d="M4 4l16 16"/>'
    specs["status/network-wireless-on.svg"] = _wifi_arcs_markup(3, "ColorScheme-Highlight accent", dot_cls="ColorScheme-Highlight accent-fill") + '<path class="ColorScheme-PositiveText accent" d="M16 17l2 2 4-4"/>'
    specs["status/network-wireless-available.svg"] = _wifi_arcs_markup(3, "ColorScheme-Text", dot_cls="ColorScheme-Highlight accent-fill") + '<circle class="ColorScheme-Highlight accent-fill" cx="19" cy="18" r="2"/>'
    specs["status/network-wireless-hotspot-symbolic.svg"] = V15_ICON_SPECS["status/network-wireless-hotspot.svg"] + sym_ring
    specs["status/network-wireless-disconnected-symbolic.svg"] = (
        '<path class="dimmed" d="M2.17 9.17a13.9 13.9 0 0 1 19.66 0M4.5 11.5a10.6 10.6 0 0 1 15 0M6.84 13.84a7.3 7.3 0 0 1 10.32 0M9.17 16.17a4 4 0 0 1 5.66 0"/>'
        '<circle class="dimmed-fill" cx="12" cy="19" r="1.5"/><path class="negative" stroke-width="2" d="M4.5 4.5l15 15"/>'
    ) + sym_ring

    for idx, pct in enumerate((0, 20, 40, 60, 80, 100)):
        bars = []
        for b in range(1, 6):
            x = 3 + (b - 1) * 4
            h = 3.2 + (b - 1) * 3.4
            y = 20 - h
            lit = b <= idx
            c = _level_class(pct, fill=True) if lit else "dimmed-fill"
            bars.append(f'<rect class="{c}" x="{x}" y="{y}" width="2.5" height="{h}" rx="1.1"/>')
        specs[f"status/network-mobile-{pct}.svg"] = "".join(bars)
    specs["status/network-mobile-off.svg"] = specs["status/network-mobile-0.svg"] + '<path class="ColorScheme-NegativeText negative" d="M4 4l16 16"/>'
    specs["status/network-mobile-acquiring.svg"] = specs["status/network-mobile-60.svg"] + '<circle class="accent-soft" cx="6" cy="6" r="3"/><circle class="ColorScheme-Highlight accent-fill nf-pulse" cx="6" cy="6" r="1.8"><animate attributeName="opacity" values="1;0.3;1" dur="1.4s" repeatCount="indefinite"/></circle>'

    specs["status/network-vpn.svg"] = (
        '<path class="accent-soft" d="M12 3l7.5 2.8v5.8c0 4.8-3.2 7.8-7.5 9.6-4.3-1.8-7.5-4.8-7.5-9.6V5.8z"/>'
        '<path d="M12 3l7.5 2.8v5.8c0 4.8-3.2 7.8-7.5 9.6-4.3-1.8-7.5-4.8-7.5-9.6V5.8z"/>'
        '<rect class="ColorScheme-Highlight accent" x="9" y="11" width="6" height="5" rx="1.1"/>'
        '<path class="ColorScheme-Highlight accent" d="M10.5 11V9.5a1.5 1.5 0 0 1 3 0V11"/>'
    )
    specs["status/network-vpn-symbolic.svg"] = specs["status/network-vpn.svg"] + sym_ring
    specs["status/network-vpn-acquiring.svg"] = (
        '<path class="accent-soft" d="M12 3l7.5 2.8v5.8c0 4.8-3.2 7.8-7.5 9.6-4.3-1.8-7.5-4.8-7.5-9.6V5.8z"/>'
        '<path d="M12 3l7.5 2.8v5.8c0 4.8-3.2 7.8-7.5 9.6-4.3-1.8-7.5-4.8-7.5-9.6V5.8z"/>'
        '<circle class="ColorScheme-Highlight accent-fill nf-pulse" cx="9" cy="12" r="1.2"/>'
        '<circle class="ColorScheme-Highlight accent-fill nf-pulse" cx="12" cy="12" r="1.2"/>'
        '<circle class="ColorScheme-Highlight accent-fill nf-pulse" cx="15" cy="12" r="1.2"/>'
        '<animate attributeName="opacity" values="1;0.55;1" dur="1.4s" repeatCount="indefinite"/>'
    )
    specs["status/network-vpn-disconnected.svg"] = '<path class="dimmed" d="M12 3l7.5 2.8v5.8c0 4.8-3.2 7.8-7.5 9.6-4.3-1.8-7.5-4.8-7.5-9.6V5.8z"/><path class="ColorScheme-NegativeText negative" d="M5 5l14 14"/>'
    specs["status/network-flightmode-on.svg"] = '<path class="accent-soft" d="M12 2.5v6.5l8 4v2l-8-2v5l3 2v1l-3-1-3 1v-1l3-2v-5l-8 2v-2l8-4V2.5z"/><path class="ColorScheme-Highlight accent" d="M12 2.5v6.5l8 4v2l-8-2v5l3 2v1l-3-1-3 1v-1l3-2v-5l-8 2v-2l8-4V2.5z"/>'
    specs["status/network-flightmode-off.svg"] = '<path class="dimmed" d="M12 2.5v6.5l8 4v2l-8-2v5l3 2v1l-3-1-3 1v-1l3-2v-5l-8 2v-2l8-4V2.5z"/><path class="ColorScheme-NegativeText negative" d="M4 4l16 16"/>'
    return specs


def _build_v20_audio_brightness_specs() -> dict[str, str]:
    specs: dict[str, str] = {}
    spk_d = "M3.5 9.5A1.5 1.5 0 0 1 5 8h2l4.2-3.4a.8.8 0 0 1 1.3.6v13.6a.8.8 0 0 1-1.3.6L7 16H5a1.5 1.5 0 0 1-1.5-1.5z"
    speaker = f'<path class="glass-fill" d="{spk_d}"/><path d="{spk_d}"/>'
    w1 = "M14.3 9.5a3.8 3.8 0 0 1 0 5"
    w2 = "M16.6 7.5a6.8 6.8 0 0 1 0 9"
    w3 = "M18.8 5.4a9.8 9.8 0 0 1 0 13.2"
    sym_ring = '<path class="symbolic-ring" d="M4.5 18.2h2.5"/>'

    specs["status/audio-volume-muted.svg"] = (
        f'{speaker}<circle class="ColorScheme-NegativeText negative-soft" cx="18" cy="12" r="3.4"/>'
        f'<path class="ColorScheme-NegativeText negative" d="M16.2 10.2l3.6 3.6M19.8 10.2l-3.6 3.6"/>'
    )
    specs["status/audio-volume-low.svg"] = f'{speaker}<path class="ColorScheme-Highlight accent" d="{w1}"/><path class="dimmed" d="{w2}"/><path class="dimmed" d="{w3}"/>'
    specs["status/audio-volume-medium.svg"] = f'{speaker}<path class="ColorScheme-Highlight accent" d="{w1}"/><path class="ColorScheme-Highlight accent" d="{w2}"/><path class="dimmed" d="{w3}"/>'
    specs["status/audio-volume-high.svg"] = f'{speaker}<path class="ColorScheme-Highlight accent" d="{w1}"/><path class="ColorScheme-Highlight accent" d="{w2}"/><path class="ColorScheme-Highlight accent" d="{w3}"/>'
    specs["status/audio-volume-high-warning.svg"] = (
        f'{speaker}<path class="ColorScheme-Highlight accent" d="{w1}"/><path class="ColorScheme-Highlight accent" d="{w2}"/><path class="ColorScheme-NeutralText warning" d="{w3}"/>'
        f'<circle class="ColorScheme-NeutralText warning-soft" cx="12" cy="3.2" r="2.2"/><circle class="ColorScheme-NeutralText warning-fill" cx="12" cy="3.2" r="1.1"/>'
    )
    specs["status/audio-volume-high-danger.svg"] = (
        f'{speaker}<path class="ColorScheme-NegativeText negative" d="{w1}"/><path class="ColorScheme-NegativeText negative" d="{w2}"/><path class="ColorScheme-NegativeText negative" d="{w3}"/>'
        f'<circle class="ColorScheme-NegativeText negative-soft" cx="12" cy="3.2" r="2.2"/><path class="ColorScheme-NegativeText negative" stroke-width="1.8" d="M12 2.1v2.2"/>'
    )

    for suffix in ("muted", "low", "medium", "high"):
        specs[f"status/audio-volume-{suffix}-symbolic.svg"] = specs[f"status/audio-volume-{suffix}.svg"] + sym_ring

    mic_shell = (
        '<rect class="glass-fill" x="9" y="3" width="6" height="10.5" rx="3"/>'
        '<rect x="9" y="3" width="6" height="10.5" rx="3"/>'
        '<path d="M5.8 10.5a6.2 6.2 0 0 0 12.4 0M12 16.7v3.8M8.5 20.5h7"/>'
    )
    specs["status/microphone-sensitivity-muted.svg"] = f'{mic_shell}<path class="ColorScheme-NegativeText negative" d="M4.5 4.5l15 15"/>'
    specs["status/microphone-sensitivity-low.svg"] = (
        f'{mic_shell}<rect class="ColorScheme-Highlight accent-soft" x="10.4" y="8.2" width="3.2" height="3.8" rx="1.6"/>'
        f'<path class="ColorScheme-Highlight accent" d="M11.2 10.1h1.6"/>'
    )
    specs["status/microphone-sensitivity-medium.svg"] = (
        f'{mic_shell}<rect class="ColorScheme-Highlight accent-soft" x="10.4" y="5.5" width="3.2" height="6.5" rx="1.6"/>'
        f'<path class="ColorScheme-Highlight accent" d="M12 6.6v4.4"/>'
    )
    specs["status/microphone-sensitivity-high.svg"] = f'{mic_shell}<rect class="ColorScheme-Highlight accent-fill" x="10.3" y="4.5" width="3.4" height="7.5" rx="1.7"/>'
    for suffix in ("muted", "low", "medium", "high"):
        specs[f"status/microphone-sensitivity-{suffix}-symbolic.svg"] = specs[f"status/microphone-sensitivity-{suffix}.svg"] + sym_ring

    sun_core = '<circle class="glass-fill" cx="12" cy="12" r="4.2"/><circle cx="12" cy="12" r="4.2"/>'
    rays_low = '<path class="dimmed" d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2"/>'
    rays_med = (
        '<circle class="ColorScheme-Highlight accent-soft" cx="12" cy="12" r="5.8"/>'
        '<path class="ColorScheme-Highlight accent" d="M12 2.2v2.4M12 19.4v2.4M2.2 12h2.4M19.4 12h2.4"/>'
        '<path class="dimmed" d="M5.2 5.2l1.7 1.7M17.1 17.1l1.7 1.7M18.8 5.2l-1.7 1.7M6.9 17.1l-1.7 1.7"/>'
    )
    rays_high = (
        '<circle class="ColorScheme-Highlight accent-soft" cx="12" cy="12" r="6.8"/>'
        '<path class="ColorScheme-Highlight accent" d="M12 2v2.8M12 19.2V22M2 12h2.8M19.2 12H22M4.9 4.9l2 2M17.1 17.1l2 2M19.1 4.9l-2 2M6.9 17.1l-2 2"/>'
    )
    specs["status/display-brightness-off.svg"] = '<circle class="dimmed-fill" cx="12" cy="12" r="4.2"/><circle class="dimmed" cx="12" cy="12" r="4.2"/><path class="ColorScheme-NegativeText negative" d="M5 5l14 14"/>'
    specs["status/display-brightness-low.svg"] = sun_core + rays_low
    specs["status/display-brightness-medium.svg"] = sun_core + rays_med
    specs["status/display-brightness-high.svg"] = sun_core + rays_high
    for level in ("off", "low", "medium", "high"):
        specs[f"status/display-brightness-{level}-symbolic.svg"] = specs[f"status/display-brightness-{level}.svg"] + '<circle class="ColorScheme-Highlight accent-fill" cx="12" cy="12" r="1.4"/>'

    specs["applets/brightness-high.svg"] = sun_core + rays_high + '<circle class="ColorScheme-Highlight accent-soft" cx="12" cy="12" r="8.2"/>'
    specs["applets/brightness-high-symbolic.svg"] = specs["applets/brightness-high.svg"] + sym_ring
    specs["applets/brightness-low.svg"] = sun_core + rays_low + '<circle class="dimmed" cx="12" cy="12" r="6.8"/>'
    specs["applets/brightness-low-symbolic.svg"] = specs["applets/brightness-low.svg"] + sym_ring

    kbd_key = '<rect class="glass-fill" x="4" y="15.5" width="16" height="3.5" rx="1.2"/><rect x="4" y="15.5" width="16" height="3.5" rx="1.2"/>'
    specs["status/keyboard-brightness-off.svg"] = '<rect class="dimmed" x="4" y="15.5" width="16" height="3.5" rx="1.2"/><path class="ColorScheme-NegativeText negative" d="M5 5l14 14"/>'
    specs["status/keyboard-brightness-low.svg"] = f'{kbd_key}<path class="dimmed" d="M12 9v2.8M7.5 10.8l1.8 1.8M16.5 10.8l-1.8 1.8"/>'
    specs["status/keyboard-brightness-medium.svg"] = f'{kbd_key}<path class="ColorScheme-Highlight accent" d="M12 7.5v4M6.8 10l2.2 2.2M17.2 10L15 12.2"/>'
    specs["status/keyboard-brightness-high.svg"] = (
        '<path class="ColorScheme-Highlight accent-soft" d="M5 15l7-9 7 9z"/>'
        f'{kbd_key}<path class="ColorScheme-Highlight accent" d="M12 6v5.5M6.2 9.2l2.6 2.6M17.8 9.2l-2.6 2.6M3.5 12.5l2.5 1.2M20.5 12.5l-2.5 1.2"/>'
    )
    return specs


def _build_v20_misc_kinetic_specs() -> dict[str, str]:
    bt_glyph = (
        '<path class="glass-fill" d="M12 4L16.5 8L12 12L16.5 16L12 20z"/>'
        '<path d="M7.5 8L16.5 16L12 20V4L16.5 8L7.5 16"/>'
    )
    return {
        "status/network-bluetooth.svg": bt_glyph + '<circle class="ColorScheme-Highlight accent-soft" cx="12" cy="12" r="9.2"/>',
        "status/network-bluetooth-activated.svg": bt_glyph + '<path class="ColorScheme-Highlight accent" d="M18.2 8.2a6.4 6.4 0 0 1 0 7.6"/><circle class="ColorScheme-Highlight accent-fill" cx="18.2" cy="12" r="1.1"/>',
        "status/network-bluetooth-inactive.svg": '<path class="dimmed" d="M7.5 8L16.5 16L12 20V4L16.5 8L7.5 16"/><path class="ColorScheme-NegativeText negative" d="M4.5 4.5l15 15"/>',
        "status/bluetooth-active.svg": bt_glyph + '<circle class="ColorScheme-Highlight accent-soft" cx="5.2" cy="12" r="2.2"/><circle class="ColorScheme-Highlight accent-fill" cx="5.2" cy="12" r="1.1"/>',
        "status/bluetooth-disabled.svg": '<path class="dimmed" d="M7.5 8L16.5 16L12 20V4L16.5 8L7.5 16"/><path class="ColorScheme-NegativeText negative" d="M5 5l14 14"/>',
        "status/bluetooth-acquiring.svg": (
            bt_glyph
            + '<circle class="ColorScheme-Highlight accent nf-pulse" cx="12" cy="12" r="9.4" stroke-dasharray="3.5 2.5">'
            '<animate attributeName="opacity" values="0.25;1;0.25" dur="1.4s" repeatCount="indefinite"/></circle>'
        ),
        "status/media-playback-playing.svg": (
            '<circle class="glass-fill" cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="9"/>'
            '<path class="ColorScheme-Highlight accent-fill" d="M9.8 8.3l6.8 3.7-6.8 3.7z"/>'
        ),
        "status/software-update-available.svg": (
            '<circle class="ColorScheme-Highlight accent-soft" cx="12" cy="11" r="7.5"/>'
            '<path class="nf-pulse" d="M12 4v10.5M7.5 10.5l4.5 4.5 4.5-4.5"><animateTransform attributeName="transform" type="translate" values="0 -1;0 1;0 -1" dur="1.4s" repeatCount="indefinite"/></path>'
            '<path class="ColorScheme-Highlight accent" d="M5 19h14"/>'
        ),
        "status/software-update-urgent.svg": (
            '<path class="ColorScheme-NeutralText warning-soft" d="M12 3l8 3v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6z"/>'
            '<path class="ColorScheme-NeutralText warning" d="M12 3l8 3v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6z"/>'
            '<path class="ColorScheme-NegativeText negative nf-pulse" stroke-width="2" d="M12 8v5"/><circle class="ColorScheme-NegativeText negative-fill" cx="12" cy="15.8" r="1.2"/>'
        ),
        "animations/process-working.svg": (
            '<g class="nf-spin"><circle class="dimmed" cx="12" cy="12" r="8.2"/>'
            '<circle class="ColorScheme-Highlight accent-soft" cx="12" cy="12" r="2.2"/>'
            '<path class="ColorScheme-Highlight accent" stroke-width="2.1" d="M12 3.8a8.2 8.2 0 0 1 7.6 5.1"/>'
            '<path class="ColorScheme-Highlight accent" opacity="0.45" d="M12 20.2a8.2 8.2 0 0 1-7.6-5.1"/>'
            '<animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1.2s" repeatCount="indefinite"/></g>'
        ),
    }


V20_KINETIC_ICON_SPECS = {
    **_build_v20_battery_specs(),
    **_build_v20_wireless_specs(),
    **_build_v20_audio_brightness_specs(),
    **_build_v20_misc_kinetic_specs(),
}


def process_working_sprite_svg(optical_size: int, frames: int = 16) -> str:
    """Render a vertical KPixmapSequence-compatible sprite sheet (size x size*frames)."""
    height = optical_size * frames
    cx = optical_size / 2.0
    r = round(optical_size * 0.34, 2)
    core_r = 1.3 if optical_size == 16 else 1.7
    step = 360.0 / frames
    stroke_w = 1.9 if optical_size == 16 else 2.1
    frame_groups = []
    for idx in range(frames):
        y_off = idx * optical_size
        angle = round(idx * step, 2)
        frame_groups.append(
            f'  <g transform="translate(0 {y_off})">'
            f'<circle class="dimmed" cx="{cx}" cy="{cx}" r="{r}"/>'
            f'<circle class="ColorScheme-Highlight accent-soft" cx="{cx}" cy="{cx}" r="{core_r}"/>'
            f'<g transform="rotate({angle} {cx} {cx})">'
            f'<path class="ColorScheme-Highlight accent" d="M{cx} {cx - r}a{r} {r} 0 0 1 {r} {r}"/>'
            f'<path class="ColorScheme-Highlight accent" opacity="0.4" d="M{cx} {cx + r}a{r} {r} 0 0 1 -{r} -{r}"/>'
            f'</g></g>'
        )
    body = "\n".join(frame_groups)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{optical_size}" height="{height}" viewBox="0 0 {optical_size} {height}">
  <defs>
    <style id="current-color-scheme" type="text/css">
      .ColorScheme-Text {{ color: {COLORS["textPrimary"]}; }}
      .ColorScheme-Highlight {{ color: {COLORS["accent"]}; }}
      .ColorScheme-NeutralText {{ color: {COLORS["neutral"]}; }}
      .ColorScheme-PositiveText {{ color: {COLORS["accent"]}; }}
      .ColorScheme-NegativeText {{ color: {COLORS["negative"]}; }}
      .accent {{ color: {COLORS["accent"]}; stroke: currentColor; }}
      .accent-soft {{ color: {COLORS["accent"]}; fill: currentColor; fill-opacity: 0.22; stroke: none; }}
      .dimmed {{ opacity: 0.22; stroke: {COLORS["textDisabled"]}; }}
    </style>
  </defs>
  <g fill="none" stroke="currentColor" class="ColorScheme-Text" stroke-width="{stroke_w}" stroke-linecap="round">
{body}
  </g>
</svg>
'''

ICON_ALIASES = {
    "actions/edit-clear.svg": "actions/edit-delete.svg",
    "actions/edit-find.svg": "actions/system-search.svg",
    "actions/edit-select-all.svg": "actions/configure.svg",
    "actions/go-previous.svg": "actions/go-next.svg",
    "actions/go-up.svg": "actions/go-next.svg",
    "actions/go-down.svg": "actions/go-next.svg",
    "actions/list-remove.svg": "actions/list-add.svg",
    "actions/dialog-ok.svg": "status/security-high.svg",
    "actions/dialog-cancel.svg": "status/dialog-error.svg",
    "actions/window-close.svg": "status/dialog-error.svg",
    "actions/media-playback-pause.svg": "actions/media-playback-start.svg",
    "actions/media-playback-stop.svg": "actions/media-playback-start.svg",
    "actions/media-skip-forward.svg": "actions/go-next.svg",
    "actions/media-skip-backward.svg": "actions/go-next.svg",
    "actions/zoom-in.svg": "actions/system-search.svg",
    "actions/zoom-out.svg": "actions/system-search.svg",
    "actions/view-list-icons.svg": "categories/applications-system.svg",
    "actions/view-list-details.svg": "actions/configure.svg",
    "applets/systemtray.svg": "categories/applications-system.svg",
    "applets/clock.svg": "status/battery-good.svg",
    "applets/notifications.svg": "status/dialog-information.svg",
    "applets/network.svg": "status/network-wireless.svg",
    "applets/audio-volume.svg": "status/audio-volume-high.svg",
    "applets/battery.svg": "status/battery-good.svg",
    "applets/audio-volume-high-symbolic.svg": "status/audio-volume-high.svg",
    "applets/battery-full.svg": "status/battery-good.svg",
    "applets/battery-full-symbolic.svg": "status/battery-good.svg",
    "applets/bluetooth-active.svg": "preferences/preferences-system-network.svg",
    "applets/bluetooth-disabled.svg": "preferences/preferences-system-network.svg",
    "applets/camera-on-symbolic.svg": "devices/camera-photo.svg",
    "applets/device-notifier.svg": "devices/media-removable.svg",
    "applets/input-caps-on.svg": "devices/input-keyboard.svg",
    "applets/input-keyboard-virtual.svg": "devices/input-keyboard.svg",
    "applets/kdeconnect-tray.svg": "devices/phone.svg",
    "applets/kdeconnect-tray-symbolic.svg": "devices/phone.svg",
    "applets/klipper.svg": "actions/edit-paste.svg",
    "applets/media-playback-playing.svg": "actions/media-playback-start.svg",
    "applets/plasmavault.svg": "status/security-high.svg",
    "applets/preferences-desktop-display-randr.svg": "places/user-desktop.svg",
    "applets/preferences-desktop-notification-bell.svg": "applets/notifications.svg",
    "applets/redshift-status-day.svg": "places/user-desktop.svg",
    "applets/redshift-status-off.svg": "places/user-desktop.svg",
    "applets/redshift-status-on.svg": "places/user-desktop.svg",
    "applets/speedometer.svg": "preferences/preferences-system-power-management.svg",
    "applets/weather-clear.svg": "status/dialog-information.svg",
    "categories/applications-office.svg": "mimetypes/text-x-generic.svg",
    "categories/applications-utilities.svg": "preferences/preferences-system.svg",
    "categories/preferences-system.svg": "preferences/preferences-system.svg",
    "devices/camera-web.svg": "devices/camera-photo.svg",
    "devices/video-display.svg": "places/user-desktop.svg",
    "devices/audio-input-microphone.svg": "devices/audio-headphones.svg",
    "devices/drive-removable-media.svg": "devices/media-removable.svg",
    "devices/drive-removable-media-usb.svg": "devices/media-removable.svg",
    "devices/network-wired.svg": "status/network-wired.svg",
    "devices/network-wireless.svg": "status/network-wireless.svg",
    "emblems/emblem-readonly.svg": "status/security-high.svg",
    "emblems/emblem-symbolic-link.svg": "places/network-workgroup.svg",
    "emblems/emblem-success.svg": "status/security-high.svg",
    "mimetypes/application-x-archive.svg": "mimetypes/package-x-generic.svg",
    "mimetypes/application-zip.svg": "mimetypes/package-x-generic.svg",
    "mimetypes/application-octet-stream.svg": "mimetypes/package-x-generic.svg",
    "mimetypes/application-vnd.tcpdump.pcap.svg": "mimetypes/package-x-generic.svg",
    "mimetypes/application-x-executable.svg": "categories/applications-development.svg",
    "mimetypes/application-x-shellscript.svg": "categories/applications-development.svg",
    "mimetypes/application-x-desktop.svg": "mimetypes/text-x-generic.svg",
    "mimetypes/audio-flac.svg": "mimetypes/audio-x-generic.svg",
    "mimetypes/text-html.svg": "mimetypes/text-x-generic.svg",
    "mimetypes/text-markdown.svg": "mimetypes/text-x-generic.svg",
    "mimetypes/text-plain.svg": "mimetypes/text-x-generic.svg",
    "mimetypes/text-x-script.svg": "mimetypes/text-x-generic.svg",
    "mimetypes/unknown.svg": "mimetypes/package-x-generic.svg",
    "mimetypes/x-office-document.svg": "mimetypes/text-x-generic.svg",
    "mimetypes/inode-directory.svg": "places/folder.svg",
    "places/folder-download.svg": "places/folder-documents.svg",
    "places/folder-pictures.svg": "places/folder-documents.svg",
    "places/folder-music.svg": "places/folder-documents.svg",
    "places/folder-videos.svg": "places/folder-documents.svg",
    "places/folder-publicshare.svg": "places/network-workgroup.svg",
    "places/network-server.svg": "places/network-workgroup.svg",
    "places/network-server-database.svg": "devices/drive-harddisk.svg",
    "places/start-here-kde.svg": "categories/applications-system.svg",
    "preferences/preferences-desktop-color.svg": "preferences/preferences-desktop-theme.svg",
    "preferences/preferences-desktop-icons.svg": "preferences/preferences-desktop-theme.svg",
    "preferences/preferences-system-windows.svg": "preferences/preferences-desktop-theme.svg",
    "preferences/preferences-system-bluetooth.svg": "preferences/preferences-system-network.svg",
    "preferences/preferences-system-sound.svg": "devices/audio-card.svg",
    "preferences/preferences-desktop-notification.svg": "status/dialog-information.svg",
    "preferences/preferences-desktop-mouse.svg": "devices/input-mouse.svg",
    "status/audio-volume-low.svg": "status/audio-volume-high.svg",
    "status/audio-volume-medium.svg": "status/audio-volume-high.svg",
    "status/audio-volume-muted.svg": "status/audio-volume-high.svg",
    "status/battery-low.svg": "status/battery-good.svg",
    "status/battery-caution.svg": "status/battery-good.svg",
    "status/battery-charging.svg": "status/battery-good.svg",
    "status/network-wireless-connected-100.svg": "status/network-wireless.svg",
    "status/network-wired-activated.svg": "status/network-wired.svg",
    "status/network-wired-disconnected.svg": "status/network-wired.svg",
    "status/dialog-question.svg": "status/dialog-information.svg",
    "status/dialog-password.svg": "status/security-high.svg",
    "status/task-complete.svg": "status/security-high.svg",
}

# Only names that are actual semantic synonyms remain byte-identical. Every
# broader fallback name receives its own small optical discriminator below.
TRUE_SYNONYM_ALIASES = {
    "actions/edit-clear.svg",
    "actions/edit-find.svg",
    "applets/audio-volume-high-symbolic.svg",
    "applets/battery-full.svg",
    "applets/battery-full-symbolic.svg",
    "applets/camera-on-symbolic.svg",
    "categories/preferences-system.svg",
    "devices/network-wired.svg",
    "devices/network-wireless.svg",
    "mimetypes/inode-directory.svg",
    "status/network-wireless-connected-100.svg",
    "status/network-wired-activated.svg",
}

DUPLICATE_ALLOWLIST = (
    ("actions/configure.svg", "categories/preferences-system.svg", "preferences/preferences-system.svg"),
    ("actions/edit-clear.svg", "actions/edit-delete.svg"),
    ("actions/edit-find.svg", "actions/system-search.svg"),
    ("applets/camera-on-symbolic.svg", "devices/camera-photo.svg"),
    ("applets/audio-volume-high-symbolic.svg", "status/audio-volume-high.svg"),
    ("applets/battery-full-symbolic.svg", "applets/battery-full.svg", "status/battery-good.svg"),
    ("categories/applications-internet.svg", "preferences/preferences-system-network.svg"),
    ("devices/network-wired.svg", "status/network-wired-activated.svg", "status/network-wired.svg"),
    ("devices/network-wireless.svg", "status/network-wireless-connected-100.svg", "status/network-wireless.svg"),
    ("mimetypes/inode-directory.svg", "places/folder.svg"),
)


def semantic_variant(body: str, relative: str) -> str:
    """Add a subtle corner precision pip to differentiate closely related aliases."""
    digest = hashlib.sha256(relative.encode()).digest()
    cx = round(20.3 + (digest[0] / 255.0) * 0.8, 3)
    cy = round(2.7 + (digest[1] / 255.0) * 0.8, 3)
    r = round(0.7 + (digest[2] / 255.0) * 0.2, 3)
    halo_r = round(r + 0.75, 3)
    op = round(0.55 + (digest[3] / 255.0) * 0.4, 3)
    return (
        body
        + f'<circle class="ColorScheme-Highlight accent-soft" cx="{cx}" cy="{cy}" r="{halo_r}"/>'
        + f'<circle class="ColorScheme-Highlight accent-fill" cx="{cx}" cy="{cy}" r="{r}" fill-opacity="{op}"/>'
    )


def icon_svg(body: str, optical_size: int | None = None) -> str:
    size = optical_size or 24
    stroke_width = 1.9 if optical_size == 16 else 1.75 if optical_size == 22 else TOKENS["iconography"]["strokeWidth"]
    motion_block = ""
    if "nf-" in body:
        motion_block = '''
  <style id="noxforge-motion" type="text/css">
    @media (prefers-reduced-motion: no-preference) {
      @keyframes nf-pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
      @keyframes nf-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      @keyframes nf-wave { 0%, 100% { opacity: 0.25; } 50% { opacity: 1; } }
      .nf-pulse { animation: nf-pulse 1.4s ease-in-out infinite; }
      .nf-spin { transform-origin: 12px 12px; animation: nf-spin 1.2s linear infinite; }
      .nf-wave-1 { animation: nf-wave 1.8s ease-in-out 0s infinite; }
      .nf-wave-2 { animation: nf-wave 1.8s ease-in-out 0.2s infinite; }
      .nf-wave-3 { animation: nf-wave 1.8s ease-in-out 0.4s infinite; }
    }
  </style>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
  <defs>
    <style id="current-color-scheme" type="text/css">
      .ColorScheme-Text {{ color: {COLORS["textPrimary"]}; }}
      .ColorScheme-Highlight {{ color: {COLORS["accent"]}; }}
      .ColorScheme-NeutralText {{ color: {COLORS["neutral"]}; }}
      .ColorScheme-PositiveText {{ color: {COLORS["accent"]}; }}
      .ColorScheme-NegativeText {{ color: {COLORS["negative"]}; }}
      .glass-fill {{ color: {COLORS["textPrimary"]}; fill: currentColor; fill-opacity: 0.10; stroke: none; }}
      .accent {{ color: {COLORS["accent"]}; stroke: currentColor; }}
      .accent-fill {{ color: {COLORS["accent"]}; fill: currentColor; stroke: none; }}
      .accent-soft {{ color: {COLORS["accent"]}; fill: currentColor; fill-opacity: 0.18; stroke: none; }}
      .dimmed {{ opacity: 0.25; stroke: currentColor; }}
      .dimmed-fill {{ color: {COLORS["textPrimary"]}; fill: currentColor; fill-opacity: 0.14; stroke: none; }}
      .symbolic-ring {{ opacity: 0.45; stroke: currentColor; stroke-width: 1; }}
      .warning {{ color: {COLORS["neutral"]}; stroke: currentColor; }}
      .warning-fill {{ color: {COLORS["neutral"]}; fill: currentColor; stroke: none; }}
      .warning-soft {{ color: {COLORS["neutral"]}; fill: currentColor; fill-opacity: 0.18; stroke: none; }}
      .negative {{ color: {COLORS["negative"]}; stroke: currentColor; }}
      .negative-fill {{ color: {COLORS["negative"]}; fill: currentColor; stroke: none; }}
      .negative-soft {{ color: {COLORS["negative"]}; fill: currentColor; fill-opacity: 0.18; stroke: none; }}
    </style>{motion_block}
  </defs>
  <g fill="none" stroke="currentColor" class="ColorScheme-Text" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round">
    {body}
  </g>
</svg>
'''


def decoration_frame(prefix: str, x: int, y: int, css_class: str, opacity: float, *, active: bool) -> str:
    def name(position: str) -> str:
        return f"{prefix}-{position}"

    attr = f'class="{css_class}" fill="currentColor" fill-opacity="{opacity:g}"'
    border_class = "NoxForge-EdgeHighlight" if active else "NoxForge-OutlineMuted"
    b_fill = f'class="{border_class}" fill="currentColor"'
    b_attr = f'class="{border_class}" stroke="currentColor" fill="none" stroke-width="1"'

    top = (
        f'<g id="{name("top")}">'
        f'<rect x="{x + 6}" y="{y}" width="28" height="6" {attr}/>'
        f'<rect x="{x + 6}" y="{y}" width="28" height="1" {b_fill}/>'
    )
    if active:
        rail = EDGE_POLISH["aurorae"]
        top += (
            f'<path d="M{x + 8} {y + 1}h{rail["activeRailLength"]}" '
            'class="ColorScheme-Highlight" stroke="currentColor" '
            f'stroke-width="{rail["activeRailThickness"]}"/>'
        )
    top += "</g>"

    topleft = (
        f'<g id="{name("topleft")}">'
        f'<path d="M{x + 4} {y}H{x + 6}V{y + 6}H{x}V{y + 4}Z" {attr}/>'
        f'<rect x="{x + 4}" y="{y}" width="2" height="1" {b_fill}/>'
        f'<line x1="{x + 4}" y1="{y}" x2="{x}" y2="{y + 4}" {b_attr}/>'
        f'<rect x="{x}" y="{y + 4}" width="1" height="2" {b_fill}/>'
        f'</g>'
    )
    topright = (
        f'<g id="{name("topright")}">'
        f'<path d="M{x + 34} {y}A6 6 0 0 1 {x + 40} {y + 6}H{x + 34}Z" {attr}/>'
        f'<path d="M{x + 34} {y + 0.5}A5.5 5.5 0 0 1 {x + 39.5} {y + 6}" {b_attr}/>'
        f'</g>'
    )
    left = (
        f'<g id="{name("left")}">'
        f'<rect x="{x}" y="{y + 6}" width="6" height="28" {attr}/>'
        f'<rect x="{x}" y="{y + 6}" width="1" height="28" {b_fill}/>'
        f'</g>'
    )
    center = f'<rect id="{name("center")}" x="{x + 6}" y="{y + 6}" width="28" height="28" {attr}/>'
    right = (
        f'<g id="{name("right")}">'
        f'<rect x="{x + 34}" y="{y + 6}" width="6" height="28" {attr}/>'
        f'<rect x="{x + 39}" y="{y + 6}" width="1" height="28" {b_fill}/>'
        f'</g>'
    )
    bottomleft = (
        f'<g id="{name("bottomleft")}">'
        f'<path d="M{x} {y + 34}H{x + 6}V{y + 40}A6 6 0 0 1 {x} {y + 34}Z" {attr}/>'
        f'<path d="M{x + 6} {y + 39.5}A5.5 5.5 0 0 1 {x + 0.5} {y + 34}" {b_attr}/>'
        f'</g>'
    )
    bottom = (
        f'<g id="{name("bottom")}">'
        f'<rect x="{x + 6}" y="{y + 34}" width="28" height="6" {attr}/>'
        f'<rect x="{x + 6}" y="{y + 39}" width="28" height="1" {b_fill}/>'
        f'</g>'
    )
    bottomright = (
        f'<g id="{name("bottomright")}">'
        f'<path d="M{x + 34} {y + 34}H{x + 40}A6 6 0 0 1 {x + 34} {y + 40}Z" {attr}/>'
        f'<path d="M{x + 39.5} {y + 34}A5.5 5.5 0 0 1 {x + 34} {y + 39.5}" {b_attr}/>'
        f'</g>'
    )

    return "\n".join([topleft, top, topright, left, center, right, bottomleft, bottom, bottomright])


def decoration_svg(colors: dict[str, str] = COLORS) -> str:
    active = decoration_frame("decoration", 0, 0, "ColorScheme-Raised", 1.0, active=True)
    inactive = decoration_frame("decoration-inactive", 52, 0, "ColorScheme-Sunken", 0.9, active=False)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="92" height="40" viewBox="0 0 92 40">
  <defs>
    <style id="current-color-scheme" type="text/css"><![CDATA[
      .ColorScheme-Raised {{ color: {colors["surfaceRaised"]}; }}
      .ColorScheme-Sunken {{ color: {colors["surfaceSunken"]}; }}
      .ColorScheme-Highlight {{ color: {colors["accent"]}; }}
      .NoxForge-EdgeHighlight {{ color: {colors["edgeHighlight"]}; }}
      .NoxForge-OutlineMuted {{ color: {colors["border"]}; }}
    ]]></style>
  </defs>
  {active}
  {inactive}
</svg>
'''


BUTTON_STATES = (
    ("active", "ColorScheme-Text", 0.0),
    ("inactive", "ColorScheme-Text", 0.0),
    ("hover", "ColorScheme-Hover", 0.85),
    ("hover-inactive", "ColorScheme-Hover", 0.45),
    ("pressed", "ColorScheme-Pressed", 1.0),
    ("pressed-inactive", "ColorScheme-Pressed", 0.65),
    ("deactivated", "ColorScheme-Text", 0.0),
    ("deactivated-inactive", "ColorScheme-Text", 0.0),
)

GLYPHS = {
    "menu": '<path d="M7 8h10M7 12h10M7 16h10"/>',
    "close": '<path d="M8.5 8.5l7 7M15.5 8.5l-7 7"/>',
    "minimize": '<path d="M7.5 13h9"/>',
    "maximize": '<rect x="7.5" y="7.5" width="9" height="9" rx="1.5"/>',
    "restore": '<path d="M9.5 9.5h5.5v5.5H9.5zM11.5 7.5h5v5"/>',
}


def button_svg(kind: str, colors: dict[str, str] = COLORS) -> str:
    groups = []
    for index, (state, color_class, opacity) in enumerate(BUTTON_STATES):
        x = index * 32
        foreground = (
            colors["negative"]
            if kind == "close" and state in {"hover", "pressed"}
            else colors["textSecondary"]
            if "inactive" in state or state.startswith("deactivated")
            else colors["textPrimary"]
        )
        border_stroke = (
            f'<rect x="0.5" y="0.5" width="23" height="23" rx="{TOKENS["geometry"]["compactRadius"]}" fill="none" stroke="{colors["negative"] if kind == "close" else colors["edgeHighlight"]}" stroke-width="1" stroke-opacity="0.6"/>'
            if state in {"hover", "pressed"}
            else ""
        )
        groups.append(
            f'''<g id="{state}-center" transform="translate({x} 0)" class="{color_class}" color="{colors['textPrimary']}">
      <rect width="24" height="24" rx="{TOKENS['geometry']['compactRadius']}" fill="currentColor" fill-opacity="{opacity:g}"/>
      {border_stroke}
      <g fill="none" stroke="{foreground}" stroke-width="{TOKENS['iconography']['strokeWidth']}" stroke-linecap="round" stroke-linejoin="round">{GLYPHS[kind]}</g>
    </g>'''
        )
    width = len(BUTTON_STATES) * 32
    body = "\n  ".join(groups)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="24" viewBox="0 0 {width} 24">
  <defs>
    <style id="current-color-scheme" type="text/css"><![CDATA[
      .ColorScheme-Text {{ color: {colors["textPrimary"]}; }}
      .ColorScheme-Hover {{ color: {colors["surfaceHover"]}; }}
      .ColorScheme-Pressed {{ color: {colors["surfaceSelected"]}; }}
    ]]></style>
  </defs>
  {body}
</svg>
'''


def write(path: Path, content: str) -> None:
    payload = content.encode()
    if CHECK:
        if not path.is_file() or path.read_bytes() != payload:
            DRIFT.append(path)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def canonical_gzip(payload: bytes) -> bytes:
    """Return a platform-independent gzip stream with a canonical header."""
    stream = io.BytesIO()
    with gzip.GzipFile(
        filename="",
        mode="wb",
        compresslevel=9,
        fileobj=stream,
        mtime=0,
    ) as archive:
        archive.write(payload)
    return stream.getvalue()


def write_aurorae_svg(target_dir: Path, name: str, content: str) -> None:
    write(target_dir / f"{name}.svg", content)
    compressed_path = target_dir / f"{name}.svgz"
    compressed = canonical_gzip(content.encode("utf-8"))
    if CHECK:
        if not compressed_path.is_file() or compressed_path.read_bytes() != compressed:
            DRIFT.append(compressed_path)
    else:
        compressed_path.write_bytes(compressed)


def main() -> None:
    specs = {
        **ICON_SPECS,
        **CORE_ICON_SPECS,
        **STATE_ICON_SPECS,
        **V5_RUNTIME_ICON_SPECS,
        **PHASE6_PRIORITY_ICON_SPECS,
        **V7_CORE_ICON_SPECS,
        **V15_ICON_SPECS,
        **V20_KINETIC_ICON_SPECS,
    }
    effective_aliases: dict[str, str] = {}

    def resolve_body(relative: str) -> str:
        if relative in specs:
            return specs[relative]
        return resolve_body(ICON_ALIASES[relative])

    for relative, target in ICON_ALIASES.items():
        if relative not in specs:
            base = resolve_body(target)
            if relative in TRUE_SYNONYM_ALIASES:
                specs[relative] = base
                effective_aliases[relative] = target
            else:
                specs[relative] = semantic_variant(base, relative)
    for relative, body in sorted(specs.items()):
        write(ICONS / "scalable" / relative, icon_svg(body))
    fixture = ARTWORK["runtimeIconFixture"]
    required = set(fixture["required"])
    missing_fixture = sorted(required - set(specs))
    if missing_fixture:
        raise SystemExit("Runtime icon fixture is missing generated icons: " + ", ".join(missing_fixture))
    optical_contexts = tuple(f"{context}/" for context in fixture["opticalContexts"])
    optical = {
        relative: body for relative, body in specs.items()
        if relative.startswith(optical_contexts)
    }
    for size in fixture["opticalSizes"]:
        for relative, body in sorted(optical.items()):
            if relative == "animations/process-working.svg":
                write(ICONS / f"{size}x{size}" / relative, process_working_sprite_svg(size, frames=16))
            else:
                write(ICONS / f"{size}x{size}" / relative, icon_svg(body, size))
    categories: dict[str, int] = {}
    for relative in specs:
        category = relative.split("/", 1)[0]
        categories[category] = categories.get(category, 0) + 1
    write(
        ICONS / "coverage.json",
        json.dumps(
            {
                "schemaVersion": 3,
                "iconCount": len(specs),
                "opticalCount": len(optical) * 2,
                "opticalSizes": fixture["opticalSizes"],
                "opticalStrokeWidths": {"16": 1.9, "22": 1.75},
                "runtimeFixture": sorted(required),
                "runtimeFixtureSource": fixture["source"],
                "phase6Priority": EDGE_POLISH["icons"]["priority"],
                "phase6ReviewSizes": EDGE_POLISH["icons"]["reviewSizes"],
                "categories": dict(sorted(categories.items())),
                "icons": sorted(specs),
                "aliases": dict(sorted(effective_aliases.items())),
                "duplicateAllowlist": [sorted(group) for group in DUPLICATE_ALLOWLIST],
            },
            indent=2,
        ) + "\n",
    )
    aurorae_targets = (
        (AURORAE, TOKENS["colors"]),
        (AURORAE_OBSIDIAN, TOKENS["colorsObsidian"]),
    )
    for target_dir, colors in aurorae_targets:
        write_aurorae_svg(target_dir, "decoration", decoration_svg(colors))
        for kind in GLYPHS:
            write_aurorae_svg(target_dir, kind, button_svg(kind, colors))
    if DRIFT:
        print("Visual asset generator drift: " + ", ".join(str(path.relative_to(ROOT)) for path in DRIFT), file=sys.stderr)
        raise SystemExit(1)
    if CHECK:
        print(
            f"Verified {len(specs)} scalable icons, {len(optical) * 2} optical variants "
            f"and {len(aurorae_targets) * (1 + len(GLYPHS))} Aurorae pairs"
        )
        return
    print(
        f"Generated {len(specs)} scalable icons, {len(optical) * 2} optical variants "
        f"and {len(aurorae_targets) * (1 + len(GLYPHS))} Aurorae pairs"
    )


if __name__ == "__main__":
    main()
