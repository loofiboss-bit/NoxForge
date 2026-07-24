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
ICONS = ROOT / "icons/NoxForge"
TOKENS = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))
COLORS = TOKENS["colors"]
CHECK = "--check" in sys.argv[1:]
DRIFT: list[Path] = []

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

CORE_ICON_SPECS = {
    "actions/edit-cut.svg": '<path d="M5 5l14 14M19 5L5 19"/><circle cx="7" cy="17" r="3"/><circle cx="17" cy="17" r="3"/><path class="accent" d="M10 10l2 2"/>',
    "actions/edit-undo.svg": '<path d="M9 7L4 12l5 5M5 12h8a6 6 0 0 1 6 6"/><path class="accent" d="M4 12h5"/>',
    "actions/edit-redo.svg": '<path d="M15 7l5 5-5 5M19 12h-8a6 6 0 0 0-6 6"/><path class="accent" d="M15 12h5"/>',
    "actions/go-next.svg": '<path d="M8 5l7 7-7 7"/><path class="accent" d="M15 12h5"/>',
    "actions/list-add.svg": '<path d="M5 7h10M5 12h10M5 17h7M19 14v6M16 17h6"/><path class="accent" d="M16 17h6"/>',
    "actions/media-playback-start.svg": '<path d="M7 4l13 8-13 8z"/><path class="accent" d="M7 4v6"/>',
    "actions/view-refresh.svg": '<path d="M19 8V4l-3 3a8 8 0 1 0 2 9M19 4h-5"/><path class="accent" d="M16 7l3-3"/>',
    "categories/applications-system.svg": '<rect x="3" y="3" width="8" height="8"/><rect x="13" y="3" width="8" height="8"/><rect x="3" y="13" width="8" height="8"/><rect x="13" y="13" width="8" height="8"/><path class="accent" d="M13 3h8v3"/>',
    "categories/applications-development.svg": '<path d="M9 5l-6 7 6 7M15 5l6 7-6 7M13 3l-2 18"/><path class="accent" d="M15 5l3 3"/>',
    "categories/applications-graphics.svg": '<path d="M4 20l4-12 8-4 4 4-4 8zM8 8l8 8"/><circle cx="16" cy="8" r="1.5"/><path class="accent" d="M4 20l5-1"/>',
    "categories/applications-internet.svg": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 4 6 4 9s-1 6-4 9M12 3c-3 3-4 6-4 9s1 6 4 9"/><path class="accent" d="M12 3v4"/>',
    "categories/applications-multimedia.svg": '<rect x="3" y="5" width="18" height="14"/><path d="M9 9l7 3-7 3z"/><path class="accent" d="M3 5h8"/>',
    "devices/camera-photo.svg": '<path d="M3 8h4l2-3h6l2 3h4v11H3z"/><circle cx="12" cy="13" r="4"/><path class="accent" d="M17 8h4"/>',
    "devices/printer.svg": '<path d="M6 9V3h12v6M6 17H3V9h18v8h-3M6 14h12v7H6z"/><path class="accent" d="M16 12h2"/>',
    "devices/audio-headphones.svg": '<path d="M4 13a8 8 0 0 1 16 0v7h-4v-6h4M4 14h4v6H4z"/><path class="accent" d="M4 13a8 8 0 0 1 3-6"/>',
    "devices/media-removable.svg": '<path d="M7 3h10v8l3 3v7H4v-7l3-3zM7 11h10"/><path class="accent" d="M10 6h4"/>',
    "emblems/emblem-favorite.svg": '<path d="M12 3l2.7 5.5 6.1.9-4.4 4.3 1 6.1-5.4-2.9-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/><path class="accent" d="M12 3v6"/>',
    "emblems/emblem-important.svg": '<path d="M12 3v12"/><circle cx="12" cy="20" r="1"/><path class="accent" d="M12 3v5"/>',
    "emblems/emblem-shared.svg": '<circle cx="6" cy="12" r="3"/><circle cx="18" cy="6" r="3"/><circle cx="18" cy="18" r="3"/><path d="M9 11l6-4M9 13l6 4"/><path class="accent" d="M15 7l3-1"/>',
    "mimetypes/text-x-generic.svg": '<path d="M6 3h9l4 4v14H6zM15 3v5h4M9 12h7M9 16h7"/><path class="accent" d="M9 12h4"/>',
    "mimetypes/application-pdf.svg": '<path d="M6 3h9l4 4v14H6zM15 3v5h4M9 16c3-6 5-6 7 0M10 13h5"/><path class="accent" d="M9 16h3"/>',
    "mimetypes/package-x-generic.svg": '<path d="M3 7l9-4 9 4v10l-9 4-9-4zM3 7l9 4 9-4M12 11v10"/><path class="accent" d="M12 3l5 2"/>',
    "mimetypes/image-x-generic.svg": '<rect x="3" y="4" width="18" height="16"/><circle cx="8" cy="9" r="2"/><path d="M4 18l5-5 3 3 3-4 5 6"/><path class="accent" d="M15 12l5 6"/>',
    "mimetypes/audio-x-generic.svg": '<path d="M9 18V6l10-2v12M9 10l10-2"/><circle cx="6" cy="18" r="3"/><circle cx="16" cy="16" r="3"/><path class="accent" d="M9 6l5-1"/>',
    "mimetypes/video-x-generic.svg": '<rect x="3" y="5" width="18" height="14"/><path d="M10 9l6 3-6 3zM3 9h3M18 9h3"/><path class="accent" d="M10 9v3"/>',
    "places/folder-documents.svg": '<path d="M3 6h7l2 2h9v11H3zM8 11h8M8 15h6"/><path class="accent" d="M8 11h5"/>',
    "places/user-trash.svg": '<path d="M5 7h14M9 7V4h6v3M7 7l1 14h8l1-14M10 11v6M14 11v6"/><path class="accent" d="M5 7h4"/>',
    "preferences/preferences-system.svg": '<path d="M4 6h16M4 12h16M4 18h16"/><circle cx="9" cy="6" r="2"/><circle cx="15" cy="12" r="2"/><circle cx="11" cy="18" r="2"/><path class="accent" d="M9 4v4"/>',
    "preferences/preferences-desktop-theme.svg": '<rect x="3" y="4" width="18" height="14"/><path d="M8 22h8M12 18v4M6 8h12M6 12h7"/><path class="accent" d="M6 8h5"/>',
    "preferences/preferences-system-network.svg": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 4 6 4 9s-1 6-4 9M12 3c-3 3-4 6-4 9s1 6 4 9"/><path class="accent" d="M12 3v4"/>',
    "preferences/preferences-system-power-management.svg": '<path d="M12 3v8M7 6a8 8 0 1 0 10 0"/><path class="accent" d="M12 3v5"/>',
    "status/dialog-information.svg": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6"/><circle cx="12" cy="7" r="1"/><path class="accent" d="M12 11v3"/>',
    "status/dialog-error.svg": '<circle cx="12" cy="12" r="9"/><path d="M8 8l8 8M16 8l-8 8"/><path class="accent" d="M8 8l4 4"/>',
    "status/security-high.svg": '<path d="M12 3l8 3v6c0 5-3 8-8 10-5-2-8-5-8-10V6zM8 12l3 3 5-6"/><path class="accent" d="M8 12l3 3"/>',
    "status/software-update-available.svg": '<path d="M12 3v12M7 10l5 5 5-5M5 20h14"/><path class="accent" d="M12 3v6"/>',
}

STATE_ICON_SPECS = {
    "actions/go-previous.svg": '<path d="M16 5l-7 7 7 7"/><path class="accent" d="M9 12H4"/>',
    "actions/go-up.svg": '<path d="M5 16l7-7 7 7"/><path class="accent" d="M12 9V4"/>',
    "actions/go-down.svg": '<path d="M5 8l7 7 7-7"/><path class="accent" d="M12 15v5"/>',
    "actions/media-playback-pause.svg": '<path d="M7 5v14M17 5v14"/><path class="accent" d="M7 5v6"/>',
    "actions/media-playback-stop.svg": '<rect x="6" y="6" width="12" height="12"/><path class="accent" d="M6 6h6"/>',
    "actions/media-skip-backward.svg": '<path d="M18 5l-9 7 9 7zM6 5v14"/><path class="accent" d="M6 5v7"/>',
    "actions/zoom-in.svg": '<circle cx="10" cy="10" r="6"/><path d="M14.5 14.5L21 21M7 10h6M10 7v6"/><path class="accent" d="M10 7v3"/>',
    "actions/zoom-out.svg": '<circle cx="10" cy="10" r="6"/><path d="M14.5 14.5L21 21M7 10h6"/><path class="accent" d="M7 10h3"/>',
    "applets/bluetooth-active.svg": '<path d="M8 6l8 12V6L8 18l8-12"/><path class="accent" d="M8 6l8 12"/>',
    "applets/bluetooth-disabled.svg": '<path d="M9 7l7 11V6l-4 6M5 5l14 14"/><path class="accent" d="M5 5l6 6"/>',
    "applets/redshift-status-day.svg": '<circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/><path class="accent" d="M12 2v3"/>',
    "applets/redshift-status-off.svg": '<circle cx="12" cy="12" r="7"/><path d="M5 5l14 14"/><path class="accent" d="M5 5l5 5"/>',
    "applets/redshift-status-on.svg": '<path d="M17 15a7 7 0 1 1-8-10 6 6 0 0 0 8 10z"/><path class="accent" d="M17 15a7 7 0 0 1-4 3"/>',
    "status/audio-volume-low.svg": '<path d="M3 9h4l5-4v14l-5-4H3zM16 10a3 3 0 0 1 0 4"/><path class="accent" d="M12 6v4"/>',
    "status/audio-volume-medium.svg": '<path d="M3 9h4l5-4v14l-5-4H3zM16 9a5 5 0 0 1 0 6"/><path class="accent" d="M12 6v4"/>',
    "status/audio-volume-muted.svg": '<path d="M3 9h4l5-4v14l-5-4H3zM16 9l5 6M21 9l-5 6"/><path class="accent" d="M16 9l3 3"/>',
    "status/battery-low.svg": '<rect x="3" y="6" width="17" height="12" rx="2"/><path d="M20 10h2v4h-2M7 12h3"/><path class="accent" d="M7 12h3"/>',
    "status/battery-caution.svg": '<rect x="3" y="6" width="17" height="12" rx="2"/><path d="M20 10h2v4h-2M11 9v4"/><circle class="accent-fill" cx="11" cy="15.5" r="1"/>',
    "status/battery-charging.svg": '<rect x="3" y="6" width="17" height="12" rx="2"/><path d="M20 10h2v4h-2M13 8l-4 5h3l-1 4 4-6h-3z"/><path class="accent" d="M13 8l-2 3"/>',
    "status/network-wireless-disconnected.svg": '<path d="M3 9a13 13 0 0 1 18 0M6 12a9 9 0 0 1 12 0M9 15a5 5 0 0 1 6 0M4 4l16 16"/><path class="accent" d="M4 4l5 5"/>',
    "status/network-wired-disconnected.svg": '<path d="M4 4h16v10h-6v3h3v3H7v-3h3v-3H4zM5 5l14 14"/><path class="accent" d="M5 5l5 5"/>',
}

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
    "applets/brightness-high.svg": "places/user-desktop.svg",
    "applets/brightness-high-symbolic.svg": "places/user-desktop.svg",
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
    "preferences/preferences-desktop-display.svg": "places/user-desktop.svg",
    "preferences/preferences-desktop-keyboard.svg": "devices/input-keyboard.svg",
    "preferences/preferences-desktop-mouse.svg": "devices/input-mouse.svg",
    "status/audio-volume-low.svg": "status/audio-volume-high.svg",
    "status/audio-volume-medium.svg": "status/audio-volume-high.svg",
    "status/audio-volume-muted.svg": "status/audio-volume-high.svg",
    "status/battery-low.svg": "status/battery-good.svg",
    "status/battery-caution.svg": "status/battery-good.svg",
    "status/battery-charging.svg": "status/battery-good.svg",
    "status/network-wireless-connected-100.svg": "status/network-wireless.svg",
    "status/network-wireless-connected-50.svg": "status/network-wireless.svg",
    "status/network-wireless-disconnected.svg": "status/network-wireless.svg",
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
    """Add a restrained deterministic discriminator to a related base glyph."""
    digest = hashlib.sha256(relative.encode()).digest()
    x = 4 + digest[0] % 13
    y = 18 + digest[1] % 3
    length = 2 + digest[2] % 3
    x2 = 18 + digest[3] % 3
    y2 = 4 + digest[4] % 13
    length2 = 2 + digest[5] % 3
    return body + f'<path class="accent" d="M{x} {y}h{length}M{x2} {y2}v{length2}"/>'


def icon_svg(body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
  <style>
    .accent {{ stroke: {COLORS["accent"]}; }}
    .accent-fill {{ fill: {COLORS["accent"]}; stroke: none; }}
  </style>
  <g fill="none" stroke="{COLORS["textPrimary"]}" stroke-width="{TOKENS["iconography"]["strokeWidth"]}" stroke-linecap="round" stroke-linejoin="round">
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
      .ColorScheme-Background {{ color: {COLORS["surface"]}; }}
      .ColorScheme-ViewBackground {{ color: {COLORS["background"]}; }}
      .ColorScheme-Highlight {{ color: {COLORS["accent"]}; }}
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
    ("hover", "ColorScheme-Hover", 1.0),
    ("hover-inactive", "ColorScheme-Text", 0.1),
    ("pressed", "ColorScheme-Pressed", 1.0),
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
        foreground = COLORS["negative"] if kind == "close" and state in {"hover", "pressed"} else "currentColor"
        groups.append(
            f'''<g id="{state}-center" transform="translate({x} 0)" class="{color_class}" color="{COLORS['textPrimary']}">
      <rect width="24" height="24" rx="{TOKENS['geometry']['compactRadius']}" fill="currentColor" fill-opacity="{opacity:g}"/>
      <g fill="none" stroke="{foreground}" stroke-width="1.7" stroke-linecap="square" stroke-linejoin="miter">{GLYPHS[kind]}</g>
    </g>'''
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="256" height="24" viewBox="0 0 256 24">
  <defs>
    <style id="current-color-scheme" type="text/css"><![CDATA[
      .ColorScheme-Text {{ color: {COLORS["textPrimary"]}; }}
      .ColorScheme-Hover {{ color: {COLORS["surfaceHover"]}; }}
      .ColorScheme-Pressed {{ color: {COLORS["surfaceSelected"]}; }}
    ]]></style>
  </defs>
  {"\n  ".join(groups)}
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


def write_aurorae_svg(name: str, content: str) -> None:
    write(AURORAE / f"{name}.svg", content)
    compressed_path = AURORAE / f"{name}.svgz"
    compressed = canonical_gzip(content.encode("utf-8"))
    if CHECK:
        if not compressed_path.is_file() or compressed_path.read_bytes() != compressed:
            DRIFT.append(compressed_path)
    else:
        compressed_path.write_bytes(compressed)


def main() -> None:
    specs = {**ICON_SPECS, **CORE_ICON_SPECS, **STATE_ICON_SPECS}
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
    optical = {
        relative: body for relative, body in specs.items()
        if relative.startswith(("actions/", "applets/", "status/"))
    }
    for size in (16, 22):
        for relative, body in sorted(optical.items()):
            write(ICONS / f"{size}x{size}" / relative, icon_svg(body))
    categories: dict[str, int] = {}
    for relative in specs:
        category = relative.split("/", 1)[0]
        categories[category] = categories.get(category, 0) + 1
    write(
        ICONS / "coverage.json",
        json.dumps(
            {
                "schemaVersion": 2,
                "iconCount": len(specs),
                "opticalCount": len(optical) * 2,
                "opticalSizes": [16, 22],
                "categories": dict(sorted(categories.items())),
                "icons": sorted(specs),
                "aliases": dict(sorted(effective_aliases.items())),
                "duplicateAllowlist": [sorted(group) for group in DUPLICATE_ALLOWLIST],
            },
            indent=2,
        ) + "\n",
    )
    write_aurorae_svg("decoration", decoration_svg())
    for kind in GLYPHS:
        write_aurorae_svg(kind, button_svg(kind))
    if DRIFT:
        print("Visual asset generator drift: " + ", ".join(str(path.relative_to(ROOT)) for path in DRIFT), file=sys.stderr)
        raise SystemExit(1)
    if CHECK:
        print(f"Verified {len(specs)} scalable icons, {len(optical) * 2} optical variants and 5 Aurorae pairs")
        return
    print(f"Generated {len(specs)} scalable icons, {len(optical) * 2} optical variants and 5 Aurorae pairs")


if __name__ == "__main__":
    main()
