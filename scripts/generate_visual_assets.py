#!/usr/bin/env python3
"""Generate original NoxForge Aurorae and representative icon SVGs."""

from __future__ import annotations

import gzip
import io
import json
import sys
from pathlib import Path

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

try:
    from .duotone_icons import (
        MONOLINE_PLACES_OVERRIDE,
        build_duotone_apps_specs,
        build_duotone_mimetype_specs,
        build_duotone_places_specs,
    )
except ImportError:
    from duotone_icons import (
        MONOLINE_PLACES_OVERRIDE,
        build_duotone_apps_specs,
        build_duotone_mimetype_specs,
        build_duotone_places_specs,
    )

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
    "actions/document-new.svg": '<path d="M6 3h8l5 5v13a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zM14 3v5h5"/><path class="accent" d="M9 14h6M12 11v6"/>',
    "actions/document-open.svg": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v1"/><path d="M3 10h18l-2 9a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1L3 10z"/><path class="accent" d="M11 13h5M13.5 10.5l2.5 2.5-2.5 2.5"/>',
    "actions/document-save.svg": '<path d="M4 4a1 1 0 0 1 1-1h11l4 4v12a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1zM8 3v5h8V3M8 14h8v6H8z"/><path class="accent" d="M15 3v5"/>',
    "actions/edit-copy.svg": '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M5 16H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1"/><path class="accent" d="M14 8l6 6"/>',
    "actions/edit-paste.svg": '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M6 14H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h2M12 4h2a1 1 0 0 1 1 1v2M9 3h3a1 1 0 0 1 1 1v1H8V4a1 1 0 0 1 1-1z"/><path class="accent" d="M15 9l5 5"/>',
    "actions/edit-delete.svg": '<path d="M4 6h16M10 6V4h4v2M6 6l1 14a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-14M10 10v7M14 10v7"/><path class="accent" d="M4 6h4"/>',
    "actions/system-search.svg": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L20.5 20.5"/><path class="accent" d="M7.5 8.5a4 4 0 0 1 4-2"/>',
    "actions/configure.svg": '<path d="M4 6h16M4 12h16M4 18h16"/><circle cx="8" cy="6" r="2"/><circle cx="16" cy="12" r="2"/><circle cx="11" cy="18" r="2"/><path class="accent" d="M8 4v4"/>',
    "places/folder.svg": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path class="accent" d="M3 9.5h18"/>',
    "places/folder-open.svg": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v1"/><path d="M3 10h18l-2 9a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1L3 10z"/><path class="accent" d="M5 10h14"/>',
    "places/user-home.svg": '<path d="M3 10.5L12 3l9 7.5v8.5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 21v-6a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v6"/><path class="accent" d="M12 3l7 6"/>',
    "places/user-desktop.svg": '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/><path class="accent" d="M4 5h5"/>',
    "places/network-workgroup.svg": '<circle cx="12" cy="5" r="2.5"/><circle cx="5" cy="18" r="2.5"/><circle cx="19" cy="18" r="2.5"/><path d="M12 7.5v4M12 11.5L6 15.5M12 11.5l6 4"/><path class="accent" d="M9 12h6"/>',
    "devices/computer.svg": '<rect x="2" y="3" width="15" height="12" rx="2"/><path d="M6 19h7M9.5 15v4M18 7h3a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1h-3z"/><path class="accent" d="M19 9.5v3"/>',
    "devices/drive-harddisk.svg": '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="8" cy="12" r="2"/><path d="M13 10h5M13 14h5"/><path class="accent" d="M16 16.5h2"/>',
    "devices/audio-card.svg": '<path d="M4 5h13v14H4zM17 9h3v6h-3M7 8h6M7 12h6M7 16h3"/><path class="accent" d="M12 16h2"/>',
    "devices/input-keyboard.svg": '<rect x="2" y="6" width="20" height="12" rx="2"/><path d="M5 10h2M9 10h2M13 10h2M17 10h2M5 14h2M9 14h6M17 14h2"/><path class="accent" d="M9 14h6"/>',
    "devices/input-mouse.svg": '<rect x="7" y="2" width="10" height="20" rx="5"/><path d="M12 2v7M7 9h10"/><path class="accent" d="M12 4v3"/>',
    "devices/phone.svg": '<rect x="6" y="2" width="12" height="20" rx="3"/><path d="M10 5h4M11.5 18.5h1"/><path class="accent" d="M10 5h4"/>',
    "status/network-wireless.svg": '<path d="M3 8.5a13 13 0 0 1 18 0M6 12a9 9 0 0 1 12 0M9 15.5a5 5 0 0 1 6 0"/><circle class="accent-fill" cx="12" cy="19" r="1.5"/>',
    "status/network-wired.svg": '<path d="M4 4h16v10h-6v3h3v3H7v-3h3v-3H4z"/><path class="accent" d="M8 8h8"/>',
    "status/audio-volume-high.svg": '<path d="M3 9.5h4l5-4v13l-5-4H3zM16 9a5 5 0 0 1 0 6M19 6a9 9 0 0 1 0 12"/><path class="accent" d="M12 6v4"/>',
    "status/battery-good.svg": '<rect x="3" y="6" width="16" height="12" rx="2.5"/><path d="M19 10h2v4h-2"/><path class="lime" d="M7 12h8"/>',
    "status/dialog-warning.svg": '<path d="M12 3L22 20a1 1 0 0 1-.87 1.5H2.87A1 1 0 0 1 2 20L12 3zM12 8.5v5.5"/><circle class="warning-fill" cx="12" cy="17" r="1"/>',
}

CORE_ICON_SPECS = {
    "actions/edit-cut.svg": '<path d="M6 6l12 12M18 6L6 18"/><circle cx="7" cy="17" r="3"/><circle cx="17" cy="17" r="3"/><path class="accent" d="M10 10l2 2"/>',
    "actions/edit-undo.svg": '<path d="M9 7L4 12l5 5M5 12h8a6 6 0 0 1 6 6"/><path class="accent" d="M4 12h5"/>',
    "actions/edit-redo.svg": '<path d="M15 7l5 5-5 5M19 12h-8a6 6 0 0 0-6 6"/><path class="accent" d="M15 12h5"/>',
    "actions/edit-select-all.svg": '<rect x="4" y="4" width="16" height="16" rx="2" stroke-dasharray="4 3"/><path class="accent" d="M9 12l2 2 4-4"/>',
    "actions/go-next.svg": '<path d="M8 5l7 7-7 7"/><path class="accent" d="M15 12h5"/>',
    "actions/list-add.svg": '<path d="M5 7h10M5 12h10M5 17h7M19 14v6M16 17h6"/><path class="accent" d="M16 17h6"/>',
    "actions/media-playback-start.svg": '<path d="M8 5l11 7-11 7z"/><path class="lime" d="M8 5v6"/>',
    "actions/view-refresh.svg": '<path d="M19 8V4l-3 3a8 8 0 1 0 2 9M19 4h-5"/><path class="accent" d="M16 7l3-3"/>',
    "categories/applications-system.svg": '<rect x="3" y="3" width="8" height="8" rx="1.5"/><rect x="13" y="3" width="8" height="8" rx="1.5"/><rect x="3" y="13" width="8" height="8" rx="1.5"/><rect x="13" y="13" width="8" height="8" rx="1.5"/><path class="accent" d="M13 3h8v3"/>',
    "categories/applications-development.svg": '<path d="M9 5l-6 7 6 7M15 5l6 7-6 7M13 3l-2 18"/><path class="accent" d="M15 5l3 3"/>',
    "categories/applications-graphics.svg": '<path d="M4 20l3-9 9-7 4 4-7 9zM11 11l2 2"/><path class="accent" d="M4 20l4.5-4.5"/>',
    "categories/applications-internet.svg": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 4 6 4 9s-1 6-4 9M12 3c-3 3-4 6-4 9s1 6 4 9"/><path class="accent" d="M12 3v4"/>',
    "categories/applications-multimedia.svg": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M9 9l7 3-7 3z"/><path class="accent" d="M3 5h8"/>',
    "devices/camera-photo.svg": '<path d="M3 8a1 1 0 0 1 1-1h3l2-3h6l2 3h3a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><circle cx="12" cy="13" r="4"/><path class="accent" d="M17 7h4"/>',
    "devices/printer.svg": '<path d="M6 9V3h12v6M6 17H3V9h18v8h-3M6 14h12v7H6z"/><path class="accent" d="M16 12h2"/>',
    "devices/audio-headphones.svg": '<path d="M4 13a8 8 0 0 1 16 0v7h-4v-6h4M4 14h4v6H4z"/><path class="accent" d="M4 13a8 8 0 0 1 3-6"/>',
    "devices/media-removable.svg": '<path d="M7 3h10v8l3 3v7H4v-7l3-3zM7 11h10"/><path class="accent" d="M10 6h4"/>',
    "emblems/emblem-favorite.svg": '<path d="M12 3l2.7 5.5 6.1.9-4.4 4.3 1 6.1-5.4-2.9-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/><path class="accent" d="M12 3v6"/>',
    "emblems/emblem-important.svg": '<path d="M12 3v12"/><circle class="accent-fill" cx="12" cy="20" r="1.5"/><path class="accent" d="M12 3v5"/>',
    "emblems/emblem-shared.svg": '<circle cx="6" cy="12" r="3"/><circle cx="18" cy="6" r="3"/><circle cx="18" cy="18" r="3"/><path d="M9 11l6-4M9 13l6 4"/><path class="accent" d="M15 7l3-1"/>',
    "mimetypes/text-x-generic.svg": '<path d="M6 3h9l4 4v14H6zM15 3v5h4M9 12h7M9 16h7"/><path class="accent" d="M9 12h4"/>',
    "mimetypes/application-pdf.svg": '<path d="M6 3h9l4 4v14H6zM15 3v5h4M9 16c3-6 5-6 7 0M10 13h5"/><path class="accent" d="M9 16h3"/>',
    "mimetypes/package-x-generic.svg": '<path d="M3 7l9-4 9 4v10l-9 4-9-4zM3 7l9 4 9-4M12 11v10"/><path class="accent" d="M12 3l5 2"/>',
    "mimetypes/image-x-generic.svg": '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8" cy="9" r="2"/><path d="M4 18l5-5 3 3 3-4 5 6"/><path class="accent" d="M15 12l5 6"/>',
    "mimetypes/audio-x-generic.svg": '<path d="M9 18V6l10-2v12M9 10l10-2"/><circle cx="6" cy="18" r="3"/><circle cx="16" cy="16" r="3"/><path class="accent" d="M9 6l5-1"/>',
    "mimetypes/video-x-generic.svg": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M10 9l6 3-6 3zM3 9h3M18 9h3"/><path class="accent" d="M10 9v3"/>',
    "places/folder-documents.svg": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M8 12h8M8 15h5"/><path class="accent" d="M8 12h5"/>',
    "places/user-trash.svg": '<path d="M4 6h16M10 6V4h4v2M6 6l1 14a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-14M10 10v7M14 10v7"/><path class="accent" d="M5 6h4"/>',
    "preferences/preferences-system.svg": '<path d="M4 6h16M4 12h16M4 18h16"/><circle cx="8" cy="6" r="2"/><circle cx="16" cy="12" r="2"/><circle cx="11" cy="18" r="2"/><path class="accent" d="M8 4v4"/>',
    "preferences/preferences-desktop-theme.svg": '<rect x="3" y="4" width="18" height="14" rx="2"/><path d="M8 22h8M12 18v4M6 8h12M6 12h7"/><path class="accent" d="M6 8h5"/>',
    "preferences/preferences-desktop-display.svg": '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/><path class="accent" d="M4 5h4"/>',
    "preferences/preferences-desktop-keyboard.svg": '<path d="M4 5h16M9 3v4"/><circle cx="9" cy="5" r="2"/><rect x="2" y="9" width="20" height="11" rx="2"/><path d="M5 13h2M9 13h2M13 13h2M17 13h2M6 17h12"/><path class="accent" d="M7 17h10"/>',
    "preferences/preferences-system-network.svg": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 4 6 4 9s-1 6-4 9M12 3c-3 3-4 6-4 9s1 6 4 9"/><path class="accent" d="M12 3v4"/>',
    "preferences/preferences-system-power-management.svg": '<path d="M12 3v8M7 6a8 8 0 1 0 10 0"/><path class="accent" d="M12 3v5"/>',
    "status/dialog-information.svg": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6"/><circle class="accent-fill" cx="12" cy="7.5" r="1"/><path class="accent" d="M12 11v3"/>',
    "status/dialog-error.svg": '<circle cx="12" cy="12" r="9"/><path d="M8.5 8.5l7 7M15.5 8.5l-7 7"/><path class="negative" d="M8.5 8.5l3.5 3.5"/>',
    "status/network-offline.svg": '<path class="dimmed" d="M3 8.5a13 13 0 0 1 18 0M6 12a9 9 0 0 1 12 0M9 15.5a5 5 0 0 1 6 0"/><path d="M4 4l16 16"/><path class="negative" d="M9 9l6 6"/>',
    "status/security-high.svg": '<path d="M12 3l8 3v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6zM8.5 12l2.5 2.5 5-5"/><path class="lime" d="M8.5 12l2.5 2.5"/>',
    "status/software-update-available.svg": '<path d="M12 3v12M7 10l5 5 5-5M5 20h14"/><path class="accent" d="M12 3v6"/>',
}

STATE_ICON_SPECS = {
    "actions/go-previous.svg": '<path d="M16 5l-7 7 7 7"/><path class="accent" d="M9 12H4"/>',
    "actions/go-up.svg": '<path d="M5 16l7-7 7 7"/><path class="accent" d="M12 9V4"/>',
    "actions/go-down.svg": '<path d="M5 8l7 7 7-7"/><path class="accent" d="M12 15v5"/>',
    "actions/media-playback-pause.svg": '<path d="M7 5v14M17 5v14"/><path class="accent" d="M7 5v6"/>',
    "actions/media-playback-stop.svg": '<rect x="6" y="6" width="12" height="12" rx="1.5"/><path class="accent" d="M6 6h6"/>',
    "actions/media-skip-backward.svg": '<path d="M18 5l-9 7 9 7zM6 5v14"/><path class="accent" d="M6 5v7"/>',
    "actions/zoom-in.svg": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L20.5 20.5M7.5 10.5h6M10.5 7.5v6"/><path class="accent" d="M10.5 7.5v3"/>',
    "actions/zoom-out.svg": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L20.5 20.5M7.5 10.5h6"/><path class="accent" d="M7.5 10.5h3"/>',
    "applets/bluetooth-active.svg": '<path d="M8 6l8 12V6L8 18l8-12"/><path class="accent" d="M8 6l8 12"/>',
    "applets/bluetooth-disabled.svg": '<path class="dimmed" d="M9 7l7 11V6l-4 6"/><path d="M5 5l14 14"/><path class="negative" d="M5 5l6 6"/>',
    "applets/redshift-status-day.svg": '<circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/><path class="accent" d="M12 2v3"/>',
    "applets/redshift-status-off.svg": '<circle class="dimmed" cx="12" cy="12" r="7"/><path d="M5 5l14 14"/><path class="negative" d="M5 5l5 5"/>',
    "applets/redshift-status-on.svg": '<path d="M17 15a7 7 0 1 1-8-10 6 6 0 0 0 8 10z"/><path class="accent" d="M17 15a7 7 0 0 1-4 3"/>',
    "status/audio-volume-low.svg": '<path d="M3 9.5h4l5-4v13l-5-4H3zM16 10a3 3 0 0 1 0 4"/><path class="accent" d="M12 6v4"/>',
    "status/audio-volume-medium.svg": '<path d="M3 9.5h4l5-4v13l-5-4H3zM16 9a5 5 0 0 1 0 6"/><path class="accent" d="M12 6v4"/>',
    "status/audio-volume-muted.svg": '<path d="M3 9.5h4l5-4v13l-5-4H3zM16 9l5 6M21 9l-5 6"/><path class="negative" d="M16 9l5 6"/>',
    "status/battery-low.svg": '<rect x="3" y="6" width="16" height="12" rx="2.5"/><path d="M19 10h2v4h-2"/><path class="warning" d="M7 12h3"/>',
    "status/battery-caution.svg": '<rect x="3" y="6" width="16" height="12" rx="2.5"/><path d="M19 10h2v4h-2M11 9v4"/><circle class="warning-fill" cx="11" cy="15.5" r="1"/>',
    "status/battery-charging.svg": '<rect x="3" y="6" width="16" height="12" rx="2.5"/><path d="M19 10h2v4h-2M13 8l-4 5h3l-1 4 4-6h-3z"/><path class="lime" d="M13 8l-2 3"/>',
    "status/network-wireless-disconnected.svg": (
        '<path class="dimmed" d="M3 8.5a13 13 0 0 1 18 0M6 12a9 9 0 0 1 12 0M9 15.5a5 5 0 0 1 6 0"/>'
        '<circle class="dimmed" cx="12" cy="19" r="1.5"/><path d="M4 4l16 16"/><path class="negative" stroke-width="2" d="M9 9l6 6"/>'
    ),
    "status/network-wired-disconnected.svg": '<path class="dimmed" d="M4 4h16v10h-6v3h3v3H7v-3h3v-3H4z"/><path d="M5 5l14 14"/><path class="negative" d="M9 9l6 6"/>',
}

V5_RUNTIME_ICON_SPECS = {
    "actions/application-exit.svg": '<path d="M10 4H5v16h5M14 8l4 4-4 4M8 12h10"/><path class="accent" d="M14 8l4 4"/>',
    "actions/help-about.svg": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6"/><circle class="accent-fill" cx="12" cy="7.5" r="1"/>',
    "actions/help-contents.svg": '<path d="M4 5h6a2 2 0 0 1 2 2v12a2 2 0 0 0-2-2H4zM20 5h-6a2 2 0 0 0-2 2v12a2 2 0 0 1 2-2h6z"/><path class="accent" d="M12 7v5"/>',
    "actions/system-run.svg": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 9l3 3-3 3M12 15h5"/><path class="accent" d="M7 9l3 3"/>',
    "actions/view-filter.svg": '<path d="M4 5h16l-6 7v6l-4 2v-8z"/><path class="accent" d="M4 5h7"/>',
    "actions/view-grid.svg": '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><path class="accent" d="M14 3h7"/>',
    "actions/view-list-tree.svg": '<path d="M5 5v14M5 8h5M5 16h5M10 6h10v4H10zM10 14h10v4H10z"/><path class="accent" d="M5 8h5"/>',
    "applets/keyboard-layout.svg": '<rect x="2" y="6" width="20" height="12" rx="2"/><path d="M5 10h2M9 10h2M13 10h2M17 10h2M6 14h12"/><path class="accent" d="M6 14h5"/>',
    "categories/applications-accessories.svg": '<path d="M6 4h12v16H6zM9 8h6M9 12h6M9 16h4"/><path class="accent" d="M6 4h5"/>',
    "categories/applications-education.svg": '<path d="M3 9l9-5 9 5-9 5zM6 11.5v4.5c4 3 8 3 12 0v-4.5"/><path class="accent" d="M21 9v6"/>',
    "devices/drive-optical.svg": '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/><path class="accent" d="M12 7a5 5 0 0 1 4 2"/>',
    "devices/scanner.svg": '<rect x="3" y="12" width="18" height="7" rx="1.5"/><path d="M5 5l14 5M7 15.5h10"/><path class="accent" d="M7 15.5h4"/>',
    "devices/tablet.svg": '<rect x="4" y="2" width="16" height="20" rx="2"/><circle cx="12" cy="18" r="1"/><path d="M8 5h8v10H8z"/><path class="accent" d="M16 5v5"/>',
    "preferences/preferences-desktop-accessibility.svg": '<circle cx="12" cy="5" r="2"/><path d="M4 9h16M12 7v13M7 20l5-7 5 7"/><path class="accent" d="M4 9h6"/>',
    "preferences/preferences-desktop-display-randr.svg": '<rect x="3" y="4" width="18" height="13" rx="1"/><path d="M9 21h6M12 17v4M7 8h10M7 12h6"/><path class="accent" d="M3 4h6"/>',
    "status/printer-error.svg": '<path d="M6 9V3h12v6M6 17H3V9h18v8h-3M6 14h12v7H6z"/><path class="negative" d="M10.5 16l3 3M13.5 16l-3 3"/>',
    "status/software-update-none.svg": '<path d="M19 8V4l-3 3a8 8 0 1 0 2 9M19 4h-5M7 12h10"/><path class="accent" d="M7 12h5"/>',
    "status/user-available.svg": '<circle cx="10" cy="8" r="4"/><path d="M3 21c0-5 3-7 7-7s7 2 7 7"/><circle cx="18" cy="17" r="3"/><path class="lime" d="M16.5 17l1 1 2-2"/>',
    "status/user-away.svg": '<circle cx="10" cy="8" r="4"/><path d="M3 21c0-5 3-7 7-7s7 2 7 7"/><circle cx="18" cy="17" r="3"/><path class="warning" d="M18 15v2l1.5 1"/>',
}

PHASE6_PRIORITY_ICON_SPECS = {
    "actions/dialog-cancel.svg": '<rect x="4" y="4" width="16" height="16" rx="4"/><path d="M8.5 8.5l7 7M15.5 8.5l-7 7"/><path class="negative" d="M8.5 8.5l3.5 3.5"/>',
    "actions/dialog-ok.svg": '<circle cx="12" cy="12" r="9"/><path d="M7.5 12l3 3 6.5-6.5"/><path class="lime" d="M7.5 12l3 3"/>',
    "applets/battery.svg": '<rect x="3" y="6" width="16" height="12" rx="2.5"/><path d="M19 10h2v4h-2M7 10v4M11 10v4"/><path class="lime" d="M15 10v4"/>',
    "applets/clock.svg": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/><path class="accent" d="M12 7v5"/>',
    "applets/network.svg": '<circle cx="5" cy="17" r="2"/><circle cx="12" cy="7" r="2"/><circle cx="19" cy="17" r="2"/><path d="M6 15l5-6M13 9l5 6M7 17h10"/><path class="accent" d="M7 17h5"/>',
    "applets/notifications.svg": '<path d="M6 16h12l-2-3V9a4 4 0 0 0-8 0v4zM10 19h4"/><path class="accent" d="M8 13h8"/>',
    "applets/systemtray.svg": '<rect x="4" y="4" width="6" height="6" rx="1.5"/><rect x="14" y="4" width="6" height="6" rx="1.5"/><rect x="4" y="14" width="6" height="6" rx="1.5"/><rect x="14" y="14" width="6" height="6" rx="1.5"/><path class="accent" d="M14 4h6v3"/>',
    "places/folder-download.svg": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M12 10v6M9 13.5l3 3 3-3"/><path class="accent" d="M9 13.5l3 3"/>',
    "places/folder-pictures.svg": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><circle cx="9" cy="12" r="1.5"/><path d="M6 17l4-3 3 2 3-4 3 5"/><path class="accent" d="M16 12l3 5"/>',
    "places/folder-videos.svg": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 11l6 3-6 3z"/><path class="accent" d="M9 11v3"/>',
    "preferences/preferences-desktop-color.svg": '<path d="M12 3a9 9 0 0 0 0 18c1.5 0 2.5-1 2.5-2.2 0-.8-.5-1.5-.5-2.3 0-1.2 1-2 2.2-2H18a3 3 0 0 0 3-3c0-4.7-4-8.5-9-8.5z"/><circle cx="8.5" cy="9.5" r="1"/><circle class="lime-fill" cx="12" cy="7.5" r="1.15"/><circle cx="15.5" cy="9.5" r="1"/><circle class="accent-fill" cx="8.5" cy="13.5" r="1.2"/>',
    "preferences/preferences-desktop-icons.svg": '<rect x="3" y="4" width="18" height="16" rx="2"/><rect x="6" y="7" width="4" height="4" rx="1"/><rect x="14" y="7" width="4" height="4" rx="1"/><rect x="6" y="14" width="4" height="3" rx="1"/><rect x="14" y="14" width="4" height="3" rx="1"/><path class="accent" d="M14 7h4v2"/>',
    "preferences/preferences-desktop-mouse.svg": '<rect x="7" y="2" width="10" height="20" rx="5"/><path d="M12 2v7M7 9h10M19 7v10"/><circle cx="19" cy="12" r="1.5"/><path class="accent" d="M19 10.5v3"/>',
    "preferences/preferences-system-bluetooth.svg": '<circle cx="12" cy="12" r="9"/><path d="M8 7l8 10V7L8 17l8-10"/><path class="accent" d="M8 7l8 10"/>',
    "preferences/preferences-system-sound.svg": '<path d="M3 9.5h4l5-4v13l-5-4H3zM16 7v10M20 5v14"/><circle cx="16" cy="11" r="1.5"/><circle cx="20" cy="14" r="1.5"/><path class="accent" d="M16 9.5v3"/>',
}

V7_CORE_ICON_SPECS = {
    "actions/draw-highlight.svg": '<path d="M5 18l9-9 5 5-9 9H5zM12 11l5 5M15 7l2-2 4 4-2 2"/><path class="accent" d="M5 18h5l-5 5z"/>',
    "actions/view-hidden.svg": '<path d="M3 12c2.5-4 5.5-6 9-6s6.5 2 9 6c-2.5 4-5.5 6-9 6s-6.5-2-9-6zM9 12a3 3 0 0 0 5 2"/><path d="M4 4l16 16"/><path class="accent" d="M4 4l6 6"/>',
    "actions/tools-report-bug.svg": '<path d="M8 8h8v10a4 4 0 0 1-8 0zM10 8V5h4v3M5 11h3M16 11h3M5 15h3M16 15h3M6 20l3-2M18 20l-3-2"/><path class="accent" d="M10 5h4M8 11h8"/>',
    "actions/system-suspend.svg": '<path d="M7 5a8 8 0 1 0 12 10A7 7 0 0 1 7 5z"/><path class="accent" d="M7 5a8 8 0 0 0 4 15"/>',
    "actions/system-reboot.svg": '<path d="M19 8V4l-3 3a8 8 0 1 0 2 9M19 4h-5"/><path class="accent" d="M16 7l3-3M18 16l-2 2"/>',
    "actions/system-shutdown.svg": '<path d="M12 3v9M7 6a8 8 0 1 0 10 0"/><path class="accent" d="M12 3v6"/>',
    "actions/system-lock-screen.svg": '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3"/><path class="accent" d="M8 10h8"/>',
    "actions/system-log-out.svg": '<path d="M10 4H5a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h5M14 8l4 4-4 4M8 12h10"/><path class="accent" d="M14 8l4 4M8 12h5"/>',
}

V15_ICON_SPECS = {
    "status/network-wireless-connected-75.svg": (
        '<path class="dimmed" d="M3 8.5a13 13 0 0 1 18 0"/>'
        '<path d="M6 12a9 9 0 0 1 12 0M9 15.5a5 5 0 0 1 6 0"/>'
        '<circle class="accent-fill" cx="12" cy="19" r="1.5"/>'
    ),
    "status/network-wireless-connected-50.svg": (
        '<path class="dimmed" d="M3 8.5a13 13 0 0 1 18 0M6 12a9 9 0 0 1 12 0"/>'
        '<path d="M9 15.5a5 5 0 0 1 6 0"/>'
        '<circle class="accent-fill" cx="12" cy="19" r="1.5"/>'
    ),
    "status/network-wireless-connected-25.svg": (
        '<path class="dimmed" d="M3 8.5a13 13 0 0 1 18 0M6 12a9 9 0 0 1 12 0M9 15.5a5 5 0 0 1 6 0"/>'
        '<circle class="accent-fill" cx="12" cy="19" r="1.5"/>'
    ),
    "status/network-wireless-connected-00.svg": (
        '<path class="dimmed" d="M3 8.5a13 13 0 0 1 18 0M6 12a9 9 0 0 1 12 0M9 15.5a5 5 0 0 1 6 0"/>'
        '<circle class="dimmed" cx="12" cy="19" r="1.5"/>'
    ),
    "status/network-wireless-acquiring.svg": (
        '<path class="dimmed" d="M3 8.5a13 13 0 0 1 18 0"/>'
        '<path class="lime" d="M6 12a9 9 0 0 1 12 0"/>'
        '<path class="dimmed" d="M9 15.5a5 5 0 0 1 6 0"/>'
        '<circle class="accent-fill" cx="12" cy="19" r="1.5"/>'
    ),
    "status/network-wireless-locked.svg": (
        '<path d="M3 8.5a13 13 0 0 1 18 0M6 12a9 9 0 0 1 10 0M9 15.5a5 5 0 0 1 4 0"/>'
        '<circle class="accent-fill" cx="12" cy="19" r="1.5"/>'
        '<rect class="accent" x="16.5" y="15.5" width="5" height="4" rx="1"/>'
        '<path class="accent" d="M17.5 15.5v-1.5a1.5 1.5 0 0 1 3 0v1.5"/>'
    ),
    "status/network-wireless-hotspot.svg": (
        '<path d="M12 7v10M9 17h6M4 7a11 11 0 0 0 0 14M20 7a11 11 0 0 1 0 14"/>'
        '<path class="accent" d="M7 10a7 7 0 0 0 0 8M17 10a7 7 0 0 1 0 8"/>'
        '<circle class="lime-fill" cx="12" cy="7" r="1.5"/>'
    ),
    "status/battery-000.svg": (
        '<rect x="3" y="6" width="16" height="12" rx="2.5"/><path d="M19 10h2v4h-2"/>'
        '<path class="negative" d="M11 9v4"/><circle class="negative-fill" cx="11" cy="15.5" r="1"/>'
    ),
    "status/battery-100.svg": (
        '<rect x="3" y="6" width="16" height="12" rx="2.5"/><path d="M19 10h2v4h-2"/>'
        '<path class="lime" d="M6 10h10M6 14h10"/>'
    ),
}


def _level_class(pct: int, *, fill: bool = False) -> str:
    suffix = "-fill" if fill else ""
    if pct <= 10:
        return f"ColorScheme-NegativeText negative{suffix}"
    if pct <= 20:
        return f"ColorScheme-NeutralText warning{suffix}"
    return f"ColorScheme-PositiveText lime{suffix}"


def _build_v20_battery_specs() -> dict[str, str]:
    specs: dict[str, str] = {}
    shell = '<rect x="3" y="6" width="16" height="12" rx="2.5"/><path d="M19 10h2v4h-2"/>'
    bolt_anim = (
        '<path class="ColorScheme-PositiveText lime nf-pulse" d="M12 8.5L9.5 12h3L10 15.5">'
        '<animate attributeName="opacity" values="0.9;0.35;0.9" dur="1.4s" repeatCount="indefinite"/></path>'
    )
    sym_mark = '<path class="symbolic-ring" d="M5 19.5h12"/>'
    for pct in range(0, 101, 10):
        tag = f"{pct:03d}"
        cls_fill = _level_class(pct, fill=True)
        cls_stroke = _level_class(pct, fill=False)
        bar_w = round(pct * 11 / 100, 2)
        if pct == 0:
            bar = '<path class="ColorScheme-NegativeText negative" d="M11 8.5v4"/><circle class="ColorScheme-NegativeText negative-fill" cx="11" cy="15.2" r="1"/>'
        else:
            bar = f'<rect class="{cls_fill}" x="5.5" y="9" width="{bar_w}" height="6" rx="1"/>'
        specs[f"status/battery-{tag}.svg"] = shell + bar
        specs[f"status/battery-{tag}-symbolic.svg"] = shell + bar + sym_mark
        chg_level = f'<path class="{cls_stroke}" d="M5.5 15.8h{max(1.0, bar_w)}"/>'
        specs[f"status/battery-{tag}-charging.svg"] = f"{shell}{bolt_anim}{chg_level}"
        specs[f"status/battery-{tag}-charging-symbolic.svg"] = f"{shell}{bolt_anim}{sym_mark}{chg_level}"
        specs[f"status/battery-{tag}-profile-powersave.svg"] = f'{shell}{bar}<path class="lime" d="M16.5 17.5c1-2 2.5-2.5 4-2.5-0.4 1.6-1.2 2.8-4 2.5z"/>'
        specs[f"status/battery-{tag}-profile-balanced.svg"] = f'{shell}{bar}<circle class="accent-fill" cx="18.5" cy="17.5" r="1.4"/>'
        specs[f"status/battery-{tag}-profile-performance.svg"] = f'{shell}{bar}<path class="warning" d="M16 19l2-2.5 2 2.5"/>'
    specs["status/battery-charging.svg"] = f"{shell}{bolt_anim}"
    specs["status/battery-charging-symbolic.svg"] = specs["status/battery-charging.svg"] + sym_mark
    specs["status/battery-caution-charging.svg"] = f'{shell}{bolt_anim}<path class="ColorScheme-NegativeText negative" d="M5.5 15.8h2.2"/>'
    specs["status/battery-low-charging.svg"] = f'{shell}{bolt_anim}<path class="ColorScheme-NeutralText warning" d="M5.5 15.8h3.5"/>'
    specs["status/battery-good-charging.svg"] = f'{shell}{bolt_anim}<path class="ColorScheme-PositiveText lime" d="M5.5 15.8h8.4"/>'
    specs["status/battery-full-charging.svg"] = f'{shell}{bolt_anim}<path class="ColorScheme-PositiveText lime" d="M5.5 15.8h10.6"/>'
    specs["status/battery-empty.svg"] = shell + '<path class="ColorScheme-NegativeText negative" d="M7 10v4"/>'
    specs["status/battery-empty-symbolic.svg"] = specs["status/battery-empty.svg"] + sym_mark
    specs["status/battery-full.svg"] = (
        f'{shell}<rect class="ColorScheme-PositiveText lime-fill" x="5" y="8.5" width="2.4" height="7" rx="0.5"/>'
        '<rect class="ColorScheme-PositiveText lime-fill" x="8.2" y="8.5" width="2.4" height="7" rx="0.5"/>'
        '<rect class="ColorScheme-PositiveText lime-fill" x="11.4" y="8.5" width="2.4" height="7" rx="0.5"/>'
        '<rect class="ColorScheme-PositiveText lime-fill" x="14.6" y="8.5" width="2.4" height="7" rx="0.5"/>'
    )
    specs["status/battery-full-symbolic.svg"] = specs["status/battery-full.svg"] + sym_mark
    specs["status/battery-missing.svg"] = shell + '<path class="ColorScheme-NegativeText negative" d="M9 10l4 4M13 10l-4 4"/>'
    specs["status/battery-missing-symbolic.svg"] = specs["status/battery-missing.svg"] + sym_mark
    specs["status/battery-ups.svg"] = '<rect x="5" y="3" width="14" height="18" rx="2"/><rect class="ColorScheme-PositiveText lime-fill" x="8" y="7" width="8" height="3" rx="1"/><path class="accent" d="M12 12.5l-2 2.5h4l-2 2.5"/>'
    specs["devices/input-mouse-battery.svg"] = '<rect x="3" y="4" width="8" height="16" rx="4"/><path d="M7 4v5M3 9h8"/><rect x="14" y="6" width="7" height="12" rx="1.5"/><rect class="ColorScheme-PositiveText lime-fill" x="15.5" y="9" width="4" height="7" rx="0.5"/><path class="accent" d="M16 4h3"/>'
    specs["devices/input-keyboard-battery.svg"] = '<rect x="2" y="10" width="14" height="10" rx="2"/><path d="M5 14h2M9 14h4M5 17h8"/><rect x="17.5" y="4" width="4.5" height="10" rx="1"/><rect class="ColorScheme-PositiveText lime-fill" x="18.7" y="7" width="2" height="5"/><path class="accent" d="M19 2.5h1.5"/>'
    specs["devices/phone-battery.svg"] = '<rect x="3" y="3" width="10" height="18" rx="2"/><path d="M6.5 6h3"/><rect x="15.5" y="7" width="6" height="11" rx="1.5"/><rect class="ColorScheme-PositiveText lime-fill" x="17" y="10" width="3" height="6"/><path class="accent" d="M17.5 5h2"/>'
    specs["devices/input-gaming-battery.svg"] = '<path d="M4 13a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4l1 5-3-1h-8l-3 1z"/><path d="M6.5 13h3M8 11.5v3"/><rect x="18" y="6" width="4" height="10" rx="1"/><rect class="ColorScheme-PositiveText lime-fill" x="19" y="9" width="2" height="5"/><circle class="accent-fill" cx="12.5" cy="12.5" r="0.9"/>'
    specs["devices/preferences-system-bluetooth-battery.svg"] = '<path d="M5 8l6 6-3 3V7l3 3-6 6"/><rect x="15" y="6" width="6" height="12" rx="1.2"/><rect class="ColorScheme-PositiveText lime-fill" x="16.5" y="9" width="3" height="7"/><path class="accent" d="M17 4h2"/>'
    return specs


def _wifi_arcs_markup(lit_arcs: int, cls: str, *, dot_cls: str | None = None) -> str:
    arcs = (
        "M9.5 16.5a3.5 3.5 0 0 1 5 0",
        "M7 14a7.1 7.1 0 0 1 10 0",
        "M4.5 11.5a10.6 10.6 0 0 1 15 0",
        "M2 9a14.1 14.1 0 0 1 20 0",
    )
    parts = []
    for idx, d in enumerate(arcs, start=1):
        if idx <= lit_arcs:
            parts.append(f'<path d="{d}"/>')
        else:
            parts.append(f'<path class="dimmed" d="{d}"/>')
    dc = dot_cls or cls
    parts.append(f'<circle class="{dc}" cx="12" cy="19" r="1.5"/>')
    return "".join(parts)


def _build_v20_wireless_specs() -> dict[str, str]:
    specs: dict[str, str] = {}
    level_map = (
        ("0", 0, "ColorScheme-NegativeText negative", "ColorScheme-NegativeText negative-fill"),
        ("20", 1, "ColorScheme-NeutralText warning", "accent-fill"),
        ("40", 2, "ColorScheme-Text", "accent-fill"),
        ("60", 2, "ColorScheme-Text", "accent-fill"),
        ("80", 3, "ColorScheme-Text", "accent-fill"),
        ("100", 4, "ColorScheme-Text", "accent-fill"),
    )
    lock_badge = '<rect x="16.5" y="15.5" width="5" height="4" rx="1"/><path d="M17.5 15.5v-1.5a1.5 1.5 0 0 1 3 0v1.5"/>'
    limit_badge = '<path class="ColorScheme-NeutralText warning" stroke-width="1.8" d="M19 13v3.8"/><circle class="ColorScheme-NeutralText warning-fill" cx="19" cy="19.2" r="0.9"/>'
    conn_ring = '<path opacity="0.45" d="M10 21.2h4"/>'
    sym_ring = '<path class="symbolic-ring" d="M8 21.5h8"/>'

    for label, arcs_lit, stroke_cls, dot_cls in level_map:
        base_body = _wifi_arcs_markup(arcs_lit, stroke_cls, dot_cls=dot_cls)
        if label == "60":
            # Ensure 60% differs visually from 40% with a subtle mid-opacity 3rd arc
            base_body = (
                '<path d="M9.5 16.5a3.5 3.5 0 0 1 5 0"/>'
                '<path d="M7 14a7.1 7.1 0 0 1 10 0"/>'
                '<path opacity="0.55" d="M4.5 11.5a10.6 10.6 0 0 1 15 0"/>'
                '<path class="dimmed" d="M2 9a14.1 14.1 0 0 1 20 0"/>'
                f'<circle class="{dot_cls}" cx="12" cy="19" r="1.5"/>'
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
        b25 = _wifi_arcs_markup(arcs_lit, "ColorScheme-Text", dot_cls="accent-fill")
        specs[f"status/network-wireless-connected-{conn_pct}-symbolic.svg"] = b25 + conn_ring + '<path class="symbolic-ring" d="M6 21.5h12"/>'
    specs["status/network-wireless-connected-100-symbolic.svg"] = _wifi_arcs_markup(4, "ColorScheme-Text", dot_cls="accent-fill") + conn_ring + sym_ring
    specs["status/network-wireless-connected-100-locked.svg"] = _wifi_arcs_markup(4, "ColorScheme-Text", dot_cls="accent-fill") + conn_ring + lock_badge
    specs["status/network-wireless-connected-100-limited.svg"] = _wifi_arcs_markup(4, "ColorScheme-Text", dot_cls="accent-fill") + conn_ring + limit_badge

    sig_levels = (
        ("none", 0, "ColorScheme-NegativeText negative", "ColorScheme-NegativeText negative-fill"),
        ("weak", 1, "ColorScheme-NeutralText warning", "ColorScheme-NeutralText warning-fill"),
        ("ok", 2, "ColorScheme-Text", "accent-fill"),
        ("good", 3, "ColorScheme-Text", "accent-fill"),
        ("excellent", 4, "ColorScheme-Text", "accent-fill"),
    )
    for sig_name, arcs_lit, sc, dc in sig_levels:
        sb = _wifi_arcs_markup(arcs_lit, sc, dot_cls=dc) + '<path class="dimmed" d="M10 21h4"/>'
        specs[f"status/network-wireless-signal-{sig_name}.svg"] = sb
        specs[f"status/network-wireless-signal-{sig_name}-symbolic.svg"] = sb + '<circle class="dimmed" cx="4" cy="20" r="0.8"/>'

    specs["status/network-wireless-acquiring.svg"] = (
        '<path class="dimmed nf-wave-3" d="M2 9a14.1 14.1 0 0 1 20 0">'
        '<animate attributeName="opacity" values="0.2;0.85;0.2" begin="0.4s" dur="1.8s" repeatCount="indefinite"/></path>'
        '<path class="lime nf-wave-2" d="M4.5 11.5a10.6 10.6 0 0 1 15 0">'
        '<animate attributeName="opacity" values="0.2;0.85;0.2" begin="0.2s" dur="1.8s" repeatCount="indefinite"/></path>'
        '<path class="nf-wave-1" d="M9.5 16.5a3.5 3.5 0 0 1 5 0">'
        '<animate attributeName="opacity" values="0.2;0.85;0.2" begin="0s" dur="1.8s" repeatCount="indefinite"/></path>'
        '<path class="dimmed" d="M7 14a7.1 7.1 0 0 1 10 0"/>'
        '<circle class="accent-fill nf-pulse" cx="12" cy="19" r="1.5"/>'
    )
    specs["status/network-wireless-acquiring-symbolic.svg"] = specs["status/network-wireless-acquiring.svg"] + sym_ring
    specs["status/network-wireless-limited.svg"] = _wifi_arcs_markup(3, "ColorScheme-Text", dot_cls="accent-fill") + limit_badge
    specs["status/network-wireless-off.svg"] = _wifi_arcs_markup(0, "dimmed", dot_cls="dimmed") + '<path d="M4 4l16 16"/><path class="ColorScheme-NegativeText negative" d="M9 9l6 6"/>'
    specs["status/network-wireless-on.svg"] = _wifi_arcs_markup(3, "ColorScheme-Text", dot_cls="accent-fill") + '<path class="accent" d="M16.5 17.5l1.5 1.5 3-3"/>'
    specs["status/network-wireless-available.svg"] = _wifi_arcs_markup(3, "ColorScheme-Text", dot_cls="accent-fill") + '<circle class="accent-fill" cx="18.5" cy="18" r="1.4"/>'
    specs["status/network-wireless-hotspot-symbolic.svg"] = V15_ICON_SPECS["status/network-wireless-hotspot.svg"] + sym_ring
    specs["status/network-wireless-disconnected-symbolic.svg"] = (
        '<path class="dimmed" d="M9.5 16.5a3.5 3.5 0 0 1 5 0M7 14a7.1 7.1 0 0 1 10 0M4.5 11.5a10.6 10.6 0 0 1 15 0M2 9a14.1 14.1 0 0 1 20 0"/>'
        '<circle class="dimmed" cx="12" cy="19" r="1.5"/><path d="M5 5l14 14"/><path class="negative" d="M9 9l6 6"/>'
    ) + sym_ring

    for idx, pct in enumerate((0, 20, 40, 60, 80, 100)):
        bars = ['<path class="accent" d="M3 5h5"/>']
        for b in range(1, 6):
            x = 3 + (b - 1) * 4
            h = 3 + (b - 1) * 3.5
            y = 20 - h
            lit = b <= idx
            if not lit:
                c = "dimmed-fill"
            elif pct <= 20:
                c = _level_class(pct, fill=True)
            elif pct >= 80 and b == idx:
                c = "ColorScheme-PositiveText lime-fill"
            else:
                c = "ColorScheme-Text text-fill"
            bars.append(f'<rect class="{c}" x="{x}" y="{y}" width="2.4" height="{h}" rx="0.6"/>')
        specs[f"status/network-mobile-{pct}.svg"] = "".join(bars)
    specs["status/network-mobile-off.svg"] = specs["status/network-mobile-0.svg"] + '<path d="M4 4l16 16"/><path class="ColorScheme-NegativeText negative" d="M9 9l6 6"/>'
    specs["status/network-mobile-acquiring.svg"] = specs["status/network-mobile-60.svg"] + '<circle class="lime-fill nf-pulse" cx="11" cy="5.5" r="1.5"><animate attributeName="opacity" values="0.9;0.3;0.9" dur="1.4s" repeatCount="indefinite"/></circle>'

    specs["status/network-vpn.svg"] = '<path d="M12 3l8 3v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6z"/><path class="accent" d="M6.5 7.5l5.5-2 5.5 2"/><rect class="lime" x="9.5" y="11" width="5" height="4.5" rx="1"/><path class="lime" d="M10.5 11V9.5a1.5 1.5 0 0 1 3 0V11"/><circle class="lime-fill" cx="12" cy="13.2" r="0.8"/>'
    specs["status/network-vpn-symbolic.svg"] = specs["status/network-vpn.svg"] + sym_ring
    specs["status/network-vpn-acquiring.svg"] = (
        '<path d="M12 3l8 3v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6z"/>'
        '<circle class="ColorScheme-Text text-fill nf-pulse" cx="9" cy="12" r="1.1"/>'
        '<circle class="accent-fill nf-pulse" cx="12" cy="12" r="1.1"/>'
        '<circle class="ColorScheme-Text text-fill nf-pulse" cx="15" cy="12" r="1.1"/>'
        '<animate attributeName="opacity" values="0.9;0.45;0.9" dur="1.4s" repeatCount="indefinite"/>'
    )
    specs["status/network-vpn-disconnected.svg"] = '<path class="dimmed" d="M12 3l8 3v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6z"/><path d="M5 5l14 14"/><path class="ColorScheme-NegativeText negative" d="M9 9l6 6"/>'
    specs["status/network-flightmode-on.svg"] = '<path d="M12 2v7l8 4v2l-8-2v5l3 2v1l-3-1-3 1v-1l3-2v-5l-8 2v-2l8-4V2z"/><path class="accent" d="M12 2v3.5"/>'
    specs["status/network-flightmode-off.svg"] = '<path class="dimmed" d="M12 2v7l8 4v2l-8-2v5l3 2v1l-3-1-3 1v-1l3-2v-5l-8 2v-2l8-4V2z"/><path d="M4 4l16 16"/><path class="ColorScheme-NegativeText negative" d="M9 9l6 6"/>'
    return specs


def _build_v20_audio_brightness_specs() -> dict[str, str]:
    specs: dict[str, str] = {}
    speaker = '<path d="M3 9.5h4l5-4v13l-5-4H3z"/><path class="accent" d="M12 7.5v3"/>'
    w1 = "M15 9.5a4 4 0 0 1 0 5"
    w2 = "M17.5 7a7.5 7.5 0 0 1 0 10"
    w3 = "M20 4.5a11 11 0 0 1 0 15"
    sym_ring = '<path class="symbolic-ring" d="M4 17.5h3"/>'

    specs["status/audio-volume-muted.svg"] = '<path d="M3 9.5h4l5-4v13l-5-4H3zM16 9l5 6M21 9l-5 6"/><path class="ColorScheme-NegativeText negative" d="M17 10l3 4"/>'
    specs["status/audio-volume-low.svg"] = f'{speaker}<path d="{w1}"/><path class="dimmed" d="{w2}"/><path class="dimmed" d="{w3}"/>'
    specs["status/audio-volume-medium.svg"] = f'{speaker}<path d="{w1}"/><path d="{w2}"/><path class="dimmed" d="{w3}"/>'
    specs["status/audio-volume-high.svg"] = f'{speaker}<path d="{w1}"/><path d="{w2}"/><path d="{w3}"/>'
    specs["status/audio-volume-high-warning.svg"] = f'{speaker}<path d="{w1}"/><path d="{w2}"/><path class="ColorScheme-NeutralText warning" d="{w3}"/><circle class="ColorScheme-NeutralText warning-fill" cx="12" cy="3.5" r="1"/>'
    specs["status/audio-volume-high-danger.svg"] = f'{speaker}<path d="{w1}"/><path class="ColorScheme-NeutralText warning" d="{w2}"/><path class="ColorScheme-NegativeText negative" d="{w3}"/><path class="ColorScheme-NegativeText negative" d="M12 2.5v2.5"/>'

    for suffix in ("muted", "low", "medium", "high"):
        specs[f"status/audio-volume-{suffix}-symbolic.svg"] = specs[f"status/audio-volume-{suffix}.svg"] + sym_ring

    mic_shell = '<rect x="9" y="3" width="6" height="10" rx="3"/><path d="M6 10a6 6 0 0 0 12 0M12 16v5M8 21h8"/>'
    specs["status/microphone-sensitivity-muted.svg"] = f'{mic_shell}<path d="M5 5l14 14"/><path class="ColorScheme-NegativeText negative" d="M9 9l6 6"/>'
    specs["status/microphone-sensitivity-low.svg"] = f'{mic_shell}<path class="dimmed" d="M12 7.5v2.5"/>'
    specs["status/microphone-sensitivity-medium.svg"] = f'{mic_shell}<path d="M12 6.5v3.5"/>'
    specs["status/microphone-sensitivity-high.svg"] = f'{mic_shell}<path d="M12 6v4"/><circle class="accent-fill" cx="12" cy="18.5" r="1"/>'
    for suffix in ("muted", "low", "medium", "high"):
        specs[f"status/microphone-sensitivity-{suffix}-symbolic.svg"] = specs[f"status/microphone-sensitivity-{suffix}.svg"] + sym_ring

    sun_core = '<circle cx="12" cy="12" r="4"/>'
    rays_low = '<path class="dimmed" d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2"/>'
    rays_med = '<path d="M12 2v3M12 19v3M2 12h3M19 12h3"/><circle class="accent-fill" cx="12" cy="12" r="0.9"/>'
    rays_high = '<path class="lime" d="M12 2v3"/><path d="M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M19.1 4.9L17 7M7 17l-2.1 2.1"/><circle class="accent-fill" cx="12" cy="12" r="1.1"/>'
    specs["status/display-brightness-off.svg"] = '<circle class="dimmed" cx="12" cy="12" r="4"/><path d="M5 5l14 14"/><path class="ColorScheme-NegativeText negative" d="M9 9l6 6"/>'
    specs["status/display-brightness-low.svg"] = sun_core + rays_low
    specs["status/display-brightness-medium.svg"] = sun_core + rays_med
    specs["status/display-brightness-high.svg"] = sun_core + rays_high
    for level in ("off", "low", "medium", "high"):
        specs[f"status/display-brightness-{level}-symbolic.svg"] = specs[f"status/display-brightness-{level}.svg"] + sym_ring

    specs["applets/brightness-high.svg"] = sun_core + rays_high + '<circle class="dimmed" cx="12" cy="12" r="6.5" stroke-dasharray="2 3"/>'
    specs["applets/brightness-high-symbolic.svg"] = specs["applets/brightness-high.svg"] + '<path class="symbolic-ring" d="M6 21.5h12"/>'
    specs["applets/brightness-low.svg"] = sun_core + rays_low + '<circle class="dimmed" cx="12" cy="12" r="6.5" stroke-dasharray="1 4"/>'
    specs["applets/brightness-low-symbolic.svg"] = specs["applets/brightness-low.svg"] + '<path class="symbolic-ring" d="M6 21.5h12"/>'

    kbd_base = '<path class="dimmed" d="M4 17h16"/>'
    specs["status/keyboard-brightness-off.svg"] = f'{kbd_base}<path class="dimmed" d="M12 9v3M7 11l2 2M17 11l-2 2"/><path d="M5 5l14 14"/><path class="ColorScheme-NegativeText negative" d="M9 9l6 6"/>'
    specs["status/keyboard-brightness-low.svg"] = '<path d="M5 17h14"/><path class="dimmed" d="M12 8v3M7 10l2 2M17 10l-2 2"/>'
    specs["status/keyboard-brightness-medium.svg"] = '<path d="M4 17h16M12 7v4M6.5 10l2.5 2.5M17.5 10L15 12.5"/><path class="accent" d="M10 17h4"/>'
    specs["status/keyboard-brightness-high.svg"] = '<path d="M3 17h18M12 6v5M6 9l3 3M18 9l-3 3M3 13l3 1.5M21 13l-3 1.5"/><path class="accent" d="M9 17h6"/><circle class="lime-fill" cx="12" cy="3.5" r="0.9"/>'
    return specs


def _build_v20_misc_kinetic_specs() -> dict[str, str]:
    bt_glyph = '<path d="M7.5 8L16.5 16L12 20V4L16.5 8L7.5 16"/>'
    bt_dim = '<path class="dimmed" d="M7.5 8L16.5 16L12 20V4L16.5 8L7.5 16"/>'
    return {
        "status/network-bluetooth.svg": bt_glyph + '<circle class="accent-fill" cx="17" cy="12" r="1.1"/>',
        "status/network-bluetooth-activated.svg": bt_glyph + '<path class="accent" d="M18 9a4.5 4.5 0 0 1 0 6"/>',
        "status/network-bluetooth-inactive.svg": bt_dim + '<path d="M4 4l16 16"/><path class="ColorScheme-NegativeText negative" d="M9 9l6 6"/>',
        "status/bluetooth-active.svg": bt_glyph + '<circle class="accent-fill" cx="5.5" cy="12" r="1.1"/>',
        "status/bluetooth-disabled.svg": bt_dim + '<path d="M5 5l14 14"/><path class="ColorScheme-NegativeText negative" d="M9 9l6 6"/>',
        "status/bluetooth-acquiring.svg": (
            bt_glyph
            + '<circle class="accent nf-pulse" cx="12" cy="12" r="9.5" stroke-dasharray="3 4">'
            '<animate attributeName="opacity" values="0.2;0.8;0.2" dur="1.4s" repeatCount="indefinite"/></circle>'
        ),
        "status/media-playback-playing.svg": (
            '<circle cx="12" cy="12" r="9"/><path d="M10 8.5l6.5 3.5-6.5 3.5z"/><path class="accent" d="M10 9.5v5"/>'
        ),
        "status/software-update-available.svg": (
            '<path class="nf-pulse" d="M12 3v11M7 10l5 5 5-5"><animateTransform attributeName="transform" type="translate" values="0 -1;0 1;0 -1" dur="1.4s" repeatCount="indefinite"/></path>'
            '<path d="M5 19h14"/><path class="accent" d="M9 19h6"/>'
        ),
        "status/software-update-urgent.svg": (
            '<path d="M12 3l8 3v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6z"/>'
            '<path class="ColorScheme-NegativeText negative nf-pulse" d="M12 8v5"/><circle class="ColorScheme-NegativeText negative-fill" cx="12" cy="15.8" r="1.1"/>'
        ),
        "animations/process-working.svg": (
            '<g class="nf-spin"><circle class="dimmed" cx="12" cy="12" r="8"/>'
            '<path class="lime" d="M12 4a8 8 0 0 1 8 8"/>'
            '<path class="accent" stroke-width="1.4" d="M12 20A8 8 0 0 1 5.07 16"/>'
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
    step = 360.0 / frames
    stroke_w = 1.8 if optical_size == 16 else 1.9
    end_x = round(cx - r * 0.866, 2)
    end_y = round(cx + r * 0.5, 2)
    frame_groups = []
    for idx in range(frames):
        y_off = idx * optical_size
        angle = round(idx * step, 2)
        frame_groups.append(
            f'  <g transform="translate(0 {y_off})">'
            f'<circle class="dimmed" cx="{cx}" cy="{cx}" r="{r}"/>'
            f'<g transform="rotate({angle} {cx} {cx})">'
            f'<path class="lime" d="M{cx} {round(cx - r, 2)}a{r} {r} 0 0 1 {r} {r}"/>'
            f'<path class="accent" stroke-width="1.5" d="M{cx} {round(cx + r, 2)}A{r} {r} 0 0 1 {end_x} {end_y}"/>'
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
    </style>
    <style id="noxforge-icon-style" type="text/css">
      .accent {{ color: {COLORS["detailCyan"]}; stroke: currentColor; }}
      .accent-fill {{ color: {COLORS["detailCyan"]}; fill: currentColor; stroke: none; }}
      .lime {{ color: {COLORS["accent"]}; stroke: currentColor; }}
      .lime-fill {{ color: {COLORS["accent"]}; fill: currentColor; stroke: none; }}
      .dimmed {{ opacity: 0.25; stroke: {COLORS["textDisabled"]}; }}
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
    "apps/noxforge-controlcenter.svg": "apps/io.github.loofiboss.noxforge.controlcenter.svg",
    "apps/noxforge-opacity.svg": "apps/io.github.loofiboss.noxforge.opacity.svg",
    "apps/visual-studio-code.svg": "apps/code.svg",
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
    "apps/noxforge-controlcenter.svg",
    "apps/noxforge-opacity.svg",
    "apps/visual-studio-code.svg",
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
    ("apps/io.github.loofiboss.noxforge.controlcenter.svg", "apps/noxforge-controlcenter.svg"),
    ("apps/io.github.loofiboss.noxforge.opacity.svg", "apps/noxforge-opacity.svg"),
    ("apps/code.svg", "apps/visual-studio-code.svg"),
    ("categories/applications-internet.svg", "preferences/preferences-system-network.svg"),
    ("devices/network-wired.svg", "status/network-wired-activated.svg", "status/network-wired.svg"),
    ("devices/network-wireless.svg", "status/network-wireless-connected-100.svg", "status/network-wireless.svg"),
    ("mimetypes/inode-directory.svg", "places/folder.svg"),
)


def semantic_variant(body: str, relative: str) -> str:
    """Keep related alias SVGs byte-distinct without adding visual noise."""
    slug = relative.removesuffix(".svg").replace("/", "-")
    return f'<g id="nf-{slug}">{body}</g>'


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
    </style>
    <style id="noxforge-icon-style" type="text/css">
      .text-fill {{ color: {COLORS["textPrimary"]}; fill: currentColor; opacity: 0.92; stroke: none; }}
      .surface-plate {{ fill: {COLORS["surfaceRaised"]}; fill-opacity: 0.90; stroke: none; }}
      .surface-tab {{ fill: {COLORS["surface"]}; fill-opacity: 0.92; stroke: none; }}
      .surface-bevel {{ stroke: {COLORS["edgeHighlight"]}; stroke-width: 1; opacity: 0.72; }}
      .accent {{ color: {COLORS["detailCyan"]}; stroke: currentColor; }}
      .accent-fill {{ color: {COLORS["detailCyan"]}; fill: currentColor; stroke: none; }}
      .lime {{ color: {COLORS["accent"]}; stroke: currentColor; }}
      .lime-fill {{ color: {COLORS["accent"]}; fill: currentColor; stroke: none; }}
      .dimmed {{ opacity: 0.28; stroke: currentColor; }}
      .dimmed-fill {{ opacity: 0.24; fill: currentColor; stroke: none; }}
      .symbolic-ring {{ opacity: 0.35; stroke: currentColor; stroke-width: 1; }}
      .warning {{ color: {COLORS["neutral"]}; stroke: currentColor; opacity: 0.9; }}
      .warning-fill {{ color: {COLORS["neutral"]}; fill: currentColor; opacity: 0.9; stroke: none; }}
      .negative {{ color: {COLORS["negative"]}; stroke: currentColor; opacity: 0.92; }}
      .negative-fill {{ color: {COLORS["negative"]}; fill: currentColor; opacity: 0.92; stroke: none; }}
    </style>{motion_block}
  </defs>
  <g fill="none" stroke="currentColor" class="ColorScheme-Text" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round">
    {body}
  </g>
</svg>
'''


def decoration_frame(
    prefix: str,
    x: int,
    y: int,
    css_class: str,
    opacity: float,
    *,
    active: bool,
    shadow: bool = True,
    maximized: bool = False,
) -> str:
    """Build Aurorae v2 9-patch frame with optional stepped ambient shadow & flat maximized corners."""
    def name(position: str) -> str:
        return f"{prefix}-{position}"

    attr = f'class="{css_class}" fill="currentColor" fill-opacity="{opacity:g}"'
    border_class = "NoxForge-EdgeHighlight" if active else "NoxForge-OutlineMuted"
    b_fill = f'class="{border_class}" fill="currentColor"'
    b_attr = f'class="{border_class}" stroke="currentColor" fill="none" stroke-width="1"'
    s_fill = 'class="NoxForge-OverlayShadow" fill="currentColor"'

    pl = 12 if shadow else 0
    pr = 12 if shadow else 0
    pt = 8 if shadow else 0
    pb = 16 if shadow else 0
    fx = x + pl
    fy = y + pt

    top = f'<g id="{name("top")}">'
    if shadow:
        top += f'<rect x="{fx + 6}" y="{y + 2}" width="28" height="6" {s_fill} fill-opacity="0.14"/>'
        top += f'<rect x="{fx + 6}" y="{y + 5}" width="28" height="3" {s_fill} fill-opacity="0.28"/>'
    top += f'<rect x="{fx + 6}" y="{fy}" width="28" height="6" {attr}/>'
    top += f'<rect x="{fx + 6}" y="{fy}" width="28" height="1" {b_fill}/>'
    if active:
        rail = EDGE_POLISH["aurorae"]
        top += (
            f'<path d="M{fx + 8} {fy + 1}h{rail["activeRailLength"]}" '
            'class="ColorScheme-Highlight" stroke="currentColor" '
            f'stroke-width="{rail["activeRailThickness"]}"/>'
        )
    top += "</g>"

    if maximized:
        topleft = (
            f'<g id="{name("topleft")}">'
            f'<rect x="{fx}" y="{fy}" width="6" height="6" {attr}/>'
            f'<rect x="{fx}" y="{fy}" width="6" height="1" {b_fill}/>'
            f'</g>'
        )
        topright = (
            f'<g id="{name("topright")}">'
            f'<rect x="{fx + 34}" y="{fy}" width="6" height="6" {attr}/>'
            f'<rect x="{fx + 34}" y="{fy}" width="6" height="1" {b_fill}/>'
            f'</g>'
        )
        bottomleft = (
            f'<g id="{name("bottomleft")}">'
            f'<rect x="{fx}" y="{fy + 34}" width="6" height="6" {attr}/>'
            f'<rect x="{fx}" y="{fy + 39}" width="6" height="1" {b_fill}/>'
            f'</g>'
        )
        bottomright = (
            f'<g id="{name("bottomright")}">'
            f'<rect x="{fx + 34}" y="{fy + 34}" width="6" height="6" {attr}/>'
            f'<rect x="{fx + 34}" y="{fy + 39}" width="6" height="1" {b_fill}/>'
            f'</g>'
        )
    else:
        topleft = f'<g id="{name("topleft")}">'
        if shadow:
            topleft += f'<rect x="{x + 4}" y="{y + 2}" width="{pl + 2}" height="{pt + 4}" rx="6" {s_fill} fill-opacity="0.14"/>'
            topleft += f'<rect x="{x + 8}" y="{y + 5}" width="{pl - 2}" height="{pt + 1}" rx="4" {s_fill} fill-opacity="0.28"/>'
        topleft += (
            f'<path d="M{fx + 4} {fy}H{fx + 6}V{fy + 6}H{fx}V{fy + 4}Z" {attr}/>'
            f'<rect x="{fx + 4}" y="{fy}" width="2" height="1" {b_fill}/>'
            f'<line x1="{fx + 4}" y1="{fy}" x2="{fx}" y2="{fy + 4}" {b_attr}/>'
            f'<rect x="{fx}" y="{fy + 4}" width="1" height="2" {b_fill}/>'
            f'</g>'
        )
        topright = f'<g id="{name("topright")}">'
        if shadow:
            topright += f'<rect x="{fx + 34}" y="{y + 2}" width="{pr + 2}" height="{pt + 4}" rx="6" {s_fill} fill-opacity="0.14"/>'
            topright += f'<rect x="{fx + 34}" y="{y + 5}" width="{pr - 2}" height="{pt + 1}" rx="4" {s_fill} fill-opacity="0.28"/>'
        topright += (
            f'<path d="M{fx + 34} {fy}A6 6 0 0 1 {fx + 40} {fy + 6}H{fx + 34}Z" {attr}/>'
            f'<path d="M{fx + 34} {fy + 0.5}A5.5 5.5 0 0 1 {fx + 39.5} {fy + 6}" {b_attr}/>'
            f'</g>'
        )
        bottomleft = f'<g id="{name("bottomleft")}">'
        if shadow:
            bottomleft += f'<rect x="{x + 2}" y="{fy + 34}" width="{pl + 4}" height="{pb + 2}" rx="8" {s_fill} fill-opacity="0.12"/>'
            bottomleft += f'<rect x="{x + 6}" y="{fy + 34}" width="{pl}" height="{pb - 4}" rx="6" {s_fill} fill-opacity="0.24"/>'
            bottomleft += f'<rect x="{x + 9}" y="{fy + 34}" width="{pl - 3}" height="{pb - 9}" rx="4" {s_fill} fill-opacity="0.38"/>'
        bottomleft += (
            f'<path d="M{fx} {fy + 34}H{fx + 6}V{fy + 40}A6 6 0 0 1 {fx} {fy + 34}Z" {attr}/>'
            f'<path d="M{fx + 6} {fy + 39.5}A5.5 5.5 0 0 1 {fx + 0.5} {fy + 34}" {b_attr}/>'
            f'</g>'
        )
        bottomright = f'<g id="{name("bottomright")}">'
        if shadow:
            bottomright += f'<rect x="{fx + 34}" y="{fy + 34}" width="{pr + 4}" height="{pb + 2}" rx="8" {s_fill} fill-opacity="0.12"/>'
            bottomright += f'<rect x="{fx + 34}" y="{fy + 34}" width="{pr}" height="{pb - 4}" rx="6" {s_fill} fill-opacity="0.24"/>'
            bottomright += f'<rect x="{fx + 34}" y="{fy + 34}" width="{pr - 3}" height="{pb - 9}" rx="4" {s_fill} fill-opacity="0.38"/>'
        bottomright += (
            f'<path d="M{fx + 34} {fy + 34}H{fx + 40}A6 6 0 0 1 {fx + 34} {fy + 40}Z" {attr}/>'
            f'<path d="M{fx + 39.5} {fy + 34}A5.5 5.5 0 0 1 {fx + 34} {fy + 39.5}" {b_attr}/>'
            f'</g>'
        )

    left = f'<g id="{name("left")}">'
    if shadow:
        left += f'<rect x="{x + 2}" y="{fy + 6}" width="{pl - 2}" height="28" {s_fill} fill-opacity="0.12"/>'
        left += f'<rect x="{x + 6}" y="{fy + 6}" width="{pl - 6}" height="28" {s_fill} fill-opacity="0.26"/>'
    left += f'<rect x="{fx}" y="{fy + 6}" width="6" height="28" {attr}/><rect x="{fx}" y="{fy + 6}" width="1" height="28" {b_fill}/></g>'

    center = f'<rect id="{name("center")}" x="{fx + 6}" y="{fy + 6}" width="28" height="28" {attr}/>'

    right = f'<g id="{name("right")}">'
    if shadow:
        right += f'<rect x="{fx + 40}" y="{fy + 6}" width="{pr - 2}" height="28" {s_fill} fill-opacity="0.12"/>'
        right += f'<rect x="{fx + 40}" y="{fy + 6}" width="{pr - 6}" height="28" {s_fill} fill-opacity="0.26"/>'
    right += f'<rect x="{fx + 34}" y="{fy + 6}" width="6" height="28" {attr}/><rect x="{fx + 39}" y="{fy + 6}" width="1" height="28" {b_fill}/></g>'

    bottom = f'<g id="{name("bottom")}">'
    if shadow:
        bottom += f'<rect x="{fx + 6}" y="{fy + 40}" width="28" height="{pb}" {s_fill} fill-opacity="0.12"/>'
        bottom += f'<rect x="{fx + 6}" y="{fy + 40}" width="28" height="{pb - 5}" {s_fill} fill-opacity="0.24"/>'
        bottom += f'<rect x="{fx + 6}" y="{fy + 40}" width="28" height="{pb - 10}" {s_fill} fill-opacity="0.38"/>'
    bottom += f'<rect x="{fx + 6}" y="{fy + 34}" width="28" height="6" {attr}/><rect x="{fx + 6}" y="{fy + 39}" width="28" height="1" {b_fill}/></g>'

    return "\n".join([topleft, top, topright, left, center, right, bottomleft, bottom, bottomright])


def decoration_svg(colors: dict[str, str] = COLORS) -> str:
    active = decoration_frame("decoration", 0, 0, "ColorScheme-Raised", 1.0, active=True, shadow=True, maximized=False)
    inactive = decoration_frame("decoration-inactive", 76, 0, "ColorScheme-Sunken", 0.9, active=False, shadow=True, maximized=False)
    maximized = decoration_frame("decoration-maximized", 152, 8, "ColorScheme-Raised", 1.0, active=True, shadow=False, maximized=True)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="64" viewBox="0 0 200 64">
  <defs>
    <style id="current-color-scheme" type="text/css"><![CDATA[
      .ColorScheme-Raised {{ color: {colors["surfaceRaised"]}; }}
      .ColorScheme-Sunken {{ color: {colors["surfaceSunken"]}; }}
      .ColorScheme-Highlight {{ color: {colors["accent"]}; }}
      .NoxForge-EdgeHighlight {{ color: {colors["edgeHighlight"]}; }}
      .NoxForge-OutlineMuted {{ color: {colors["border"]}; }}
      .NoxForge-OverlayShadow {{ color: {colors.get("shadowOverlay", "#050708")}; }}
    ]]></style>
  </defs>
  {active}
  {inactive}
  {maximized}
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
    duotone_places = build_duotone_places_specs(TOKENS["accents"])
    duotone_mimetypes = build_duotone_mimetype_specs()
    duotone_apps = build_duotone_apps_specs()
    specs = {
        **ICON_SPECS,
        **CORE_ICON_SPECS,
        **STATE_ICON_SPECS,
        **V5_RUNTIME_ICON_SPECS,
        **PHASE6_PRIORITY_ICON_SPECS,
        **V7_CORE_ICON_SPECS,
        **V15_ICON_SPECS,
        **V20_KINETIC_ICON_SPECS,
        **duotone_places,
        **duotone_mimetypes,
        **duotone_apps,
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
    duotone_contexts = ("apps/", "places/", "mimetypes/")
    duotone_optical = {
        relative: body for relative, body in specs.items()
        if relative.startswith(duotone_contexts)
    }
    small_optical_count = 0
    for size in fixture["opticalSizes"]:
        for relative, body in sorted(optical.items()):
            small_body = MONOLINE_PLACES_OVERRIDE.get(relative, body)
            if relative == "animations/process-working.svg":
                write(ICONS / f"{size}x{size}" / relative, process_working_sprite_svg(size, frames=16))
            else:
                write(ICONS / f"{size}x{size}" / relative, icon_svg(small_body, size))
            small_optical_count += 1
    duotone_sizes = (32, 48, 64)
    duotone_optical_count = 0
    for size in duotone_sizes:
        for relative, body in sorted(duotone_optical.items()):
            write(ICONS / f"{size}x{size}" / relative, icon_svg(body, size))
            duotone_optical_count += 1
    total_optical_count = small_optical_count + duotone_optical_count
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
                "opticalCount": total_optical_count,
                "opticalSizes": [16, 22, 32, 48, 64],
                "smallOpticalCount": small_optical_count,
                "duotoneOpticalCount": duotone_optical_count,
                "opticalStrokeWidths": {"16": 1.9, "22": 1.75, "32": 1.7, "48": 1.7, "64": 1.7},
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
            f"Verified {len(specs)} scalable icons, {total_optical_count} optical variants "
            f"and {len(aurorae_targets) * (1 + len(GLYPHS))} Aurorae pairs"
        )
        return
    print(
        f"Generated {len(specs)} scalable icons, {total_optical_count} optical variants "
        f"and {len(aurorae_targets) * (1 + len(GLYPHS))} Aurorae pairs"
    )


if __name__ == "__main__":
    main()
