"""Duotone Surface iconography definitions for NoxForge V21 (places, mimetypes, curated apps)."""

from __future__ import annotations


def _folder_plate(
    inner: str,
    *,
    tab_fill_cls: str = "surface-tab",
    body_fill_cls: str = "surface-plate",
    accent_bar_cls: str = "lime",
    accent_color: str | None = None,
) -> str:
    style_attr = f' style="stroke:{accent_color}"' if accent_color else ""
    bar = f'<path class="{accent_bar_cls}"{style_attr} d="M4.5 9.5h7"/>'
    return (
        f'<path class="{tab_fill_cls}" d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v1H3z"/>'
        f'<rect class="{body_fill_cls}" x="3" y="9" width="18" height="10" rx="2"/>'
        f'<path class="surface-bevel" d="M4 9.6h16"/>'
        f'<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
        f"{bar}{inner}"
    )


def _doc_plate(inner: str, *, badge_cls: str = "accent", notch: bool = False) -> str:
    if notch:
        shell = (
            '<path class="surface-plate" d="M7.5 3H18a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V5.5z"/>'
            '<path class="surface-bevel" d="M8 3.6h9.5"/>'
            '<path d="M7.5 3H18a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V5.5z"/>'
            f'<path class="{badge_cls}" d="M5 6L8 3"/>'
        )
    else:
        shell = (
            '<path class="surface-plate" d="M6 3h9l4 4v13a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/>'
            '<path class="surface-tab" d="M15 3l4 4h-4z"/>'
            '<path class="surface-bevel" d="M6.5 3.6H14"/>'
            '<path d="M6 3h9l4 4v13a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zM15 3v4h4"/>'
        )
    return shell + inner


def _app_plate(inner: str, *, rounded: int = 4, notch_cls: str = "lime") -> str:
    return (
        f'<path class="surface-plate" d="M6.5 3H19a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6.5z"/>'
        f'<path class="surface-bevel" d="M7 3.6h11.5"/>'
        f'<path d="M6.5 3H19a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6.5z"/>'
        f'<path class="{notch_cls}" d="M3 6.8L6.8 3"/>'
        f"{inner}"
    )


def build_duotone_places_specs(accents: dict[str, dict[str, str]]) -> dict[str, str]:
    specs: dict[str, str] = {
        "places/folder.svg": _folder_plate('<path class="dimmed" d="M7 14h10"/>'),
        "places/folder-open.svg": (
            '<path class="surface-tab" d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v1H3z"/>'
            '<path class="surface-plate" d="M3 10h18l-2 9a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1L3 10z"/>'
            '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v1M3 10h18l-2 9a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1L3 10z"/>'
            '<path class="lime" d="M5 10h14"/>'
        ),
        "places/folder-documents.svg": _folder_plate('<path d="M8.5 12.5h7M8.5 15.5h4.5"/>', accent_bar_cls="accent"),
        "places/folder-download.svg": _folder_plate('<path d="M12 11v5.5M9.5 14.5l2.5 2.5 2.5-2.5"/>'),
        "places/folder-pictures.svg": _folder_plate('<circle class="accent-fill" cx="8.5" cy="12.5" r="1"/><path d="M7 17l3.2-2.8 2.3 1.8 2.5-3 2 4"/>', accent_bar_cls="accent"),
        "places/folder-music.svg": _folder_plate('<path d="M10 16.5V12l5-1v4.5"/><circle class="accent-fill" cx="8.8" cy="16.5" r="1.2"/><circle class="accent-fill" cx="13.8" cy="15.5" r="1.2"/>', accent_bar_cls="accent"),
        "places/folder-videos.svg": _folder_plate('<path d="M10 11.5l5 2.75-5 2.75z"/>', accent_bar_cls="accent"),
        "places/folder-code.svg": _folder_plate('<path d="M9.5 12L7 14.5 9.5 17M14.5 12l2.5 2.5-2.5 2.5M12.7 11.5l-1.4 6"/>'),
        "places/folder-git.svg": _folder_plate('<circle class="lime-fill" cx="9" cy="12.5" r="1.2"/><circle cx="9" cy="16.5" r="1.2"/><circle cx="15" cy="14.5" r="1.2"/><path d="M9 13.7v1.6M10.2 13l3.6 1"/>'),
        "places/folder-cloud.svg": _folder_plate('<path d="M8.5 16.5h7a2 2 0 0 0 .3-3.95A3 3 0 0 0 10 12.2a2.2 2.2 0 0 0-1.5 4.3z"/>', accent_bar_cls="accent"),
        "places/folder-games.svg": _folder_plate('<path d="M8 14.5h3M9.5 13v3"/><circle class="lime-fill" cx="14.5" cy="13.5" r="0.9"/><circle class="accent-fill" cx="16" cy="15.2" r="0.9"/>'),
        "places/folder-publicshare.svg": _folder_plate('<circle cx="9" cy="14.5" r="1.5"/><circle cx="15" cy="12.5" r="1.4"/><circle cx="15" cy="16.5" r="1.4"/><path d="M10.4 13.8l3.2-1M10.4 15.2l3.2 1"/>', accent_bar_cls="accent"),
        "places/folder-templates.svg": _folder_plate('<rect x="8" y="11.5" width="8" height="5.5" rx="1" stroke-dasharray="2 1.5"/>', accent_bar_cls="accent"),
        "places/folder-locked.svg": _folder_plate('<rect x="9.5" y="13.5" width="5" height="3.8" rx="0.8"/><path d="M10.5 13.5v-1.2a1.5 1.5 0 0 1 3 0v1.2"/>', accent_bar_cls="warning"),
        "places/folder-important.svg": _folder_plate('<path class="warning" d="M12 11.5v3.2"/><circle class="warning-fill" cx="12" cy="16.6" r="0.9"/>', accent_bar_cls="warning"),
        "places/user-home.svg": (
            '<path class="surface-plate" d="M3 10.5L12 3l9 7.5v8.5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
            '<path class="surface-tab" d="M9 21v-6a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v6z"/>'
            '<path d="M3 10.5L12 3l9 7.5v8.5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
            '<path d="M9 21v-6a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v6"/>'
            '<path class="lime" d="M12 3l6.5 5.4"/>'
        ),
        "places/user-desktop.svg": (
            '<rect class="surface-plate" x="3" y="4" width="18" height="12" rx="2"/>'
            '<path class="surface-bevel" d="M4.5 4.8h15"/>'
            '<rect x="3" y="4" width="18" height="12" rx="2"/>'
            '<path d="M8 20h8M12 16v4"/><path class="lime" d="M5 7h5"/>'
        ),
        "places/user-trash.svg": (
            '<path class="surface-plate" d="M6 6l1 14a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-14z"/>'
            '<path d="M4 6h16M10 6V4h4v2M6 6l1 14a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-14M10 10v7M14 10v7"/>'
            '<path class="negative" d="M4 6h4"/>'
        ),
        "places/network-workgroup.svg": (
            '<circle class="surface-plate" cx="12" cy="5.5" r="2.5"/><circle class="surface-plate" cx="5.5" cy="18" r="2.5"/><circle class="surface-plate" cx="18.5" cy="18" r="2.5"/>'
            '<circle cx="12" cy="5.5" r="2.5"/><circle cx="5.5" cy="18" r="2.5"/><circle cx="18.5" cy="18" r="2.5"/>'
            '<path d="M12 8v3.5M12 11.5l-5.5 4.3M12 11.5l5.5 4.3"/><path class="accent" d="M9.5 11.5h5"/>'
        ),
        "places/network-server.svg": _app_plate('<path d="M7 9h10M7 13h10M7 17h6"/><circle class="lime-fill" cx="16.5" cy="17" r="1"/>', notch_cls="accent"),
        "places/network-server-database.svg": (
            '<ellipse class="surface-plate" cx="12" cy="6.5" rx="7" ry="2.5"/>'
            '<path class="surface-tab" d="M5 6.5v11c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5v-11z"/>'
            '<ellipse cx="12" cy="6.5" rx="7" ry="2.5"/>'
            '<path d="M5 6.5v11c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5v-11M5 12c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5"/>'
            '<circle class="lime-fill" cx="15.5" cy="14.5" r="1"/>'
        ),
        "places/start-here-kde.svg": _app_plate('<path class="lime" d="M7.5 16.5V7.5l5 9V7.5"/><path d="M14.5 16.5V7.5h3M14.5 12h2.5"/>'),
    }
    for accent_key in ("lime", "cyan", "violet", "amber", "crimson", "ice"):
        if accent_key in accents:
            hex_val = accents[accent_key]["accent"]
            specs[f"places/folder-{accent_key}.svg"] = _folder_plate(
                f'<circle cx="12" cy="14.2" r="2.1" style="stroke:{hex_val}"/>',
                accent_bar_cls="lime",
                accent_color=hex_val,
            )
    return specs


def build_duotone_mimetype_specs() -> dict[str, str]:
    return {
        "mimetypes/text-x-generic.svg": _doc_plate('<path d="M8.5 11h7M8.5 14.2h7M8.5 17.4h4.5"/><path class="accent" d="M8.5 11h3"/>'),
        "mimetypes/text-plain.svg": _doc_plate('<path d="M8.5 10.5h7M8.5 13.5h5M8.5 16.5h6"/>', notch=True),
        "mimetypes/text-markdown.svg": _doc_plate('<path d="M7.5 16.5v-5l2.2 2.4 2.2-2.4v5"/><path class="lime" d="M15.5 11.5v5M13.8 14.8l1.7 1.7 1.7-1.7"/>', badge_cls="lime", notch=True),
        "mimetypes/text-html.svg": _doc_plate('<path d="M9 12l-2.2 2.5L9 17M15 12l2.2 2.5L15 17"/><path class="accent" d="M13 11l-2 7"/>'),
        "mimetypes/text-x-cmake.svg": _doc_plate('<polygon points="12,9.5 17,17.5 7,17.5"/><path class="lime" d="M12 9.5l2.5 5.5"/>', badge_cls="lime", notch=True),
        "mimetypes/text-x-python.svg": _doc_plate('<path d="M9.5 12.5h4a1.5 1.5 0 0 1 0 3h-3a1.5 1.5 0 0 0 0 3h4"/><circle class="lime-fill" cx="10.2" cy="10.5" r="0.9"/><circle class="accent-fill" cx="13.8" cy="17.5" r="0.9"/>', badge_cls="lime", notch=True),
        "mimetypes/text-x-c++src.svg": _doc_plate('<path d="M10.5 11.5a3 3 0 1 0 0 6"/><path class="accent" d="M13.5 14.5h3M15 13v3"/>', notch=True),
        "mimetypes/text-x-rust.svg": _doc_plate('<circle cx="12" cy="14" r="3.2"/><path class="warning" d="M12 9.5v1.3M12 17.2v1.3M7.5 14h1.3M15.2 14h1.3"/>', badge_cls="warning", notch=True),
        "mimetypes/text-x-script.svg": _doc_plate('<path d="M8 12l2.8 2.3L8 16.6"/><path class="lime" d="M12.2 16.6h4"/>', badge_cls="lime"),
        "mimetypes/application-json.svg": _doc_plate('<path d="M9.5 10.5c-1 0-1.5.7-1.5 1.7v1.1c0 .7-.5 1.2-1 1.2.5 0 1 .5 1 1.2v1.1c0 1 .5 1.7 1.5 1.7M14.5 10.5c1 0 1.5.7 1.5 1.7v1.1c0 .7.5 1.2 1 1.2-.5 0-1 .5-1 1.2v1.1c0 1-.5 1.7-1.5 1.7"/><circle class="accent-fill" cx="12" cy="14.5" r="1"/>', notch=True),
        "mimetypes/application-xml.svg": _doc_plate('<path d="M8.5 12l-2 2.5 2 2.5M15.5 12l2 2.5-2 2.5M10.8 12.2l2.4 4.6M13.2 12.2l-2.4 4.6"/>', notch=True),
        "mimetypes/application-pdf.svg": _doc_plate('<path class="negative" d="M8.5 16.5c2.2-6 4.8-6 7 0"/><path d="M9.2 14h5.6"/>', badge_cls="negative"),
        "mimetypes/application-x-desktop.svg": _doc_plate('<rect x="8" y="10.5" width="8" height="6.5" rx="1"/><path class="accent" d="M8 12.5h8"/>'),
        "mimetypes/application-x-executable.svg": _doc_plate('<rect x="8" y="10.5" width="8" height="6.5" rx="1"/><path class="lime" d="M10.5 12.5l3 1.4-3 1.4z"/>', badge_cls="lime", notch=True),
        "mimetypes/application-x-shellscript.svg": _doc_plate('<path d="M8 11.5l3 2.5-3 2.5"/><path class="lime" d="M12.5 16.5H16M8 8.5h4"/>', badge_cls="lime", notch=True),
        "mimetypes/application-x-archive.svg": (
            '<path class="surface-plate" d="M3.5 7L12 3l8.5 4v10L12 21l-8.5-4z"/>'
            '<path class="surface-tab" d="M3.5 7L12 11l8.5-4L12 3z"/>'
            '<path d="M3.5 7L12 3l8.5 4v10L12 21l-8.5-4zM3.5 7L12 11l8.5-4M12 11v10"/>'
            '<path class="warning" d="M10.5 13.5v4"/>'
        ),
        "mimetypes/application-zip.svg": (
            '<rect class="surface-plate" x="5" y="3" width="14" height="18" rx="2"/>'
            '<rect x="5" y="3" width="14" height="18" rx="2"/>'
            '<path class="accent" d="M12 4v10M10.5 6h3M10.5 9h3M10.5 12h3"/>'
            '<rect x="10" y="14.5" width="4" height="3.5" rx="0.8"/>'
        ),
        "mimetypes/application-x-tar.svg": (
            '<rect class="surface-plate" x="4" y="4" width="16" height="16" rx="2"/>'
            '<rect x="4" y="4" width="16" height="16" rx="2"/>'
            '<path d="M4 10h16M9 10v10M15 10v10"/><path class="lime" d="M8 7h8"/>'
        ),
        "mimetypes/application-x-rpm.svg": _doc_plate('<circle cx="12" cy="14" r="3.5"/><path class="negative" d="M12 14l2.4-1.8"/>', badge_cls="negative", notch=True),
        "mimetypes/application-vnd.flatpak.ref.svg": (
            '<polygon class="surface-plate" points="12,3 19.5,7.5 19.5,16.5 12,21 4.5,16.5 4.5,7.5"/>'
            '<polygon points="12,3 19.5,7.5 19.5,16.5 12,21 4.5,16.5 4.5,7.5"/>'
            '<path d="M12 3v9m0 0l7.5-4.5M12 12L4.5 7.5"/><path class="accent" d="M12 12v9"/>'
        ),
        "mimetypes/package-x-generic.svg": (
            '<path class="surface-plate" d="M3 7l9-4 9 4v10l-9 4-9-4z"/>'
            '<path d="M3 7l9-4 9 4v10l-9 4-9-4zM3 7l9 4 9-4M12 11v10"/><path class="accent" d="M12 3l5 2"/>'
        ),
        "mimetypes/application-octet-stream.svg": _doc_plate('<path d="M8.5 11.5h2v3h-2zM13.5 11.5v3M8.5 16.5v2.2M13.5 16.5h2v2.2h-2z"/>', notch=True),
        "mimetypes/application-vnd.tcpdump.pcap.svg": _doc_plate('<circle cx="9" cy="13" r="1.2"/><circle cx="15" cy="13" r="1.2"/><circle cx="12" cy="17.5" r="1.2"/><path class="accent" d="M9.9 13.9l1.4 2.6M14.1 13.9l-1.4 2.6"/>', notch=True),
        "mimetypes/image-x-generic.svg": (
            '<rect class="surface-plate" x="3" y="4" width="18" height="16" rx="2"/>'
            '<rect x="3" y="4" width="18" height="16" rx="2"/>'
            '<circle class="lime-fill" cx="8" cy="9" r="1.5"/>'
            '<path d="M4.5 17.5l4.5-4.5 3 2.8 3-3.8 4.5 5.5"/>'
        ),
        "mimetypes/audio-x-generic.svg": (
            '<rect class="surface-plate" x="4" y="3" width="16" height="18" rx="2"/>'
            '<rect x="4" y="3" width="16" height="18" rx="2"/>'
            '<path d="M10 15.5V7.5l6-1.5v8"/><circle class="accent-fill" cx="8.5" cy="16" r="1.8"/><circle class="accent-fill" cx="14.5" cy="14.5" r="1.8"/>'
        ),
        "mimetypes/audio-flac.svg": _doc_plate('<path class="accent" d="M8 14v2M10.5 11.5v5M13 10v8M15.5 12.5v3"/>', notch=True),
        "mimetypes/video-x-generic.svg": (
            '<rect class="surface-plate" x="3" y="5" width="18" height="14" rx="2"/>'
            '<rect x="3" y="5" width="18" height="14" rx="2"/>'
            '<path class="accent" d="M10 9.5l5.5 2.5-5.5 2.5z"/><path d="M6 5v14M18 5v14"/>'
        ),
        "mimetypes/x-office-document.svg": _doc_plate('<rect x="8.5" y="10.5" width="7" height="3.2" rx="0.6"/><path d="M8.5 16h7M8.5 18.5h4.5"/>', badge_cls="accent"),
        "mimetypes/unknown.svg": _doc_plate('<path d="M10 11.8a2 2 0 0 1 3.8.8c0 1.4-1.8 1.6-1.8 2.8"/><circle class="accent-fill" cx="12" cy="17.8" r="1"/>', notch=True),
    }


def build_duotone_apps_specs() -> dict[str, str]:
    """Curated ~52 original NoxForge app icons (zero Breeze/third-party copied paths)."""
    return {
        # NoxForge & KDE core
        "apps/io.github.loofiboss.noxforge.controlcenter.svg": _app_plate(
            '<circle cx="12" cy="12" r="4.5"/><path class="lime" d="M12 6.5v2M12 15.5v2M6.5 12h2M15.5 12h2"/><circle class="lime-fill" cx="12" cy="12" r="1.4"/>'
        ),
        "apps/io.github.loofiboss.noxforge.opacity.svg": _app_plate(
            '<rect x="6.5" y="7" width="8" height="8" rx="1.5"/><rect class="accent" x="9.5" y="9.5" width="8" height="8" rx="1.5"/>',
            notch_cls="accent",
        ),
        "apps/systemsettings.svg": _app_plate(
            '<path d="M7 9h10M7 15h10"/><circle class="lime-fill" cx="10" cy="9" r="1.7"/><circle class="accent-fill" cx="14.5" cy="15" r="1.7"/>',
            notch_cls="accent",
        ),
        "apps/org.kde.dolphin.svg": _app_plate(
            '<path d="M6.5 9.5h4l1.5 1.5h5.5v6.5h-11z"/><path class="accent" d="M6.5 12h11"/>',
            notch_cls="accent",
        ),
        "apps/org.kde.konsole.svg": _app_plate(
            '<path d="M7 9.5l3.5 2.7L7 15"/><path class="lime" d="M12 15h5"/>'
        ),
        "apps/org.kde.kate.svg": _app_plate(
            '<path d="M7.5 16.5l7.2-7.2 2.2 2.2-7.2 7.2H7.5z"/><path class="accent" d="M13.5 10.5l2.2 2.2"/>',
            notch_cls="accent",
        ),
        "apps/org.kde.plasmashell.svg": _app_plate(
            '<circle cx="9" cy="9.5" r="1.3"/><circle class="lime-fill" cx="15" cy="9.5" r="1.5"/><circle cx="11" cy="15.5" r="1.5"/><path d="M13 14.5l3 2.5"/>'
        ),
        "apps/org.kde.discover.svg": _app_plate(
            '<path d="M7.5 10h9l-.8 7.5H8.3z"/><path class="accent" d="M10 10V8.5a2 2 0 0 1 4 0V10"/>',
            notch_cls="accent",
        ),
        "apps/org.kde.spectacle.svg": _app_plate(
            '<path d="M7 10V7.5h2.5M14.5 7.5H17V10M7 14v2.5h2.5M14.5 16.5H17V14"/><circle class="lime" cx="12" cy="12" r="2.4"/>'
        ),
        "apps/org.kde.ark.svg": _app_plate(
            '<rect x="7" y="7.5" width="10" height="9.5" rx="1.2"/><path class="warning" d="M12 7.5v7"/><path d="M10 14.5h4"/>',
            notch_cls="warning",
        ),
        "apps/org.kde.okular.svg": _app_plate(
            '<path d="M6.8 8h4.2a1.5 1.5 0 0 1 1 1.4v7.6a1.5 1.5 0 0 0-1-.4H6.8zM17.2 8H13a1.5 1.5 0 0 0-1 1.4V17a1.5 1.5 0 0 1 1-.4h4.2z"/><path class="accent" d="M12 9v7"/>',
            notch_cls="accent",
        ),
        "apps/org.kde.gwenview.svg": _app_plate(
            '<circle class="lime-fill" cx="9" cy="9.5" r="1.2"/><path d="M6.8 16.5l3.7-3.8 2.2 2.2 2.3-3 2.2 4.6"/>'
        ),
        "apps/org.kde.kcalc.svg": _app_plate(
            '<path d="M8.5 8.5v3M7 10h3M14 10h3M7.5 14.5l2.5 2.5M10 14.5l-2.5 2.5"/><path class="lime" d="M14 15h3M14 17h3"/>'
        ),
        "apps/org.kde.plasma-systemmonitor.svg": _app_plate(
            '<path class="lime" d="M6.5 13.5h2.5l1.6-4.5 2.2 6.8 1.7-3.8h3"/>'
        ),
        "apps/org.kde.elisa.svg": _app_plate(
            '<path d="M9.5 15.5v-6l5.5-1.2v6"/><circle class="accent-fill" cx="8.5" cy="15.8" r="1.4"/><circle class="accent-fill" cx="14" cy="14.5" r="1.4"/>',
            notch_cls="accent",
        ),
        "apps/org.kde.kwalletmanager5.svg": _app_plate(
            '<rect x="7" y="8.5" width="10" height="7.5" rx="1.2"/><path class="warning" d="M13 12.2h4"/>',
            notch_cls="warning",
        ),
        # Browsers & Communication
        "apps/firefox.svg": _app_plate(
            '<circle cx="12" cy="12" r="5"/><path class="warning" d="M8.5 9a5 5 0 0 1 7.5 1.5c1 2.2-.5 4.8-3 5.2"/>',
            notch_cls="warning",
        ),
        "apps/zen-browser.svg": _app_plate(
            '<circle cx="12" cy="12" r="5.2"/><circle class="accent" cx="12" cy="12" r="2.8"/><circle class="lime-fill" cx="12" cy="12" r="1"/>',
            notch_cls="accent",
        ),
        "apps/brave-browser.svg": _app_plate(
            '<path d="M12 6.8l5 2.2-.9 5.5-4.1 2.8-4.1-2.8-.9-5.5z"/><path class="warning" d="M9.5 11.5l2.5 2 2.5-2"/>',
            notch_cls="warning",
        ),
        "apps/chromium-browser.svg": _app_plate(
            '<circle cx="12" cy="12" r="5.2"/><circle class="accent" cx="12" cy="12" r="2.1"/><path d="M12 6.8h4.5M7.5 14.5L9.8 11M14.2 13l-2.2 4.2"/>',
            notch_cls="accent",
        ),
        "apps/thunderbird.svg": _app_plate(
            '<rect x="6.8" y="8.5" width="10.4" height="7" rx="1"/><path class="accent" d="M7.2 9l4.8 3.6L16.8 9"/>',
            notch_cls="accent",
        ),
        "apps/discord.svg": _app_plate(
            '<path d="M7.5 9.5c2.5-1 6.5-1 9 0l1 5.5c-1.5 1-3.5 1.5-5.5 1.5s-4-.5-5.5-1.5z"/><circle class="accent-fill" cx="10" cy="12.5" r="1"/><circle class="accent-fill" cx="14" cy="12.5" r="1"/>',
            notch_cls="accent",
        ),
        "apps/dev.vencord.Vesktop.svg": _app_plate(
            '<path d="M8 8.5l4 7.5 4-7.5"/><path class="lime" d="M10.5 8.5L12 11.5l1.5-3"/>'
        ),
        "apps/org.telegram.desktop.svg": _app_plate(
            '<path d="M6.8 12.2l10.2-4-2.2 8.8-3.2-2.4-2 1.8.4-3z"/><path class="accent" d="M10 13.2l7-5"/>',
            notch_cls="accent",
        ),
        "apps/org.signal.Signal.svg": _app_plate(
            '<path d="M7.5 10a4.8 4.8 0 1 1 2 5.2L7 16.5z" stroke-dasharray="2.5 1.5"/><circle class="accent-fill" cx="12" cy="12" r="1.4"/>',
            notch_cls="accent",
        ),
        # Editors, Terminals & DevTools
        "apps/code.svg": _app_plate(
            '<path d="M15.5 7.2v9.6l-8-4.8z"/><path class="accent" d="M8 9.2l7.5 5.8M8 14.8l7.5-5.8"/>',
            notch_cls="accent",
        ),
        "apps/dev.zed.Zed.svg": _app_plate(
            '<path d="M7.5 8h9l-9 8h9"/><path class="lime" d="M11.5 8h5l-2 2"/>'
        ),
        "apps/nvim.svg": _app_plate(
            '<path class="lime" d="M8 16.5V7.5l8 9V7.5"/><path class="accent" d="M8 7.5l3 3.4M13 13.1l3 3.4"/>'
        ),
        "apps/com.mitchellh.ghostty.svg": _app_plate(
            '<path d="M8 17V11a4 4 0 0 1 8 0v6l-2-1.2-2 1.2-2-1.2z"/><circle class="accent-fill" cx="10.5" cy="11.5" r="0.9"/><circle class="accent-fill" cx="13.5" cy="11.5" r="0.9"/>',
            notch_cls="accent",
        ),
        "apps/kitty.svg": _app_plate(
            '<path d="M7.5 16.5V9l2.5 2h4l2.5-2v7.5"/><circle class="lime-fill" cx="10.2" cy="13" r="0.9"/><circle class="lime-fill" cx="13.8" cy="13" r="0.9"/>'
        ),
        "apps/Alacritty.svg": _app_plate(
            '<path d="M12 7l4.5 10h-2l-2.5-5.6L9.5 17h-2z"/><path class="warning" d="M11 14.5l1 2.5 1-2.5"/>',
            notch_cls="warning",
        ),
        "apps/yazi.svg": _app_plate(
            '<path d="M7.5 8.5l4.5 4.2 4.5-4.2M12 12.7v4.5"/><path class="lime" d="M8.5 17.2h7"/>'
        ),
        "apps/docker.svg": _app_plate(
            '<path d="M7.5 11.5h2v2h-2zM10.5 11.5h2v2h-2zM10.5 8.8h2v2h-2zM13.5 11.5h2v2h-2z"/><path class="accent" d="M6.5 14.5h11c-.5 2.2-2.4 3.2-5.5 3.2s-5-1-5.5-3.2z"/>',
            notch_cls="accent",
        ),
        "apps/podman.svg": _app_plate(
            '<circle cx="12" cy="12" r="4.8"/><circle class="accent" cx="10.2" cy="11" r="1"/><circle class="accent" cx="13.8" cy="11" r="1"/><path d="M10.5 14.2h3"/>',
            notch_cls="accent",
        ),
        "apps/virt-manager.svg": _app_plate(
            '<path d="M7 9l2.5 6L12 9l2.5 6L17 9"/><path class="lime" d="M7 16.5h10"/>'
        ),
        # Gaming
        "apps/steam.svg": _app_plate(
            '<circle cx="14.5" cy="9.5" r="2.3"/><circle cx="9.2" cy="14.5" r="1.8"/><path class="accent" d="M13 11l-2.5 2.5M7 13l1.5 1.2"/>',
            notch_cls="accent",
        ),
        "apps/net.lutris.Lutris.svg": _app_plate(
            '<path d="M12 7l5 2.8v4.4L12 17l-5-2.8V9.8z"/><path class="warning" d="M12 7v10M7 9.8l5 2.8 5-2.8"/>',
            notch_cls="warning",
        ),
        "apps/com.heroicgameslauncher.hgl.svg": _app_plate(
            '<path d="M12 7l4.5 2.5V14L12 17l-4.5-3V9.5z"/><path class="lime" d="M10 10v4.2M14 10v4.2M10 12.1h4"/>'
        ),
        # Media & Creative
        "apps/com.obsproject.Studio.svg": _app_plate(
            '<circle cx="12" cy="12" r="5"/><path class="accent" d="M12 8.2a2.5 2.5 0 0 1 2 4.2M15.3 13.8a2.5 2.5 0 0 1-4.6.5M9.5 13.5a2.5 2.5 0 0 1 2.2-4.3"/>',
            notch_cls="accent",
        ),
        "apps/vlc.svg": _app_plate(
            '<path d="M10.5 7.5h3l2.5 9h-8z"/><path class="warning" d="M9.5 11.5h5M8.8 14h6.4"/>',
            notch_cls="warning",
        ),
        "apps/mpv.svg": _app_plate(
            '<circle cx="12" cy="12" r="5"/><path class="lime" d="M10.5 9.5l4.5 2.5-4.5 2.5z"/>'
        ),
        "apps/gimp.svg": _app_plate(
            '<path d="M7.5 13.5c0-3 2.5-5 5-5s4.5 1.8 4.5 4.2c0 2.5-2.2 4.3-5 4.3s-4.5-1.4-4.5-3.5z"/><circle class="accent-fill" cx="10.5" cy="11.5" r="1"/><path class="warning" d="M14.5 14.5l2.5 2"/>',
            notch_cls="accent",
        ),
        "apps/org.kde.krita.svg": _app_plate(
            '<circle cx="12" cy="12" r="4.8"/><path class="accent" d="M8.5 15.5l6.5-6.5M14.5 9.5l1.2 1.2"/>',
            notch_cls="accent",
        ),
        "apps/org.inkscape.Inkscape.svg": _app_plate(
            '<path d="M12 7l5 5.2-5 4.8-5-4.8z"/><path class="lime" d="M12 7l2.2 3.2-2.2 1.2-2.2-1.2z"/>'
        ),
        "apps/blender.svg": _app_plate(
            '<circle cx="12.5" cy="13" r="3.5"/><path class="warning" d="M7.5 10.5h5M10 8.5l2.5 2M7.5 14.5l2-1.5"/>',
            notch_cls="warning",
        ),
        "apps/org.kde.kdenlive.svg": _app_plate(
            '<path class="negative" d="M12 7.5v9"/><path d="M7.5 10.5v3M14.5 9.5l3 2.5-3 2.5z"/>',
            notch_cls="negative",
        ),
        "apps/spotify.svg": _app_plate(
            '<circle cx="12" cy="12" r="5.2"/><path class="lime" d="M9.2 10.5c2-.5 4-.3 5.6.5M9.6 12.6c1.6-.4 3.3-.2 4.6.4M10.1 14.5c1.2-.3 2.4-.1 3.4.3"/>'
        ),
        # Office & Security
        "apps/libreoffice-main.svg": _app_plate(
            '<path d="M8 7.5h4.8l3.2 3.2v5.8H8z"/><path class="accent" d="M13.5 7.5H16V10z"/>',
            notch_cls="accent",
        ),
        "apps/libreoffice-writer.svg": _app_plate(
            '<path d="M8 8h8M8 11h8M8 14h5"/><path class="accent" d="M8 16.5h8"/>',
            notch_cls="accent",
        ),
        "apps/libreoffice-calc.svg": _app_plate(
            '<rect x="7.5" y="8" width="9" height="8" rx="1"/><path class="lime" d="M7.5 11.5h9M11.5 8v8"/>'
        ),
        "apps/libreoffice-impress.svg": _app_plate(
            '<rect x="7.5" y="8.5" width="9" height="6.5" rx="1"/><path class="warning" d="M10 15l-1.5 2M14 15l1.5 2M10 11.5h4"/>',
            notch_cls="warning",
        ),
        "apps/com.bitwarden.desktop.svg": _app_plate(
            '<path d="M8 8h8v4.5c0 2.5-1.8 4-4 4.8-2.2-.8-4-2.3-4-4.8z"/><path class="accent" d="M12 8.2v8.8"/>',
            notch_cls="accent",
        ),
        "apps/org.keepassxc.KeePassXC.svg": _app_plate(
            '<circle cx="10.2" cy="11.5" r="2.5"/><path class="lime" d="M12.5 11.5h4.5v2M15 11.5v1.5"/>'
        ),
    }


# Keep monoline 16x16 / 22x22 clean symbolic variants for places/
MONOLINE_PLACES_OVERRIDE = {
    "places/folder.svg": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path class="accent" d="M3 9.5h18"/>',
    "places/folder-open.svg": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v1"/><path d="M3 10h18l-2 9a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1L3 10z"/><path class="accent" d="M5 10h14"/>',
    "places/folder-documents.svg": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M8 12h8M8 15h5"/><path class="accent" d="M8 12h5"/>',
    "places/folder-download.svg": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M12 10v6M9 13.5l3 3 3-3"/><path class="accent" d="M9 13.5l3 3"/>',
    "places/folder-pictures.svg": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><circle cx="9" cy="12" r="1.5"/><path d="M6 17l4-3 3 2 3-4 3 5"/><path class="accent" d="M16 12l3 5"/>',
    "places/folder-videos.svg": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 11l6 3-6 3z"/><path class="accent" d="M9 11v3"/>',
    "places/user-home.svg": '<path d="M3 10.5L12 3l9 7.5v8.5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 21v-6a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v6"/><path class="accent" d="M12 3l7 6"/>',
    "places/user-desktop.svg": '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/><path class="accent" d="M4 5h5"/>',
    "places/user-trash.svg": '<path d="M4 6h16M10 6V4h4v2M6 6l1 14a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-14M10 10v7M14 10v7"/><path class="accent" d="M5 6h4"/>',
    "places/network-workgroup.svg": '<circle cx="12" cy="5" r="2.5"/><circle cx="5" cy="18" r="2.5"/><circle cx="19" cy="18" r="2.5"/><path d="M12 7.5v4M12 11.5L6 15.5M12 11.5l6 4"/><path class="accent" d="M9 12h6"/>',
}
