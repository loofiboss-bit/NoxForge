#!/usr/bin/env python3
"""Render professional, captivating marketing and gallery screenshots for NoxForge on KDE Store / OpenDesktop.

Showcases NoxForge v14.0.0 features:
- Dual-Palette Parity (Quiet Graphite #0D1419 & True Obsidian OLED #000000)
- Forge Accent Matrix (Electric Lime, Forge Cyan, Cyber Violet, Molten Amber)
- Architectural Window Craft (18px Chamfered Forge Notch Aurorae & KWin Switcher)
- Unified Control Suite (3-Tab PySide6 Control Center & Depth/Opacity Configurator)
- Native Plasma 6 / Wayland Shell & Kickoff Launcher & Lock Screen
- 100% Original Scalable Vector Iconography & Ecosystem Integrations
"""

from __future__ import annotations

import math
import os
import shutil
import sys
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PIL import Image, ImageFilter
from PyQt6.QtCore import QPointF, QRect, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontDatabase,
    QGuiApplication,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PyQt6.QtSvg import QSvgRenderer

app = QGuiApplication([])

ROOT = Path(__file__).resolve().parents[1]
MEDIA_STORE = ROOT / "media/store"
WALLPAPERS = ROOT / "wallpapers/NoxForge/contents/images"
WALLPAPERS_OBSIDIAN = ROOT / "wallpapers/NoxForge-Obsidian/contents/images"
BRAND = ROOT / "design/brand"
ICONS = ROOT / "icons/NoxForge/scalable"
AURORAE = ROOT / "aurorae/io.github.loofiboss.noxforge.desktop"

# -------------------------------------------------------------------------
# Design Tokens & Color Palettes
# -------------------------------------------------------------------------

BG_GRAPHITE = QColor("#0D1419")
SURFACE_GRAPHITE = QColor("#141E25")
SURFACE_RAISED = QColor("#1B2831")
SURFACE_SUNKEN = QColor("#10191F")
SURFACE_HOVER = QColor("#283942")
SURFACE_SELECTED = QColor("#223429")
BORDER_DEFAULT = QColor("#2F414B")
BORDER_STRONG = QColor("#455A64")

BG_OBSIDIAN = QColor("#000000")
SURFACE_OBSIDIAN = QColor("#0A0F13")
SURFACE_OBSIDIAN_RAISED = QColor("#121B21")
BORDER_OBSIDIAN = QColor("#283942")

# Forge Accent Matrix
ACCENT_LIME = QColor("#A3FF47")
ACCENT_LIME_MUTED = QColor("#71994F")
ACCENT_LIME_SOFT = QColor("#243528")
ACCENT_LIME_PRESSED = QColor("#82D936")
ACCENT_INK = QColor("#0D1419")

ACCENT_CYAN = QColor("#22D3EE")
ACCENT_VIOLET = QColor("#A78BFA")
ACCENT_AMBER = QColor("#FBBF24")
ALERT_RED = QColor("#FF6B7A")

TEXT_PRIMARY = QColor("#E8F0F2")
TEXT_SECONDARY = QColor("#A6B4B9")
TEXT_DISABLED = QColor("#6F7C82")


def get_font(family: str, size: int, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
    f = QFont(family, size)
    f.setWeight(weight)
    f.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    return f


def notched_path(rect: QRectF, radius: float = 8.0, notch: float = 18.0) -> QPainterPath:
    path = QPainterPath()
    if notch <= 0.0:
        path.addRoundedRect(rect, radius, radius)
        return path
    path.moveTo(rect.left() + notch, rect.top())
    path.lineTo(rect.right() - radius, rect.top())
    path.quadTo(rect.right(), rect.top(), rect.right(), rect.top() + radius)
    path.lineTo(rect.right(), rect.bottom() - radius)
    path.quadTo(rect.right(), rect.bottom(), rect.right() - radius, rect.bottom())
    path.lineTo(rect.left() + radius, rect.bottom())
    path.quadTo(rect.left(), rect.bottom(), rect.left(), rect.bottom() - radius)
    path.lineTo(rect.left(), rect.top() + notch)
    path.closeSubpath()
    return path


def draw_window_frame(
    p: QPainter,
    rect: QRectF,
    title: str,
    *,
    is_active: bool = True,
    is_obsidian: bool = False,
    notch: float = 18.0,
    radius: float = 8.0,
    titlebar_height: float = 38.0,
    accent: QColor = ACCENT_LIME,
) -> QRectF:
    bg = SURFACE_OBSIDIAN if is_obsidian else SURFACE_GRAPHITE
    border = BORDER_STRONG if is_active else BORDER_DEFAULT

    path = notched_path(rect, radius=radius, notch=notch)

    p.save()
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.fillPath(path, bg)

    p.setClipPath(path)
    tb_rect = QRectF(rect.left(), rect.top(), rect.width(), titlebar_height)
    tb_bg = SURFACE_OBSIDIAN_RAISED if is_obsidian else SURFACE_RAISED
    p.fillRect(tb_rect, tb_bg)

    # Titlebar bottom divider
    p.setPen(QPen(border, 1.0))
    p.drawLine(QPointF(rect.left(), rect.top() + titlebar_height), QPointF(rect.right(), rect.top() + titlebar_height))

    # Inner bevel highlight for crisp depth
    if is_active:
        p.setPen(QPen(QColor(255, 255, 255, 16), 1.0))
        p.drawLine(QPointF(rect.left() + notch + 2, rect.top() + 1), QPointF(rect.right() - radius, rect.top() + 1))

    # Window title
    p.setFont(get_font("Inter", 11, QFont.Weight.DemiBold if is_active else QFont.Weight.Normal))
    p.setPen(TEXT_PRIMARY if is_active else TEXT_SECONDARY)
    title_rect = QRectF(rect.left() + notch + 14, rect.top(), rect.width() - notch - 140, titlebar_height)
    p.drawText(title_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, title)

    # Window Controls (Aurorae Vector Buttons)
    btn_y = rect.top() + (titlebar_height - 18) / 2
    right = rect.right() - 14

    # Close button (subtle alert red hover effect)
    close_rect = QRectF(right - 20, btn_y, 18, 18)
    p.setPen(QPen(ALERT_RED if is_active else TEXT_DISABLED, 1.8))
    p.drawLine(QPointF(close_rect.left() + 4, close_rect.top() + 4), QPointF(close_rect.right() - 4, close_rect.bottom() - 4))
    p.drawLine(QPointF(close_rect.left() + 4, close_rect.bottom() - 4), QPointF(close_rect.right() - 4, close_rect.top() + 4))

    # Maximize button (cyan precision)
    max_rect = QRectF(right - 44, btn_y, 18, 18)
    p.setPen(QPen(ACCENT_CYAN if is_active else TEXT_DISABLED, 1.6))
    p.drawRoundedRect(QRectF(max_rect.left() + 4, max_rect.top() + 4, 10, 10), 1.5, 1.5)

    # Minimize button (lime accent)
    min_rect = QRectF(right - 68, btn_y, 18, 18)
    p.setPen(QPen(accent if is_active else TEXT_DISABLED, 1.6))
    p.drawLine(QPointF(min_rect.left() + 4, min_rect.top() + 9), QPointF(min_rect.right() - 4, min_rect.top() + 9))

    p.setClipping(False)
    p.setPen(QPen(border, 1.2))
    p.drawPath(path)

    # Signature Forge Notch Chamfer Highlight
    if is_active:
        notch_path = QPainterPath()
        notch_path.moveTo(rect.left(), rect.top() + notch)
        notch_path.lineTo(rect.left() + notch, rect.top())
        p.setPen(QPen(accent, 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawPath(notch_path)

    p.restore()
    return QRectF(rect.left() + 1, rect.top() + titlebar_height + 1, rect.width() - 2, rect.height() - titlebar_height - 2)


def render_svg(p: QPainter, svg_path: Path, rect: QRectF) -> None:
    if svg_path.is_file():
        renderer = QSvgRenderer(str(svg_path))
        renderer.render(p, rect)


def qimage_to_pil(qimg: QImage) -> Image.Image:
    qimg = qimg.convertToFormat(QImage.Format.Format_RGBA8888)
    width, height = qimg.width(), qimg.height()
    ptr = qimg.bits()
    ptr.setsize(height * width * 4)
    return Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)


def pil_to_qimage(pil_img: Image.Image) -> QImage:
    data = pil_img.convert("RGBA").tobytes("raw", "RGBA")
    qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
    return qimg.copy()


def add_drop_shadow(
    base: Image.Image,
    element: Image.Image,
    pos: tuple[int, int],
    radius: int = 36,
    offset: tuple[int, int] = (0, 18),
    opacity: float = 0.60,
) -> None:
    """Composite element with realistic multi-layer depth shadow (contact + ambient diffuse)."""
    alpha = element.split()[-1]

    # 1. Broad ambient shadow
    ambient_mask = alpha.point(lambda p: int(p * opacity * 0.55))
    ambient_shadow = Image.new("RGBA", element.size, (4, 7, 10, 255))
    amb_pad = int(radius * 1.5)
    amb_canvas = Image.new("RGBA", (element.width + amb_pad * 2, element.height + amb_pad * 2), (0, 0, 0, 0))
    amb_canvas.paste(ambient_shadow, (amb_pad, amb_pad), mask=ambient_mask)
    amb_blurred = amb_canvas.filter(ImageFilter.GaussianBlur(radius))

    # 2. Tight contact shadow for elevated definition
    contact_mask = alpha.point(lambda p: int(p * opacity * 0.75))
    contact_shadow = Image.new("RGBA", element.size, (2, 3, 5, 255))
    con_pad = int(radius * 0.6)
    con_canvas = Image.new("RGBA", (element.width + con_pad * 2, element.height + con_pad * 2), (0, 0, 0, 0))
    con_canvas.paste(contact_shadow, (con_pad, con_pad), mask=contact_mask)
    con_blurred = con_canvas.filter(ImageFilter.GaussianBlur(max(4, int(radius * 0.3))))

    base.alpha_composite(amb_blurred, (pos[0] + offset[0] - amb_pad, pos[1] + offset[1] - amb_pad))
    base.alpha_composite(con_blurred, (pos[0] + offset[0] // 2 - con_pad, pos[1] + offset[1] // 2 - con_pad))
    base.alpha_composite(element, pos)


# -------------------------------------------------------------------------
# Window Content Renderers
# -------------------------------------------------------------------------

def create_dolphin_window(
    width: int = 1160,
    height: int = 740,
    is_active: bool = False,
    is_obsidian: bool = False,
    accent: QColor = ACCENT_LIME,
    custom_title: str = "Projects — Dolphin",
) -> Image.Image:
    """Authentic KDE 6 Dolphin file manager window with NoxForge styling."""
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    content = draw_window_frame(
        p,
        QRectF(0, 0, width, height),
        custom_title,
        is_active=is_active,
        is_obsidian=is_obsidian,
        accent=accent,
    )

    tb_h = 42
    tb_rect = QRectF(content.left(), content.top(), content.width(), tb_h)
    p.fillRect(tb_rect, SURFACE_OBSIDIAN_RAISED if is_obsidian else SURFACE_RAISED)
    p.setPen(QPen(BORDER_OBSIDIAN if is_obsidian else BORDER_DEFAULT, 1.0))
    p.drawLine(QPointF(tb_rect.left(), tb_rect.bottom()), QPointF(tb_rect.right(), tb_rect.bottom()))

    # Back / Forward buttons
    p.setFont(get_font("Inter", 13, QFont.Weight.Bold))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(content.left() + 16, content.top(), 20, tb_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter, "‹")
    p.drawText(QRectF(content.left() + 40, content.top(), 20, tb_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter, "›")

    # Path Breadcrumb pills
    p.setFont(get_font("Inter", 10, QFont.Weight.Medium))
    path_x = content.left() + 80
    for segment in ["Home", "Projects", "NoxForge"]:
        seg_rect = QRectF(path_x, content.top() + 7, 76, 28)
        p.setPen(BORDER_OBSIDIAN if is_obsidian else BORDER_DEFAULT)
        p.setBrush(SURFACE_OBSIDIAN if is_obsidian else SURFACE_GRAPHITE)
        p.drawRoundedRect(seg_rect, 4, 4)
        p.setPen(accent if segment == "NoxForge" else TEXT_SECONDARY)
        p.drawText(seg_rect, Qt.AlignmentFlag.AlignCenter, segment)
        path_x += 84
        p.setPen(TEXT_DISABLED)
        p.drawText(QRectF(path_x - 7, content.top() + 7, 10, 28), Qt.AlignmentFlag.AlignCenter, "›")

    # Search bar on right
    search_rect = QRectF(content.right() - 230, content.top() + 7, 210, 28)
    p.setPen(BORDER_OBSIDIAN if is_obsidian else BORDER_DEFAULT)
    p.setBrush(BG_OBSIDIAN if is_obsidian else SURFACE_SUNKEN)
    p.drawRoundedRect(search_rect, 5, 5)
    render_svg(p, ICONS / "actions/system-search.svg", QRectF(search_rect.left() + 8, search_rect.top() + 6, 16, 16))
    p.setFont(get_font("Inter", 9, QFont.Weight.Normal))
    p.setPen(TEXT_DISABLED)
    p.drawText(QRectF(search_rect.left() + 30, search_rect.top(), 170, 28), Qt.AlignmentFlag.AlignVCenter, "Search NoxForge...")

    # Left Sidebar (Places)
    side_w = 210
    side_rect = QRectF(content.left(), content.top() + tb_h, side_w, content.height() - tb_h - 32)
    p.fillRect(side_rect, BG_OBSIDIAN if is_obsidian else SURFACE_SUNKEN)
    p.setPen(QPen(BORDER_OBSIDIAN if is_obsidian else BORDER_DEFAULT, 1.0))
    p.drawLine(QPointF(side_rect.right(), side_rect.top()), QPointF(side_rect.right(), side_rect.bottom()))

    places = [
        ("Home", "places/user-home.svg", False),
        ("Documents", "places/folder-documents.svg", False),
        ("Downloads", "places/folder-download.svg", False),
        ("Pictures", "places/folder-pictures.svg", False),
        ("Projects", "places/folder.svg", True),
        ("Trash", "places/user-trash.svg", False),
    ]

    p.setFont(get_font("Inter", 9, QFont.Weight.DemiBold))
    p.setPen(TEXT_DISABLED)
    p.drawText(QRectF(side_rect.left() + 16, side_rect.top() + 14, 180, 20), Qt.AlignmentFlag.AlignVCenter, "PLACES")

    item_y = side_rect.top() + 40
    for name, icon, is_selected in places:
        item_rect = QRectF(side_rect.left() + 8, item_y, side_w - 16, 32)
        if is_selected:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(SURFACE_SELECTED)
            p.drawRoundedRect(item_rect, 6, 6)
            p.setBrush(accent)
            p.drawRoundedRect(QRectF(item_rect.left(), item_rect.top() + 6, 3, 20), 1.5, 1.5)

        render_svg(p, ICONS / icon, QRectF(item_rect.left() + 12, item_rect.top() + 6, 20, 20))
        p.setFont(get_font("Inter", 10, QFont.Weight.Medium if is_selected else QFont.Weight.Normal))
        p.setPen(accent if is_selected else TEXT_PRIMARY)
        p.drawText(QRectF(item_rect.left() + 40, item_rect.top(), 140, 32), Qt.AlignmentFlag.AlignVCenter, name)
        item_y += 36

    # Devices header in sidebar
    p.setFont(get_font("Inter", 9, QFont.Weight.DemiBold))
    p.setPen(TEXT_DISABLED)
    p.drawText(QRectF(side_rect.left() + 16, item_y + 8, 180, 20), Qt.AlignmentFlag.AlignVCenter, "DEVICES")
    item_y += 32

    devices = [
        ("Fedora NVMe", "devices/drive-harddisk.svg"),
        ("Workstation", "devices/computer.svg"),
    ]
    for dname, dicon in devices:
        drect = QRectF(side_rect.left() + 8, item_y, side_w - 16, 32)
        render_svg(p, ICONS / dicon, QRectF(drect.left() + 12, drect.top() + 6, 20, 20))
        p.setFont(get_font("Inter", 10, QFont.Weight.Normal))
        p.setPen(TEXT_SECONDARY)
        p.drawText(QRectF(drect.left() + 40, drect.top(), 140, 32), Qt.AlignmentFlag.AlignVCenter, dname)
        item_y += 34

    # Main Grid Area (File Browser)
    main_rect = QRectF(side_rect.right() + 1, content.top() + tb_h, content.width() - side_w - 1, content.height() - tb_h - 32)
    p.fillRect(main_rect, BG_OBSIDIAN if is_obsidian else SURFACE_GRAPHITE)

    folders_and_files = [
        ("apps", "places/folder.svg", True, "App Integrations"),
        ("aurorae", "places/folder.svg", True, "Forge Notch 18px"),
        ("color-schemes", "places/folder.svg", True, "Graphite & Obsidian"),
        ("design", "places/folder.svg", True, "Tokens & Branding"),
        ("icons", "places/folder.svg", True, "Original Vector Icon Theme"),
        ("plasma", "places/folder.svg", True, "Plasma 6 Desktop Theme"),
        ("tools", "places/folder.svg", True, "Control Center & Opacity"),
        ("wallpapers", "places/folder.svg", True, "Geometric Visuals"),
        ("CMakeLists.txt", "mimetypes/text-x-generic.svg", False, "CMake Build Engine"),
        ("README.md", "mimetypes/text-markdown.svg", False, "v14.0.0 Specification"),
        ("VERSION", "mimetypes/text-plain.svg", False, "Release: 14.0.0"),
        ("LICENSE", "mimetypes/text-plain.svg", False, "MIT License"),
    ]

    grid_cols = 4
    col_w = (main_rect.width() - 40) / grid_cols
    row_h = 96
    gx = main_rect.left() + 20
    gy = main_rect.top() + 20

    for i, (fname, ficon, is_dir, fdesc) in enumerate(folders_and_files):
        c = i % grid_cols
        r = i // grid_cols
        bx = gx + c * col_w
        by = gy + r * row_h
        card_rect = QRectF(bx + 4, by + 4, col_w - 8, row_h - 8)

        p.setPen(BORDER_OBSIDIAN if is_obsidian else BORDER_DEFAULT)
        p.setBrush(SURFACE_OBSIDIAN_RAISED if is_obsidian else SURFACE_RAISED)
        p.drawRoundedRect(card_rect, 6, 6)

        render_svg(p, ICONS / ficon, QRectF(card_rect.left() + 12, card_rect.top() + (row_h - 8 - 36) / 2, 36, 36))

        p.setFont(get_font("Inter", 10, QFont.Weight.Medium))
        p.setPen(TEXT_PRIMARY)
        p.drawText(QRectF(card_rect.left() + 56, card_rect.top() + 16, card_rect.width() - 60, 20), Qt.AlignmentFlag.AlignVCenter, fname)

        p.setFont(get_font("Inter", 8, QFont.Weight.Normal))
        p.setPen(accent if is_dir else ACCENT_CYAN)
        p.drawText(QRectF(card_rect.left() + 56, card_rect.top() + 36, card_rect.width() - 60, 16), Qt.AlignmentFlag.AlignVCenter, fdesc)

    # Status Bar
    stat_rect = QRectF(content.left(), content.bottom() - 32, content.width(), 32)
    p.fillRect(stat_rect, BG_OBSIDIAN if is_obsidian else SURFACE_SUNKEN)
    p.setPen(QPen(BORDER_OBSIDIAN if is_obsidian else BORDER_DEFAULT, 1.0))
    p.drawLine(QPointF(stat_rect.left(), stat_rect.top()), QPointF(stat_rect.right(), stat_rect.top()))
    p.setFont(get_font("Inter", 9, QFont.Weight.Normal))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(stat_rect.left() + 16, stat_rect.top(), 360, 32), Qt.AlignmentFlag.AlignVCenter, "12 items • 182.4 GiB free space")

    slider_rect = QRectF(stat_rect.right() - 140, stat_rect.top() + 14, 100, 4)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(BORDER_STRONG)
    p.drawRoundedRect(slider_rect, 2, 2)
    p.setBrush(accent)
    p.drawRoundedRect(QRectF(slider_rect.left(), slider_rect.top(), 40, 4), 2, 2)
    p.setBrush(TEXT_PRIMARY)
    p.drawEllipse(QPointF(slider_rect.left() + 40, slider_rect.center().y()), 5, 5)

    p.end()
    return qimage_to_pil(img)


def create_konsole_window(
    width: int = 1200,
    height: int = 780,
    is_active: bool = True,
    is_obsidian: bool = True,
    accent: QColor = ACCENT_LIME,
    custom_title: str = "loofi@fedora: ~/Projects/NoxForge — Konsole",
) -> Image.Image:
    """Konsole terminal window displaying authentic v14.0.0 fastfetch & noxforge-ctl output."""
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    content = draw_window_frame(
        p,
        QRectF(0, 0, width, height),
        custom_title,
        is_active=is_active,
        is_obsidian=is_obsidian,
        accent=accent,
    )

    p.fillRect(content, BG_OBSIDIAN if is_obsidian else BG_GRAPHITE)

    is_compact = (width < 800)

    # Tab Bar
    tab_h = 32
    tab_bar = QRectF(content.left(), content.top(), content.width(), tab_h)
    p.fillRect(tab_bar, SURFACE_OBSIDIAN_RAISED if is_obsidian else SURFACE_RAISED)
    p.setPen(QPen(BORDER_OBSIDIAN if is_obsidian else BORDER_DEFAULT, 1.0))
    p.drawLine(QPointF(tab_bar.left(), tab_bar.bottom()), QPointF(tab_bar.right(), tab_bar.bottom()))

    t1_w = 210 if is_compact else 240
    tab1 = QRectF(tab_bar.left() + 10, tab_bar.top() + 3, t1_w, 29)
    p.fillRect(tab1, BG_OBSIDIAN if is_obsidian else BG_GRAPHITE)
    p.setPen(QPen(BORDER_OBSIDIAN if is_obsidian else BORDER_DEFAULT, 1.0))
    p.drawRect(tab1)
    p.setPen(QPen(accent, 2.0))
    p.drawLine(QPointF(tab1.left(), tab1.top() + 1), QPointF(tab1.right(), tab1.top() + 1))

    render_svg(p, ICONS / "actions/utilities-terminal.svg", QRectF(tab1.left() + 10, tab1.top() + 7, 15, 15))
    p.setFont(get_font("Inter", 8 if is_compact else 9, QFont.Weight.Medium))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(tab1.left() + 30, tab1.top(), t1_w - 36, 29), Qt.AlignmentFlag.AlignVCenter, "loofi@fedora: NoxForge")

    if not is_compact:
        tab2 = QRectF(tab_bar.left() + 258, tab_bar.top() + 3, 170, 29)
        p.setFont(get_font("Inter", 9, QFont.Weight.Normal))
        p.setPen(TEXT_DISABLED)
        p.drawText(QRectF(tab2.left() + 10, tab2.top(), 150, 29), Qt.AlignmentFlag.AlignVCenter, "noxforge-ctl (status)")

        p.setFont(get_font("Inter", 12, QFont.Weight.Bold))
        p.setPen(TEXT_DISABLED)
        p.drawText(QRectF(tab_bar.left() + 434, tab_bar.top(), 25, 29), Qt.AlignmentFlag.AlignCenter, "+")

    # Terminal Body
    body = QRectF(content.left() + 20, content.top() + tab_h + 16, content.width() - 40, content.height() - tab_h - 32)
    mono_font = get_font("JetBrains Mono", 8 if is_compact else 10)
    mono_bold = get_font("JetBrains Mono", 8 if is_compact else 10, QFont.Weight.Bold)

    y = body.top()

    # Prompt 1
    p.setFont(mono_bold)
    p.setPen(accent)
    p.drawText(QPointF(body.left(), y), "loofi@fedora")
    p.setPen(TEXT_SECONDARY)
    p.drawText(QPointF(body.left() + (75 if is_compact else 100), y), ":")
    p.setPen(ACCENT_CYAN)
    p.drawText(QPointF(body.left() + (85 if is_compact else 110), y), "~/Projects/NoxForge")
    p.setPen(ACCENT_VIOLET)
    p.drawText(QPointF(body.left() + (220 if is_compact else 290), y), "(main)")
    p.setPen(TEXT_PRIMARY)
    p.drawText(QPointF(body.left() + (270 if is_compact else 350), y), "$ fastfetch")
    y += 20 if is_compact else 24

    # Geometric NoxForge ASCII Art
    logo_lines = [
        "      __     ______   __   __   ",
        "     /  \\   |  ____|  \\ \\ / /   ",
        "    / /\\ \\  | |__      \\ V /    ",
        "   / ____ \\ |  __|      > <     ",
        "  /_/    \\_\\|_|        /_/ \\_\\  ",
        "                                ",
        "   ███╗   ██╗ ███████╗ ███████╗ ",
        "   ████╗  ██║ ██╔════╝ ██╔════╝ ",
        "   ██╔██╗ ██║ █████╗   ███████╗ ",
        "   ██║╚██╗██║ ██╔══╝   ╚════██║ ",
        "   ██║ ╚████║ ██║      ███████║ ",
        "   ╚═╝  ╚═══╝ ╚═╝      ╚══════╝ ",
    ]

    specs = [
        ("OS", "Fedora Linux 44 (Plasma 6.7)" if is_compact else "Fedora Linux 44 (Plasma Desktop) x86_64"),
        ("Kernel", "Linux 7.2.8-200.fc44.x86_64"),
        ("Uptime", "5 hours, 14 mins"),
        ("Packages", "3592 (rpm), 24 (flatpak)"),
        ("Shell", "zsh 5.9 (x86_64-linux-gnu)"),
        ("Display", "2560x1440 @ 165Hz (Wayland Native)"),
        ("DE", "KDE Plasma 6.7.5"),
        ("WM", "KWin (Wayland)"),
        ("WM Theme", "NoxForge Forge Notch (18px)"),
        ("Theme", "NoxForge Obsidian OLED [v14.0.0]"),
        ("Icons", "NoxForge Scalable [Vector]"),
        ("Style", "NoxForge Qt6 Engine [Dynamic]"),
        ("Terminal", "Konsole (Obsidian OLED)"),
        ("Memory", "7.85 GiB / 32.00 GiB (24%)"),
    ]

    logo_x = body.left() + 4
    specs_x = body.left() + (220 if is_compact else 330)
    start_y = y

    p.setFont(get_font("JetBrains Mono", 7 if is_compact else 10, QFont.Weight.Bold))
    for i, line in enumerate(logo_lines):
        ly = start_y + i * (14 if is_compact else 20)
        p.setPen(ACCENT_CYAN if i < 6 else accent)
        p.drawText(QPointF(logo_x, ly), line)

    for i, (k, v) in enumerate(specs):
        sy = start_y + i * (14 if is_compact else 19)
        p.setFont(mono_bold)
        p.setPen(accent)
        p.drawText(QPointF(specs_x, sy), f"{k:<9}")
        p.setPen(TEXT_SECONDARY)
        p.drawText(QPointF(specs_x + (65 if is_compact else 85), sy), "❯")
        p.setFont(mono_font)
        p.setPen(TEXT_PRIMARY if any(x in v for x in ["Obsidian", "Forge Notch", "Vector", "v14.0.0"]) else TEXT_SECONDARY)
        p.drawText(QPointF(specs_x + (80 if is_compact else 105), sy), v)

    swatch_y = start_y + len(specs) * (14 if is_compact else 19) + 8
    p.setFont(mono_bold)
    p.setPen(TEXT_DISABLED)
    p.drawText(QPointF(specs_x, swatch_y + 10), "MATRIX   ❯")

    # Forge Accent Matrix Colors
    matrix_colors = [
        QColor("#0D1419"), QColor("#000000"), QColor("#A3FF47"), QColor("#22D3EE"),
        QColor("#A78BFA"), QColor("#FBBF24"), QColor("#FF6B7A"), QColor("#E8F0F2")
    ]
    for idx, col in enumerate(matrix_colors):
        dot_x = specs_x + (80 if is_compact else 105) + idx * (20 if is_compact else 26)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(col)
        p.drawRoundedRect(QRectF(dot_x, swatch_y + 2, 16 if is_compact else 20, 10 if is_compact else 14), 2, 2)

    y = swatch_y + (28 if is_compact else 36)

    # Prompt 2: noxforge-ctl status
    p.setFont(mono_bold)
    p.setPen(accent)
    p.drawText(QPointF(body.left(), y), "loofi@fedora")
    p.setPen(TEXT_SECONDARY)
    p.drawText(QPointF(body.left() + (75 if is_compact else 100), y), ":")
    p.setPen(ACCENT_CYAN)
    p.drawText(QPointF(body.left() + (85 if is_compact else 110), y), "~/Projects/NoxForge")
    p.setPen(ACCENT_VIOLET)
    p.drawText(QPointF(body.left() + (220 if is_compact else 290), y), "(main)")
    p.setPen(TEXT_PRIMARY)
    p.drawText(QPointF(body.left() + (270 if is_compact else 350), y), "$ noxforge-ctl status")
    y += 18 if is_compact else 22

    ctl_status = [
        ("● Profile", "Obsidian OLED (True Black #000000)", accent),
        ("● Accent", "Electric Lime (#A3FF47) [Forge Accent Matrix]", accent),
        ("● Style Engine", "NoxForge Qt6 Native Engine v14.0.0 [Active]", ACCENT_CYAN),
        ("● Opacity", "Panel 88% | Popups 92% | Blur 18px", ACCENT_AMBER),
        ("● Diagnostics", "Schema 7 Doctor Qualified — 72/72 Checks PASS", accent),
    ]

    p.setFont(mono_font)
    for c_key, c_val, c_color in ctl_status:
        p.setPen(c_color)
        p.drawText(QPointF(body.left() + 14, y), c_key)
        p.setPen(TEXT_SECONDARY)
        p.drawText(QPointF(body.left() + (120 if is_compact else 160), y), "➜")
        p.setPen(TEXT_PRIMARY)
        p.drawText(QPointF(body.left() + (135 if is_compact else 180), y), c_val)
        y += 15 if is_compact else 18

    y += 8
    # Prompt 3 with cursor
    p.setFont(mono_bold)
    p.setPen(accent)
    p.drawText(QPointF(body.left(), y), "loofi@fedora")
    p.setPen(TEXT_SECONDARY)
    p.drawText(QPointF(body.left() + (75 if is_compact else 100), y), ":")
    p.setPen(ACCENT_CYAN)
    p.drawText(QPointF(body.left() + (85 if is_compact else 110), y), "~/Projects/NoxForge")
    p.setPen(ACCENT_VIOLET)
    p.drawText(QPointF(body.left() + (220 if is_compact else 290), y), "(main)")
    p.setPen(TEXT_PRIMARY)
    p.drawText(QPointF(body.left() + (270 if is_compact else 350), y), "$ ")
    p.fillRect(QRectF(body.left() + (285 if is_compact else 368), y - (11 if is_compact else 13), 7 if is_compact else 8, 14 if is_compact else 16), accent)

    p.end()
    return qimage_to_pil(img)


def create_control_center_window(
    width: int = 1260,
    height: int = 800,
    is_active: bool = True,
) -> Image.Image:
    """NoxForge Control Center GUI window showcasing Profile, Accent Matrix & Opacity sliders."""
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    content = draw_window_frame(
        p,
        QRectF(0, 0, width, height),
        "NoxForge Control Center — Unified Orchestration Hub",
        is_active=is_active,
        is_obsidian=False,
        accent=ACCENT_LIME,
    )

    # 3 Notched Tabs
    tab_h = 42
    tab_rect = QRectF(content.left(), content.top(), content.width(), tab_h)
    p.fillRect(tab_rect, SURFACE_SUNKEN)
    p.setPen(QPen(BORDER_DEFAULT, 1.0))
    p.drawLine(QPointF(tab_rect.left(), tab_rect.bottom()), QPointF(tab_rect.right(), tab_rect.bottom()))

    tabs = [
        ("Profil & Accent", True),
        ("Opacitet & Djup", False),
        ("Diagnostik & Doctor", False),
    ]

    tx = content.left() + 20
    for tname, is_sel in tabs:
        tw = 170
        tpath = notched_path(QRectF(tx, tab_rect.top() + 6, tw, tab_h - 6), radius=5, notch=12 if is_sel else 0)
        p.setPen(BORDER_STRONG if is_sel else BORDER_DEFAULT)
        p.setBrush(SURFACE_GRAPHITE if is_sel else SURFACE_RAISED)
        p.drawPath(tpath)
        if is_sel:
            p.setPen(QPen(ACCENT_LIME, 2.5))
            p.drawLine(QPointF(tx, tab_rect.top() + 18), QPointF(tx + 12, tab_rect.top() + 6))
        p.setFont(get_font("Inter", 10, QFont.Weight.DemiBold if is_sel else QFont.Weight.Normal))
        p.setPen(ACCENT_LIME if is_sel else TEXT_SECONDARY)
        p.drawText(QRectF(tx, tab_rect.top() + 6, tw, tab_h - 6), Qt.AlignmentFlag.AlignCenter, tname)
        tx += tw + 10

    # Body
    body = QRectF(content.left() + 24, content.top() + tab_h + 20, content.width() - 48, content.height() - tab_h - 36)
    col_w = (body.width() - 24) / 2

    # Left Column: Profile & Accent
    lx = body.left()
    ly = body.top()

    # Section 1: Skrivbordsprofil
    p_box = QRectF(lx, ly, col_w, 200)
    p.setPen(BORDER_DEFAULT)
    p.setBrush(SURFACE_RAISED)
    p.drawRoundedRect(p_box, 8, 8)

    p.setFont(get_font("Inter", 10, QFont.Weight.Bold))
    p.setPen(ACCENT_LIME)
    p.drawText(QRectF(lx + 16, ly + 14, col_w - 32, 20), Qt.AlignmentFlag.AlignVCenter, "SKRIVBORDSPROFIL (KDE, GTK & TERMINALS)")

    p.setFont(get_font("Inter", 9, QFont.Weight.Normal))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(lx + 16, ly + 36, col_w - 32, 20), Qt.AlignmentFlag.AlignVCenter, "Växla mellan grafitgrå ytor och sann pitch-black OLED-svärta:")

    # Profile Button 1: Graphite
    btn_g = QRectF(lx + 16, ly + 66, (col_w - 44) / 2, 80)
    p.setPen(BORDER_DEFAULT)
    p.setBrush(SURFACE_GRAPHITE)
    p.drawRoundedRect(btn_g, 6, 6)
    p.setFont(get_font("Inter", 10, QFont.Weight.Medium))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(btn_g.left() + 12, btn_g.top() + 14, btn_g.width() - 24, 20), Qt.AlignmentFlag.AlignVCenter, "NoxForge Graphite")
    p.setFont(get_font("Inter", 8, QFont.Weight.Normal))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(btn_g.left() + 12, btn_g.top() + 38, btn_g.width() - 24, 30), Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap, "Refined #0D1419 balanced contrast")

    # Profile Button 2: Obsidian OLED (ACTIVE)
    btn_o = QRectF(btn_g.right() + 12, ly + 66, (col_w - 44) / 2, 80)
    p.setPen(QPen(ACCENT_LIME, 2.0))
    p.setBrush(QColor("#102018"))
    p.drawRoundedRect(btn_o, 6, 6)
    p.setFont(get_font("Inter", 10, QFont.Weight.Bold))
    p.setPen(ACCENT_LIME)
    p.drawText(QRectF(btn_o.left() + 12, btn_o.top() + 14, btn_o.width() - 24, 20), Qt.AlignmentFlag.AlignVCenter, "NoxForge Obsidian")
    p.setFont(get_font("Inter", 8, QFont.Weight.Normal))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(btn_o.left() + 12, btn_o.top() + 38, btn_o.width() - 24, 30), Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap, "True #000000 OLED deep power saving")

    badge_act = QRectF(btn_o.right() - 56, btn_o.top() + 10, 48, 18)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(ACCENT_LIME)
    p.drawRoundedRect(badge_act, 3, 3)
    p.setFont(get_font("Inter", 7, QFont.Weight.Bold))
    p.setPen(ACCENT_INK)
    p.drawText(badge_act, Qt.AlignmentFlag.AlignCenter, "ACTIVE")

    # Section 2: Forge Accent Matrix
    a_box = QRectF(lx, p_box.bottom() + 16, col_w, 240)
    p.setPen(BORDER_DEFAULT)
    p.setBrush(SURFACE_RAISED)
    p.drawRoundedRect(a_box, 8, 8)

    p.setFont(get_font("Inter", 10, QFont.Weight.Bold))
    p.setPen(ACCENT_LIME)
    p.drawText(QRectF(lx + 16, a_box.top() + 14, col_w - 32, 20), Qt.AlignmentFlag.AlignVCenter, "FORGE ACCENT MATRIX")

    p.setFont(get_font("Inter", 9, QFont.Weight.Normal))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(lx + 16, a_box.top() + 36, col_w - 32, 20), Qt.AlignmentFlag.AlignVCenter, "Välj signaturaccentfärg för kontroller, fokusramar och notch-markeringar:")

    accents = [
        ("lime", "Electric Lime (#A3FF47)", ACCENT_LIME, True),
        ("cyan", "Forge Cyan (#22D3EE)", ACCENT_CYAN, False),
        ("violet", "Cyber Violet (#A78BFA)", ACCENT_VIOLET, False),
        ("amber", "Molten Amber (#FBBF24)", ACCENT_AMBER, False),
    ]

    ay = a_box.top() + 66
    for idx, (akey, alabel, acolor, is_sel) in enumerate(accents):
        col_idx = idx % 2
        row_idx = idx // 2
        abtn_x = lx + 16 + col_idx * ((col_w - 44) / 2 + 12)
        abtn_y = ay + row_idx * 54
        abtn_rect = QRectF(abtn_x, abtn_y, (col_w - 44) / 2, 44)

        p.setPen(QPen(acolor if is_sel else BORDER_DEFAULT, 1.8 if is_sel else 1.0))
        p.setBrush(SURFACE_SELECTED if is_sel else SURFACE_GRAPHITE)
        p.drawRoundedRect(abtn_rect, 6, 6)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(acolor)
        p.drawEllipse(QPointF(abtn_rect.left() + 20, abtn_rect.center().y()), 6, 6)

        p.setFont(get_font("Inter", 9, QFont.Weight.Bold if is_sel else QFont.Weight.Medium))
        p.setPen(acolor if is_sel else TEXT_PRIMARY)
        p.drawText(QRectF(abtn_rect.left() + 34, abtn_rect.top(), abtn_rect.width() - 40, 44), Qt.AlignmentFlag.AlignVCenter, alabel)

    # Section 3: Day/Night Scheduler
    sched_box = QRectF(lx, a_box.bottom() + 16, col_w, body.bottom() - a_box.bottom() - 16)
    p.setPen(BORDER_DEFAULT)
    p.setBrush(SURFACE_RAISED)
    p.drawRoundedRect(sched_box, 8, 8)

    p.setFont(get_font("Inter", 10, QFont.Weight.Bold))
    p.setPen(ACCENT_LIME)
    p.drawText(QRectF(lx + 16, sched_box.top() + 14, col_w - 32, 20), Qt.AlignmentFlag.AlignVCenter, "DAG / NATT AUTOMATISERING")

    chk_r = QRectF(lx + 16, sched_box.top() + 44, 18, 18)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(ACCENT_LIME)
    p.drawRoundedRect(chk_r, 4, 4)
    p.setPen(QPen(ACCENT_INK, 2.0))
    p.drawLine(QPointF(chk_r.left() + 4, chk_r.top() + 9), QPointF(chk_r.left() + 8, chk_r.top() + 13))
    p.drawLine(QPointF(chk_r.left() + 8, chk_r.top() + 13), QPointF(chk_r.left() + 14, chk_r.top() + 5))

    p.setFont(get_font("Inter", 9, QFont.Weight.Medium))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(lx + 44, sched_box.top() + 42, col_w - 60, 22), Qt.AlignmentFlag.AlignVCenter, "Automatisk växling: Graphite (07:00) / Obsidian (20:00)")

    # Right Column: Opacity Configurator (Live Preview Sliders)
    rx = body.left() + col_w + 24
    ry = body.top()

    op_box = QRectF(rx, ry, col_w, 360)
    p.setPen(BORDER_DEFAULT)
    p.setBrush(SURFACE_RAISED)
    p.drawRoundedRect(op_box, 8, 8)

    p.setFont(get_font("Inter", 10, QFont.Weight.Bold))
    p.setPen(ACCENT_LIME)
    p.drawText(QRectF(rx + 16, ry + 14, col_w - 32, 20), Qt.AlignmentFlag.AlignVCenter, "OPACITET & DJUP (NOXFORGE-OPACITY)")

    p.setFont(get_font("Inter", 9, QFont.Weight.Normal))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(rx + 16, ry + 36, col_w - 32, 20), Qt.AlignmentFlag.AlignVCenter, "Justera transparens och oskärpedjup i realtid för paneler och fönster:")

    sliders = [
        ("Plasma Panel Transparency", 0.88, "88% (Standard)"),
        ("Popups, Menus & Kickoff", 0.92, "92% (High Readability)"),
        ("Aurorae Window Decoration Blur", 0.75, "18px Gaussian Radius"),
    ]

    s_y = ry + 68
    for s_label, s_val, s_text in sliders:
        p.setFont(get_font("Inter", 9, QFont.Weight.Medium))
        p.setPen(TEXT_PRIMARY)
        p.drawText(QRectF(rx + 16, s_y, col_w - 32, 18), Qt.AlignmentFlag.AlignVCenter, s_label)
        p.setFont(get_font("Inter", 9, QFont.Weight.Bold))
        p.setPen(ACCENT_LIME)
        p.drawText(QRectF(rx + 16, s_y, col_w - 32, 18), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, s_text)
        s_y += 24

        track = QRectF(rx + 16, s_y + 4, col_w - 32, 8)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(SURFACE_SUNKEN)
        p.drawRoundedRect(track, 4, 4)
        p.setBrush(ACCENT_LIME)
        p.drawRoundedRect(QRectF(track.left(), track.top(), track.width() * s_val, 8), 4, 4)
        p.setBrush(TEXT_PRIMARY)
        p.drawEllipse(QPointF(track.left() + track.width() * s_val, track.center().y()), 8, 8)
        s_y += 36

    # Presets Row
    p.setFont(get_font("Inter", 9, QFont.Weight.Medium))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(rx + 16, s_y, col_w - 32, 18), Qt.AlignmentFlag.AlignVCenter, "Förinställda profiler:")
    s_y += 24

    presets = ["Solid (100%)", "Default (88%)", "Translucent (75%)", "Glass (60%)"]
    pw = (col_w - 32 - 24) / len(presets)
    for p_idx, ptext in enumerate(presets):
        pr = QRectF(rx + 16 + p_idx * (pw + 8), s_y, pw, 32)
        is_p_sel = (p_idx == 1)
        p.setPen(BORDER_STRONG if is_p_sel else BORDER_DEFAULT)
        p.setBrush(SURFACE_SELECTED if is_p_sel else SURFACE_GRAPHITE)
        p.drawRoundedRect(pr, 5, 5)
        p.setFont(get_font("Inter", 8, QFont.Weight.Bold if is_p_sel else QFont.Weight.Normal))
        p.setPen(ACCENT_LIME if is_p_sel else TEXT_PRIMARY)
        p.drawText(pr, Qt.AlignmentFlag.AlignCenter, ptext)

    # Diagnostics Box on bottom right
    diag_box = QRectF(rx, op_box.bottom() + 16, col_w, body.bottom() - op_box.bottom() - 16)
    p.setPen(BORDER_DEFAULT)
    p.setBrush(SURFACE_RAISED)
    p.drawRoundedRect(diag_box, 8, 8)

    p.setFont(get_font("Inter", 10, QFont.Weight.Bold))
    p.setPen(ACCENT_LIME)
    p.drawText(QRectF(rx + 16, diag_box.top() + 14, col_w - 32, 20), Qt.AlignmentFlag.AlignVCenter, "SYSTEMDIAGNOSTIK & DOKTOR (SCHEMA 7)")

    checks = [
        ("✔ Schema 7 Validering", "72 / 72 kontroller godkända (100% PASS)", ACCENT_LIME),
        ("✔ Native Qt 6 Style", "noxforgestyle.so laddad i KWin/Plasma", ACCENT_CYAN),
        ("✔ Forge Notch Aurorae", "18px chamfer aktiv på Wayland", ACCENT_LIME),
        ("✔ KWin TabBox Switcher", "Obsidian kwin-switcher synkroniserad", ACCENT_AMBER),
    ]

    dy = diag_box.top() + 42
    for c_title, c_desc, c_col in checks:
        p.setFont(get_font("Inter", 9, QFont.Weight.Bold))
        p.setPen(c_col)
        p.drawText(QRectF(rx + 16, dy, 180, 20), Qt.AlignmentFlag.AlignVCenter, c_title)
        p.setFont(get_font("Inter", 9, QFont.Weight.Normal))
        p.setPen(TEXT_PRIMARY)
        p.drawText(QRectF(rx + 200, dy, col_w - 220, 20), Qt.AlignmentFlag.AlignVCenter, c_desc)
        dy += 24

    p.end()
    return qimage_to_pil(img)


def create_plasma_panel(width: int = 2240, height: int = 58) -> Image.Image:
    """Floating Plasma 6 panel with running tasks, system tray, and NoxForge launcher."""
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    panel_rect = QRectF(0, 0, width, height)
    p.setPen(QPen(BORDER_STRONG, 1.2))
    p.setBrush(QColor(13, 20, 25, 235))
    p.drawRoundedRect(panel_rect, 14, 14)

    # Launcher button with glowing Forge mark
    render_svg(p, BRAND / "noxforge-mark.svg", QRectF(16, 13, 32, 32))

    tasks = [
        ("Projects", "places/folder.svg", True),
        ("Konsole", "actions/utilities-terminal.svg", True),
        ("Control Center", "preferences/preferences-system.svg", True),
        ("Kate", "actions/document-new.svg", False),
        ("Firefox", "categories/applications-internet.svg", False),
    ]

    tx = 68
    for name, icon, is_active in tasks:
        item_w = 136 if is_active else 44
        task_rect = QRectF(tx, 8, item_w, height - 16)
        if is_active:
            p.setPen(BORDER_DEFAULT)
            p.setBrush(SURFACE_RAISED)
            p.drawRoundedRect(task_rect, 8, 8)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(ACCENT_LIME)
            p.drawRoundedRect(QRectF(task_rect.left() + 20, task_rect.bottom() - 3, task_rect.width() - 40, 3), 1.5, 1.5)

            render_svg(p, ICONS / icon, QRectF(task_rect.left() + 10, task_rect.top() + (task_rect.height() - 20) / 2, 20, 20))
            p.setFont(get_font("Inter", 9, QFont.Weight.Medium))
            p.setPen(TEXT_PRIMARY)
            p.drawText(QRectF(task_rect.left() + 36, task_rect.top(), task_rect.width() - 40, task_rect.height()), Qt.AlignmentFlag.AlignVCenter, name)
        else:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(255, 255, 255, 12))
            p.drawRoundedRect(task_rect, 8, 8)
            render_svg(p, ICONS / icon, QRectF(task_rect.left() + (item_w - 22) / 2, task_rect.top() + (task_rect.height() - 22) / 2, 22, 22))
            p.setBrush(TEXT_SECONDARY)
            p.drawEllipse(QPointF(task_rect.center().x(), task_rect.bottom() - 2), 2, 2)

        tx += item_w + 8

    # System Tray & Clock
    rx = width - 20
    p.setPen(QPen(BORDER_STRONG, 1.5))
    p.drawLine(QPointF(rx - 10, 14), QPointF(rx - 10, height - 14))

    rx -= 120
    p.setFont(get_font("Inter", 10, QFont.Weight.DemiBold))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(rx, 9, 100, 20), Qt.AlignmentFlag.AlignCenter, "14:28")
    p.setFont(get_font("Inter", 8, QFont.Weight.Normal))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(rx, 29, 100, 18), Qt.AlignmentFlag.AlignCenter, "Ons, 1 Okt")

    tray_icons = [
        "status/battery-good.svg",
        "status/audio-volume-high.svg",
        "status/network-wireless.svg",
        "status/security-high.svg",
    ]
    rx -= 30
    for ticon in tray_icons:
        rx -= 32
        render_svg(p, ICONS / ticon, QRectF(rx, 18, 22, 22))

    p.end()
    return qimage_to_pil(img)


def create_launcher_window(width: int = 760, height: int = 600) -> Image.Image:
    """Kickoff application launcher window with user profile, categories & apps."""
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    box = QRectF(0, 0, width, height)
    p.setPen(QPen(BORDER_STRONG, 1.2))
    p.setBrush(QColor(14, 22, 28, 250))
    p.drawRoundedRect(box, 12, 12)

    hdr = QRectF(0, 0, width, 58)
    p.fillRect(hdr, SURFACE_RAISED)
    p.setPen(QPen(BORDER_DEFAULT, 1.0))
    p.drawLine(QPointF(hdr.left(), hdr.bottom()), QPointF(hdr.right(), hdr.bottom()))

    avatar_rect = QRectF(18, 11, 36, 36)
    p.setPen(QPen(ACCENT_LIME, 2.0))
    p.setBrush(SURFACE_SUNKEN)
    p.drawEllipse(avatar_rect)
    p.setFont(get_font("Inter", 11, QFont.Weight.Bold))
    p.setPen(ACCENT_LIME)
    p.drawText(avatar_rect, Qt.AlignmentFlag.AlignCenter, "DU")

    p.setFont(get_font("Inter", 11, QFont.Weight.DemiBold))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(64, 11, 200, 36), Qt.AlignmentFlag.AlignVCenter, "Demo User")

    search_r = QRectF(width - 360, 13, 340, 32)
    p.setPen(QPen(ACCENT_LIME, 1.5))
    p.setBrush(SURFACE_SUNKEN)
    p.drawRoundedRect(search_r, 6, 6)
    render_svg(p, ICONS / "actions/system-search.svg", QRectF(search_r.left() + 8, search_r.top() + 7, 18, 18))
    p.setFont(get_font("Inter", 9, QFont.Weight.Normal))
    p.setPen(TEXT_DISABLED)
    p.drawText(QRectF(search_r.left() + 32, search_r.top(), 280, 32), Qt.AlignmentFlag.AlignVCenter, "Search applications, files, settings...")

    cat_w = 200
    cat_rect = QRectF(0, 58, cat_w, height - 58 - 46)
    p.fillRect(cat_rect, SURFACE_SUNKEN)
    p.setPen(QPen(BORDER_DEFAULT, 1.0))
    p.drawLine(QPointF(cat_rect.right(), cat_rect.top()), QPointF(cat_rect.right(), cat_rect.bottom()))

    categories = [
        ("Favoriter", "status/task-complete.svg", True),
        ("Utveckling", "categories/applications-development.svg", False),
        ("System", "categories/applications-system.svg", False),
        ("Grafik", "categories/applications-graphics.svg", False),
        ("Internet", "categories/applications-internet.svg", False),
        ("Multimedia", "categories/applications-multimedia.svg", False),
        ("Verktyg", "categories/applications-utilities.svg", False),
    ]

    cy = 72
    for cname, cicon, csel in categories:
        crect = QRectF(8, cy, cat_w - 16, 36)
        if csel:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(SURFACE_SELECTED)
            p.drawRoundedRect(crect, 6, 6)
            p.setBrush(ACCENT_LIME)
            p.drawRoundedRect(QRectF(crect.left(), crect.top() + 6, 3, 24), 1.5, 1.5)

        render_svg(p, ICONS / cicon, QRectF(crect.left() + 12, crect.top() + 8, 20, 20))
        p.setFont(get_font("Inter", 10, QFont.Weight.Medium if csel else QFont.Weight.Normal))
        p.setPen(ACCENT_LIME if csel else TEXT_PRIMARY)
        p.drawText(QRectF(crect.left() + 40, crect.top(), 140, 36), Qt.AlignmentFlag.AlignVCenter, cname)
        cy += 40

    apps = [
        ("NoxForge Control Center", "Unified orchestration suite", "preferences/preferences-system.svg"),
        ("NoxForge Opacity", "Depth & transparency configurator", "categories/applications-graphics.svg"),
        ("Konsole", "Everyday command-line precision", "actions/utilities-terminal.svg"),
        ("Dolphin", "Vector file management", "places/folder.svg"),
        ("System Settings", "KDE Plasma appearance & hardware", "preferences/preferences-system.svg"),
        ("Kate", "Advanced code and text editor", "actions/document-new.svg"),
    ]

    ax = cat_w + 20
    ay = 72
    app_w = (width - cat_w - 40) / 2

    for i, (aname, adesc, aicon) in enumerate(apps):
        col = i % 2
        row = i // 2
        cur_x = ax + col * app_w
        cur_y = ay + row * 98
        app_box = QRectF(cur_x, cur_y, app_w - 12, 86)

        p.setPen(BORDER_DEFAULT)
        p.setBrush(SURFACE_RAISED)
        p.drawRoundedRect(app_box, 8, 8)

        render_svg(p, ICONS / aicon, QRectF(app_box.left() + 14, app_box.top() + 23, 40, 40))

        p.setFont(get_font("Inter", 10, QFont.Weight.DemiBold))
        p.setPen(TEXT_PRIMARY)
        p.drawText(QRectF(app_box.left() + 66, app_box.top() + 22, app_box.width() - 72, 22), Qt.AlignmentFlag.AlignVCenter, aname)

        p.setFont(get_font("Inter", 8, QFont.Weight.Normal))
        p.setPen(TEXT_SECONDARY)
        p.drawText(QRectF(app_box.left() + 66, app_box.top() + 44, app_box.width() - 72, 18), Qt.AlignmentFlag.AlignVCenter, adesc)

    ftr = QRectF(0, height - 46, width, 46)
    p.fillRect(ftr, SURFACE_SUNKEN)
    p.setPen(QPen(BORDER_DEFAULT, 1.0))
    p.drawLine(QPointF(ftr.left(), ftr.top()), QPointF(ftr.right(), ftr.top()))

    p.setFont(get_font("Inter", 9, QFont.Weight.Medium))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(20, height - 46, 200, 46), Qt.AlignmentFlag.AlignVCenter, "Session Controls")

    actions = ["Lås", "Viloläge", "Starta om", "Stäng av"]
    rx = width - 20
    for act in reversed(actions):
        rx -= 84
        p.drawText(QRectF(rx, height - 46, 80, 46), Qt.AlignmentFlag.AlignCenter, act)

    p.end()
    return qimage_to_pil(img)


def create_lockscreen_card(width: int = 700, height: int = 440) -> Image.Image:
    """Card previewing the native Plasma 6 / Wayland Lock Screen with kinetic password focus."""
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    box = QRectF(0, 0, width, height)
    p.setPen(QPen(BORDER_STRONG, 1.2))
    p.setBrush(QColor(8, 12, 16, 248))
    p.drawRoundedRect(box, 14, 14)

    # Ambient glow on top
    grad = QLinearGradient(0, 0, width, 0)
    grad.setColorAt(0.0, QColor(34, 211, 238, 40))
    grad.setColorAt(0.5, QColor(163, 255, 71, 50))
    grad.setColorAt(1.0, QColor(167, 139, 250, 40))
    p.fillRect(QRectF(0, 0, width, 4), grad)

    # Header title
    p.setFont(get_font("Inter", 9, QFont.Weight.Bold))
    p.setPen(ACCENT_LIME)
    p.drawText(QRectF(24, 20, width - 48, 20), Qt.AlignmentFlag.AlignCenter, "PLASMA 6 / WAYLAND NATIVE LOCK SCREEN")

    # Large Clock
    p.setFont(get_font("Inter", 44, QFont.Weight.Bold))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(0, 56, width, 54), Qt.AlignmentFlag.AlignCenter, "14:28")

    # Date
    p.setFont(get_font("Inter", 12, QFont.Weight.Medium))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(0, 116, width, 24), Qt.AlignmentFlag.AlignCenter, "Onsdag, 1 Oktober")

    # Avatar
    av_rect = QRectF((width - 64) / 2, 156, 64, 64)
    p.setPen(QPen(ACCENT_LIME, 2.5))
    p.setBrush(SURFACE_RAISED)
    p.drawEllipse(av_rect)
    p.setFont(get_font("Inter", 18, QFont.Weight.Bold))
    p.setPen(ACCENT_LIME)
    p.drawText(av_rect, Qt.AlignmentFlag.AlignCenter, "DU")

    p.setFont(get_font("Inter", 12, QFont.Weight.DemiBold))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(0, 230, width, 24), Qt.AlignmentFlag.AlignCenter, "Demo User")

    # Kinetic Password Field
    pw_rect = QRectF((width - 320) / 2, 268, 320, 42)
    p.setPen(QPen(ACCENT_LIME, 2.0))
    p.setBrush(BG_OBSIDIAN)
    p.drawRoundedRect(pw_rect, 6, 6)

    p.setFont(get_font("Inter", 16, QFont.Weight.Bold))
    p.setPen(ACCENT_LIME)
    p.drawText(QRectF(pw_rect.left() + 16, pw_rect.top(), pw_rect.width() - 60, 42), Qt.AlignmentFlag.AlignVCenter, "••••••••••••")

    # Unlock arrow button
    btn_r = QRectF(pw_rect.right() - 36, pw_rect.top() + 6, 30, 30)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(ACCENT_LIME)
    p.drawRoundedRect(btn_r, 4, 4)
    p.setFont(get_font("Inter", 14, QFont.Weight.Bold))
    p.setPen(ACCENT_INK)
    p.drawText(btn_r, Qt.AlignmentFlag.AlignCenter, "➔")

    # Prompt tag
    p.setFont(get_font("Inter", 8, QFont.Weight.Normal))
    p.setPen(TEXT_DISABLED)
    p.drawText(QRectF(0, 320, width, 20), Qt.AlignmentFlag.AlignCenter, "Kinetic focus ring • PAM & biometric ready")

    # Session Buttons
    s_actions = ["Viloläge", "Starta om", "Stäng av"]
    sx = (width - len(s_actions) * 100) / 2
    for sa in s_actions:
        sr = QRectF(sx, 370, 90, 30)
        p.setPen(BORDER_DEFAULT)
        p.setBrush(SURFACE_RAISED)
        p.drawRoundedRect(sr, 5, 5)
        p.setFont(get_font("Inter", 8, QFont.Weight.Medium))
        p.setPen(TEXT_SECONDARY)
        p.drawText(sr, Qt.AlignmentFlag.AlignCenter, sa)
        sx += 100

    p.end()
    return qimage_to_pil(img)


def create_alt_tab_switcher(width: int = 940, height: int = 280) -> Image.Image:
    """Obsidian KWin TabBox switcher overlay (Alt+Tab) with notched window cards."""
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    box = QRectF(0, 0, width, height)
    p.setPen(QPen(BORDER_STRONG, 1.5))
    p.setBrush(QColor(10, 16, 20, 248))
    p.drawRoundedRect(box, 14, 14)

    cards = [
        ("NoxForge Control Center", "preferences/preferences-system.svg", True),
        ("Konsole — fastfetch", "actions/utilities-terminal.svg", False),
        ("Dolphin — Projects", "places/folder.svg", False),
        ("Kate — main.cpp", "actions/document-new.svg", False),
    ]

    card_w = (width - 64) / 4
    for i, (ctitle, cicon, csel) in enumerate(cards):
        cx = 24 + i * (card_w + 4)
        cy = 28
        c_rect = QRectF(cx, cy, card_w - 8, 180)

        cpath = notched_path(c_rect, radius=6, notch=14 if csel else 0)
        p.setPen(QPen(ACCENT_LIME if csel else BORDER_DEFAULT, 2.0 if csel else 1.0))
        p.setBrush(SURFACE_SELECTED if csel else SURFACE_RAISED)
        p.drawPath(cpath)

        if csel:
            p.setPen(QPen(ACCENT_LIME, 2.5))
            p.drawLine(QPointF(c_rect.left(), c_rect.top() + 14), QPointF(c_rect.left() + 14, c_rect.top()))

        thumb = QRectF(c_rect.left() + 12, c_rect.top() + 16, c_rect.width() - 24, 105)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(BG_OBSIDIAN if csel else SURFACE_SUNKEN)
        p.drawRoundedRect(thumb, 4, 4)
        render_svg(p, ICONS / cicon, QRectF(thumb.left() + (thumb.width() - 48) / 2, thumb.top() + (thumb.height() - 48) / 2, 48, 48))

        p.setFont(get_font("Inter", 9, QFont.Weight.DemiBold if csel else QFont.Weight.Medium))
        p.setPen(ACCENT_LIME if csel else TEXT_PRIMARY)
        p.drawText(QRectF(c_rect.left() + 6, c_rect.bottom() - 46, c_rect.width() - 12, 38), Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, ctitle)

    p.setFont(get_font("Inter", 10, QFont.Weight.DemiBold))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(0, height - 36, width, 24), Qt.AlignmentFlag.AlignCenter, "Active Window: NoxForge Control Center (Obsidian OLED)")

    p.end()
    return qimage_to_pil(img)


def create_icon_palette_card(width: int = 1180, height: int = 420) -> Image.Image:
    """Card displaying representative original vector icons categorized with optical scales."""
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    box = QRectF(0, 0, width, height)
    p.setPen(QPen(BORDER_STRONG, 1.2))
    p.setBrush(QColor(14, 22, 28, 245))
    p.drawRoundedRect(box, 12, 12)

    p.fillRect(QRectF(0, 0, width, 46), SURFACE_RAISED)
    p.setPen(QPen(BORDER_DEFAULT, 1.0))
    p.drawLine(QPointF(0, 46), QPointF(width, 46))

    p.setFont(get_font("Inter", 11, QFont.Weight.Bold))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(20, 0, 450, 46), Qt.AlignmentFlag.AlignVCenter, "ORIGINAL SCALABLE VECTOR ICON SET • 16 / 22 / 32 / 48 / 64px")

    p.setFont(get_font("Inter", 9, QFont.Weight.DemiBold))
    p.setPen(ACCENT_LIME)
    p.drawText(QRectF(width - 360, 0, 340, 46), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, "Geometric Line Art & Electric Lime / Cyan Accents")

    icon_groups = [
        ("PLACES", [
            ("user-home.svg", "Home"),
            ("folder-documents.svg", "Documents"),
            ("folder-pictures.svg", "Pictures"),
            ("folder-download.svg", "Downloads"),
            ("user-trash.svg", "Trash"),
        ]),
        ("DEVICES", [
            ("computer.svg", "Computer"),
            ("drive-harddisk.svg", "Storage"),
            ("audio-card.svg", "Audio"),
            ("input-keyboard.svg", "Keyboard"),
            ("phone.svg", "Mobile"),
        ]),
        ("ACTIONS", [
            ("document-new.svg", "New File"),
            ("document-save.svg", "Save"),
            ("edit-copy.svg", "Copy"),
            ("system-search.svg", "Search"),
            ("configure.svg", "Configure"),
        ]),
        ("STATUS", [
            ("network-wireless.svg", "Wireless"),
            ("audio-volume-high.svg", "Volume"),
            ("battery-good.svg", "Battery"),
            ("security-high.svg", "Security"),
            ("task-complete.svg", "Qualified"),
        ]),
    ]

    gy = 62
    col_w = (width - 40) / len(icon_groups)
    for g_idx, (gname, items) in enumerate(icon_groups):
        gx = 20 + g_idx * col_w
        p.setFont(get_font("Inter", 9, QFont.Weight.Bold))
        p.setPen(ACCENT_CYAN)
        p.drawText(QRectF(gx, gy, col_w, 20), Qt.AlignmentFlag.AlignLeft, gname)

        iy = gy + 28
        for ifile, ilabel in items:
            i_box = QRectF(gx, iy, col_w - 16, 54)
            p.setPen(BORDER_DEFAULT)
            p.setBrush(SURFACE_GRAPHITE)
            p.drawRoundedRect(i_box, 6, 6)

            full_p = ICONS / f"{gname.lower()}/{ifile}"
            render_svg(p, full_p, QRectF(i_box.left() + 10, i_box.top() + 11, 32, 32))

            p.setFont(get_font("Inter", 10, QFont.Weight.Medium))
            p.setPen(TEXT_PRIMARY)
            p.drawText(QRectF(i_box.left() + 52, i_box.top() + 10, i_box.width() - 60, 18), Qt.AlignmentFlag.AlignVCenter, ilabel)

            p.setFont(get_font("Inter", 8, QFont.Weight.Normal))
            p.setPen(ACCENT_LIME)
            p.drawText(QRectF(i_box.left() + 52, i_box.top() + 28, i_box.width() - 60, 16), Qt.AlignmentFlag.AlignVCenter, "Scalable Vector")

            iy += 60

    p.end()
    return qimage_to_pil(img)


def create_header_banner(title: str, subtitle: str, width: int = 2560) -> Image.Image:
    """Header banner across gallery screenshots with brand lockup & version badge."""
    h = 140
    img = QImage(width, h, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    grad = QLinearGradient(0, 0, 0, h)
    grad.setColorAt(0.0, QColor(9, 14, 18, 235))
    grad.setColorAt(1.0, QColor(9, 14, 18, 0))
    p.fillRect(QRect(0, 0, width, h), grad)

    render_svg(p, BRAND / "noxforge-lockup.svg", QRectF(80, 24, 240, 58))

    p.setFont(get_font("Inter", 24, QFont.Weight.Bold))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(360, 22, width - 680, 36), Qt.AlignmentFlag.AlignVCenter, title)

    p.setFont(get_font("Inter", 12, QFont.Weight.Medium))
    p.setPen(ACCENT_LIME)
    p.drawText(QRectF(360, 60, width - 680, 26), Qt.AlignmentFlag.AlignVCenter, subtitle)

    p.setPen(QPen(ACCENT_LIME, 2.0))
    p.drawLine(QPointF(360, 92), QPointF(520, 92))

    # Version Badge Pill on Right
    badge_rect = QRectF(width - 280, 32, 200, 34)
    p.setPen(BORDER_STRONG)
    p.setBrush(SURFACE_RAISED)
    p.drawRoundedRect(badge_rect, 6, 6)
    p.setFont(get_font("Inter", 10, QFont.Weight.Bold))
    p.setPen(ACCENT_LIME)
    p.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, "VERSION 14.0.0 • PLASMA 6")

    p.end()
    return qimage_to_pil(img)


def create_palette_callout_pill(label: str, desc: str, color: QColor, width: int = 340) -> Image.Image:
    """Small floating pill badge for palette callouts."""
    h = 56
    img = QImage(width, h, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    box = QRectF(0, 0, width, h)
    p.setPen(QPen(BORDER_STRONG, 1.2))
    p.setBrush(QColor(10, 15, 20, 240))
    p.drawRoundedRect(box, 8, 8)

    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(color)
    p.drawRoundedRect(QRectF(14, 14, 28, 28), 6, 6)

    p.setFont(get_font("Inter", 10, QFont.Weight.Bold))
    p.setPen(color)
    p.drawText(QRectF(52, 10, width - 60, 20), Qt.AlignmentFlag.AlignVCenter, label)

    p.setFont(get_font("Inter", 8, QFont.Weight.Normal))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(52, 30, width - 60, 16), Qt.AlignmentFlag.AlignVCenter, desc)

    p.end()
    return qimage_to_pil(img)


def create_accent_matrix_strip(width: int = 740, height: int = 68) -> Image.Image:
    """Floating card showcasing the 4 Forge Accent Matrix colors."""
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    box = QRectF(0, 0, width, height)
    p.setPen(QPen(BORDER_STRONG, 1.2))
    p.setBrush(QColor(10, 16, 20, 245))
    p.drawRoundedRect(box, 10, 10)

    p.setFont(get_font("Inter", 9, QFont.Weight.Bold))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(20, 0, 180, height), Qt.AlignmentFlag.AlignVCenter, "FORGE ACCENT MATRIX ❯")

    accents = [
        ("Lime", ACCENT_LIME, True),
        ("Cyan", ACCENT_CYAN, False),
        ("Violet", ACCENT_VIOLET, False),
        ("Amber", ACCENT_AMBER, False),
    ]

    bx = 200
    for aname, acolor, is_sel in accents:
        pill = QRectF(bx, 14, 120, 40)
        p.setPen(QPen(acolor if is_sel else BORDER_DEFAULT, 1.5 if is_sel else 1.0))
        p.setBrush(SURFACE_SELECTED if is_sel else SURFACE_RAISED)
        p.drawRoundedRect(pill, 6, 6)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(acolor)
        p.drawEllipse(QPointF(pill.left() + 18, pill.center().y()), 5, 5)

        p.setFont(get_font("Inter", 9, QFont.Weight.Bold if is_sel else QFont.Weight.Medium))
        p.setPen(acolor if is_sel else TEXT_SECONDARY)
        p.drawText(QRectF(pill.left() + 30, pill.top(), 80, 40), Qt.AlignmentFlag.AlignVCenter, aname)

        bx += 132

    p.end()
    return qimage_to_pil(img)


# -------------------------------------------------------------------------
# Screenshot Composition Generators
# -------------------------------------------------------------------------

def generate_screenshot_01_hero_desktop(out_path_1440: Path, out_path_1080: Path) -> None:
    print("Generating 01_hero_desktop_showcase...")
    wp_path = WALLPAPERS / "2560x1440.png"
    canvas = Image.open(wp_path).convert("RGBA")

    dolphin = create_dolphin_window(width=1160, height=740, is_active=False)
    konsole = create_konsole_window(width=1240, height=800, is_active=True, is_obsidian=True)
    panel = create_plasma_panel(width=2240, height=58)

    add_drop_shadow(canvas, dolphin, (100, 160), radius=34, offset=(0, 18), opacity=0.55)
    add_drop_shadow(canvas, konsole, (1200, 240), radius=40, offset=(0, 22), opacity=0.68)
    add_drop_shadow(canvas, panel, (160, 1354), radius=22, offset=(0, 10), opacity=0.48)

    canvas.save(out_path_1440, "PNG")
    canvas.resize((1920, 1080), Image.Resampling.LANCZOS).save(out_path_1080, "PNG")
    print(f"Saved {out_path_1440.name} and {out_path_1080.name}")


def generate_screenshot_02_dual_palettes(out_path_1440: Path, out_path_1080: Path) -> None:
    print("Generating 02_dual_palettes_obsidian...")
    wp_path = WALLPAPERS / "2560x1440.png"
    canvas = Image.open(wp_path).convert("RGBA")

    banner = create_header_banner(
        "DUAL-PALETTE PARITY • GRAPHITE & TRUE OBSIDIAN OLED",
        "Refined deep graphite surfaces (#0D1419) and pure pitch-black OLED depth (#000000) with Forge Accent Matrix"
    )
    canvas.alpha_composite(banner, (0, 0))

    dolphin_graphite = create_dolphin_window(
        width=1140,
        height=840,
        is_active=True,
        is_obsidian=False,
        accent=ACCENT_CYAN,
        custom_title="NoxForge Graphite (#0D1419) — Dolphin",
    )
    konsole_obsidian = create_konsole_window(
        width=1140,
        height=840,
        is_active=True,
        is_obsidian=True,
        accent=ACCENT_LIME,
        custom_title="NoxForge Obsidian OLED (#000000) — Konsole",
    )

    add_drop_shadow(canvas, dolphin_graphite, (90, 200), radius=34, offset=(0, 18), opacity=0.58)
    add_drop_shadow(canvas, konsole_obsidian, (1330, 200), radius=36, offset=(0, 18), opacity=0.68)

    # Callout badges above each window
    pill_graphite = create_palette_callout_pill("GRAPHITE (#0D1419)", "Balanced contrast • Daylight focus", ACCENT_CYAN, width=320)
    pill_obsidian = create_palette_callout_pill("OBSIDIAN OLED (#000000)", "True pitch-black • OLED power efficiency", ACCENT_LIME, width=340)

    add_drop_shadow(canvas, pill_graphite, (90, 1060), radius=20, offset=(0, 8), opacity=0.6)
    add_drop_shadow(canvas, pill_obsidian, (1330, 1060), radius=20, offset=(0, 8), opacity=0.6)

    # Accent Matrix strip at center bottom
    matrix_card = create_accent_matrix_strip(width=760, height=64)
    add_drop_shadow(canvas, matrix_card, (900, 1260), radius=24, offset=(0, 10), opacity=0.6)

    panel = create_plasma_panel(width=2240, height=58)
    add_drop_shadow(canvas, panel, (160, 1354), radius=22, offset=(0, 10), opacity=0.48)

    canvas.save(out_path_1440, "PNG")
    canvas.resize((1920, 1080), Image.Resampling.LANCZOS).save(out_path_1080, "PNG")
    print(f"Saved {out_path_1440.name}")


def generate_screenshot_03_window_craft(out_path_1440: Path, out_path_1080: Path) -> None:
    print("Generating 03_window_craft_aurorae...")
    wp_path = WALLPAPERS / "2560x1440.png"
    canvas = Image.open(wp_path).convert("RGBA")

    banner = create_header_banner(
        "ARCHITECTURAL WINDOW CRAFT • THE FORGE NOTCH & TABBOX",
        "Signature 18px top-left notch geometry, tactile Aurorae controls & Obsidian KWin switcher"
    )
    canvas.alpha_composite(banner, (0, 0))

    dolphin_inactive = create_dolphin_window(
        width=1120,
        height=720,
        is_active=False,
        is_obsidian=False,
        custom_title="Inactive Window (Graphite) — Dolphin",
    )
    konsole_active = create_konsole_window(
        width=1240,
        height=740,
        is_active=True,
        is_obsidian=True,
        accent=ACCENT_LIME,
        custom_title="Active Window (Obsidian OLED & Forge Notch) — Konsole",
    )
    alt_tab = create_alt_tab_switcher(width=1040, height=300)
    panel = create_plasma_panel(width=2240, height=58)

    add_drop_shadow(canvas, dolphin_inactive, (120, 220), radius=30, offset=(0, 14), opacity=0.48)
    add_drop_shadow(canvas, konsole_active, (960, 180), radius=38, offset=(0, 20), opacity=0.68)
    add_drop_shadow(canvas, alt_tab, (760, 840), radius=44, offset=(0, 26), opacity=0.74)
    add_drop_shadow(canvas, panel, (160, 1354), radius=22, offset=(0, 10), opacity=0.48)

    canvas.save(out_path_1440, "PNG")
    canvas.resize((1920, 1080), Image.Resampling.LANCZOS).save(out_path_1080, "PNG")
    print(f"Saved {out_path_1440.name}")


def generate_screenshot_04_qt6_controls(out_path_1440: Path, out_path_1080: Path) -> None:
    print("Generating 04_system_completeness_qt6 (Control Center & Opacity Hub)...")
    wp_path = WALLPAPERS / "2560x1440.png"
    canvas = Image.open(wp_path).convert("RGBA")

    banner = create_header_banner(
        "UNIFIED CONTROL CENTER & NATIVE QT 6 SUITE",
        "3-Tab PySide6 Control Center, Depth & Opacity configurator, and adaptive Qt 6 style engine"
    )
    canvas.alpha_composite(banner, (0, 0))

    ctrl_window = create_control_center_window(width=1480, height=880, is_active=True)
    panel = create_plasma_panel(width=2240, height=58)

    add_drop_shadow(canvas, ctrl_window, (540, 220), radius=40, offset=(0, 20), opacity=0.68)
    add_drop_shadow(canvas, panel, (160, 1354), radius=22, offset=(0, 10), opacity=0.48)

    canvas.save(out_path_1440, "PNG")
    canvas.resize((1920, 1080), Image.Resampling.LANCZOS).save(out_path_1080, "PNG")
    print(f"Saved {out_path_1440.name}")


def generate_screenshot_05_plasma_launcher(out_path_1440: Path, out_path_1080: Path) -> None:
    print("Generating 05_launcher_and_plasma_shell...")
    wp_path = WALLPAPERS / "2560x1440.png"
    canvas = Image.open(wp_path).convert("RGBA")

    banner = create_header_banner(
        "PLASMA 6 SHELL, KICKOFF LAUNCHER & LOCK SCREEN",
        "Tactile kickoff categories, floating panel geometry, and kinetic Plasma 6 Wayland Lock Screen"
    )
    canvas.alpha_composite(banner, (0, 0))

    dolphin_bg = create_dolphin_window(width=1140, height=720, is_active=False, is_obsidian=False)
    add_drop_shadow(canvas, dolphin_bg, (540, 220), radius=34, offset=(0, 18), opacity=0.50)

    lockscreen = create_lockscreen_card(width=720, height=450)
    add_drop_shadow(canvas, lockscreen, (1640, 240), radius=40, offset=(0, 22), opacity=0.72)

    launcher = create_launcher_window(width=840, height=660)
    add_drop_shadow(canvas, launcher, (160, 660), radius=44, offset=(0, 26), opacity=0.74)

    panel = create_plasma_panel(width=2240, height=58)
    add_drop_shadow(canvas, panel, (160, 1354), radius=22, offset=(0, 10), opacity=0.48)

    canvas.save(out_path_1440, "PNG")
    canvas.resize((1920, 1080), Image.Resampling.LANCZOS).save(out_path_1080, "PNG")
    print(f"Saved {out_path_1440.name}")


def generate_screenshot_06_iconography(out_path_1440: Path, out_path_1080: Path) -> None:
    print("Generating 06_original_iconography...")
    wp_path = WALLPAPERS / "2560x1440.png"
    canvas = Image.open(wp_path).convert("RGBA")

    banner = create_header_banner(
        "ORIGINAL SCALABLE VECTOR ICONOGRAPHY",
        "Clean geometric line artwork with electric-lime and cyan detail accents across all system surfaces"
    )
    canvas.alpha_composite(banner, (0, 0))

    dolphin = create_dolphin_window(width=1200, height=640, is_active=True, is_obsidian=False)
    add_drop_shadow(canvas, dolphin, (90, 220), radius=34, offset=(0, 18), opacity=0.60)

    icon_card = create_icon_palette_card(width=1200, height=440)
    add_drop_shadow(canvas, icon_card, (1270, 220), radius=38, offset=(0, 20), opacity=0.68)

    panel = create_plasma_panel(width=2240, height=58)
    add_drop_shadow(canvas, panel, (160, 1354), radius=22, offset=(0, 10), opacity=0.48)

    canvas.save(out_path_1440, "PNG")
    canvas.resize((1920, 1080), Image.Resampling.LANCZOS).save(out_path_1080, "PNG")
    print(f"Saved {out_path_1440.name}")


def generate_store_hero_banner(out_path_1280: Path, out_path_1920: Path) -> None:
    print("Generating store-hero banner...")
    width, height = 1280, 640
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(BG_GRAPHITE)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    wp = QPixmap(str(WALLPAPERS / "1920x1080.png"))
    p.drawPixmap(QRect(0, 0, width, height), wp, QRect(100, 50, 1720, 860))

    grad = QLinearGradient(0, 0, width, 0)
    grad.setColorAt(0.0, QColor(13, 20, 25, 252))
    grad.setColorAt(0.55, QColor(13, 20, 25, 230))
    grad.setColorAt(1.0, QColor(13, 20, 25, 120))
    p.fillRect(QRect(0, 0, width, height), grad)

    render_svg(p, BRAND / "noxforge-lockup.svg", QRectF(60, 46, 360, 86))

    p.setFont(get_font("Inter", 32, QFont.Weight.ExtraBold))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(64, 144, 600, 48), Qt.AlignmentFlag.AlignVCenter, "DEEP FOCUS")

    p.setFont(get_font("Inter", 12, QFont.Weight.Bold))
    p.setPen(ACCENT_LIME)
    p.drawText(QRectF(64, 196, 600, 26), Qt.AlignmentFlag.AlignVCenter, "KDE PLASMA 6 • EVERYDAY PRECISION VISUAL SYSTEM • v14.0.0")

    features = [
        "✦ Dual Palettes: Refined Graphite (#0D1419) & True Obsidian OLED (#000000)",
        "✦ Forge Accent Matrix: Electric Lime, Forge Cyan, Cyber Violet & Amber",
        "✦ Unified Control Center & Opacity Configurator (PySide6 Hub)",
        "✦ Signature Forge Notch 18px Chamfer Aurorae Window Decorations",
        "✦ 100% Original Scalable Vector Icon Theme & Terminal Ecosystems",
    ]

    p.setFont(get_font("Inter", 11, QFont.Weight.Medium))
    fy = 240
    for feat in features:
        p.setPen(ACCENT_LIME if any(x in feat for x in ["Obsidian", "Forge Accent", "Control Center"]) else TEXT_SECONDARY)
        p.drawText(QRectF(64, fy, 600, 24), Qt.AlignmentFlag.AlignVCenter, feat)
        fy += 28

    # Clean, non-overlapping badges
    badges = ["Plasma 6.7+", "Qt 6.11+", "Wayland", "Fedora 44 / Arch", "MIT License"]
    bx = 64
    for btext in badges:
        bw = 96
        br = QRectF(bx, 420, bw, 28)
        p.setPen(BORDER_STRONG)
        p.setBrush(SURFACE_RAISED)
        p.drawRoundedRect(br, 5, 5)
        p.setFont(get_font("Inter", 8, QFont.Weight.DemiBold))
        p.setPen(ACCENT_LIME if "Plasma" in btext or "v14" in btext else TEXT_PRIMARY)
        p.drawText(br, Qt.AlignmentFlag.AlignCenter, btext)
        bx += bw + 8

    p.end()
    pil_base = qimage_to_pil(img)

    # Mini Konsole fitted cleanly inside frame
    mini_konsole = create_konsole_window(width=600, height=480, is_active=True, is_obsidian=True)
    add_drop_shadow(pil_base, mini_konsole, (630, 80), radius=30, offset=(0, 16), opacity=0.68)

    pil_base.save(out_path_1280, "PNG")
    pil_base.resize((1920, 1080), Image.Resampling.LANCZOS).save(out_path_1920, "PNG")
    print(f"Saved {out_path_1280.name}")


def generate_store_thumbnail_and_icon(out_path_thumb: Path, out_path_icon: Path) -> None:
    print("Generating store thumbnail (s1.png / 480x380) and store-icon (400x400)...")
    w, h = 480, 380
    img = QImage(w, h, QImage.Format.Format_ARGB32_Premultiplied)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    wp = QPixmap(str(WALLPAPERS / "1920x1080.png"))
    p.drawPixmap(QRect(0, 0, w, h), wp, QRect(200, 100, 1500, 1180))

    # Top brand bar
    grad = QLinearGradient(0, 0, 0, 80)
    grad.setColorAt(0.0, QColor(13, 20, 25, 245))
    grad.setColorAt(1.0, QColor(13, 20, 25, 0))
    p.fillRect(QRect(0, 0, w, 80), grad)

    render_svg(p, BRAND / "noxforge-lockup.svg", QRectF(16, 12, 160, 40))

    p.setFont(get_font("Inter", 8, QFont.Weight.Bold))
    p.setPen(ACCENT_LIME)
    p.drawText(QRectF(190, 20, 270, 24), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, "DEEP FOCUS • v14.0.0")

    # Center floating card showcase
    card = QRectF(24, 76, w - 48, h - 130)
    p.setPen(QPen(ACCENT_LIME, 1.5))
    p.setBrush(QColor(10, 15, 19, 248))
    p.drawPath(notched_path(card, radius=8, notch=14))

    # Card Titlebar
    p.fillRect(QRectF(card.left(), card.top(), card.width(), 28), SURFACE_OBSIDIAN_RAISED)
    p.setFont(get_font("Inter", 8, QFont.Weight.Medium))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(card.left() + 20, card.top(), 220, 28), Qt.AlignmentFlag.AlignVCenter, "NoxForge v14.0.0 — Unified Suite")

    # Mini Fastfetch inside card
    mono = get_font("JetBrains Mono", 8)
    mono_b = get_font("JetBrains Mono", 8, QFont.Weight.Bold)

    cx = card.left() + 16
    cy = card.top() + 46

    # Mini mark
    render_svg(p, BRAND / "noxforge-mark.svg", QRectF(cx, cy, 70, 60))

    tx = cx + 84
    p.setFont(mono_b)
    p.setPen(ACCENT_LIME)
    p.drawText(QPointF(tx, cy + 14), "OS      ❯")
    p.setFont(mono)
    p.setPen(TEXT_PRIMARY)
    p.drawText(QPointF(tx + 68, cy + 14), "Fedora 44 (Plasma 6.7)")

    p.setFont(mono_b)
    p.setPen(ACCENT_LIME)
    p.drawText(QPointF(tx, cy + 30), "THEME   ❯")
    p.setFont(mono)
    p.setPen(TEXT_PRIMARY)
    p.drawText(QPointF(tx + 68, cy + 30), "NoxForge Obsidian OLED")

    p.setFont(mono_b)
    p.setPen(ACCENT_LIME)
    p.drawText(QPointF(tx, cy + 46), "DECOR   ❯")
    p.setFont(mono)
    p.setPen(TEXT_PRIMARY)
    p.drawText(QPointF(tx + 68, cy + 46), "Forge Notch 18px")

    # Color dots
    ansi = [ACCENT_LIME, ACCENT_CYAN, ACCENT_VIOLET, ACCENT_AMBER, ALERT_RED]
    for idx, ac in enumerate(ansi):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(ac)
        p.drawRoundedRect(QRectF(tx + idx * 24, cy + 62, 18, 12), 2, 2)

    # Feature badges
    by = card.bottom() - 36
    feats = ["Graphite", "Obsidian OLED", "Control Hub", "Vector Icons"]
    fx = card.left() + 14
    for f in feats:
        fw = (card.width() - 40) / 4
        fr = QRectF(fx, by, fw, 22)
        p.setPen(BORDER_STRONG)
        p.setBrush(SURFACE_RAISED)
        p.drawRoundedRect(fr, 4, 4)
        p.setFont(get_font("Inter", 7, QFont.Weight.DemiBold))
        p.setPen(ACCENT_LIME if "OLED" in f or "Hub" in f else TEXT_PRIMARY)
        p.drawText(fr, Qt.AlignmentFlag.AlignCenter, f)
        fx += fw + 4

    # Bottom dock pill
    dock_r = QRectF(50, h - 38, w - 100, 26)
    p.setPen(BORDER_STRONG)
    p.setBrush(QColor(13, 20, 25, 235))
    p.drawRoundedRect(dock_r, 6, 6)
    render_svg(p, BRAND / "noxforge-mark.svg", QRectF(dock_r.left() + 8, dock_r.top() + 4, 18, 18))
    render_svg(p, ICONS / "places/folder.svg", QRectF(dock_r.left() + 36, dock_r.top() + 4, 18, 18))
    render_svg(p, ICONS / "actions/utilities-terminal.svg", QRectF(dock_r.left() + 64, dock_r.top() + 4, 18, 18))
    render_svg(p, ICONS / "preferences/preferences-system.svg", QRectF(dock_r.left() + 92, dock_r.top() + 4, 18, 18))
    p.setFont(get_font("Inter", 7, QFont.Weight.DemiBold))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(dock_r.right() - 60, dock_r.top(), 50, 26), Qt.AlignmentFlag.AlignCenter, "14:28")

    p.end()
    qimage_to_pil(img).save(out_path_thumb, "PNG")

    # Store Icon (400x400)
    icon_img = QImage(400, 400, QImage.Format.Format_ARGB32_Premultiplied)
    ip = QPainter(icon_img)
    ip.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    ip.fillRect(QRect(0, 0, 400, 400), BG_OBSIDIAN)

    ip.drawPixmap(QRect(0, 0, 400, 400), wp, QRect(300, 200, 800, 800))
    ip.fillRect(QRect(0, 0, 400, 400), QColor(10, 15, 20, 200))

    ip.setPen(QPen(ACCENT_LIME, 2.5))
    ip.drawRect(QRectF(1, 1, 398, 398))

    render_svg(ip, BRAND / "noxforge-mark.svg", QRectF(70, 65, 260, 200))

    ip.setFont(get_font("Inter", 18, QFont.Weight.ExtraBold))
    ip.setPen(TEXT_PRIMARY)
    ip.drawText(QRectF(0, 285, 400, 32), Qt.AlignmentFlag.AlignCenter, "NOXFORGE")

    ip.setFont(get_font("Inter", 10, QFont.Weight.Bold))
    ip.setPen(ACCENT_LIME)
    ip.drawText(QRectF(0, 322, 400, 22), Qt.AlignmentFlag.AlignCenter, "v14.0.0 • PLASMA 6")

    ip.end()
    qimage_to_pil(icon_img).save(out_path_icon, "PNG")
    print(f"Saved {out_path_thumb.name} and {out_path_icon.name}")


def main() -> int:
    MEDIA_STORE.mkdir(parents=True, exist_ok=True)
    v11_media = ROOT / "media/v11"
    v11_media.mkdir(parents=True, exist_ok=True)

    print("--- Starting NoxForge Store Screenshot Generation ---")
    generate_screenshot_01_hero_desktop(
        MEDIA_STORE / "01_hero_desktop_showcase_2560x1440.png",
        MEDIA_STORE / "01_hero_desktop_showcase_1920x1080.png",
    )
    generate_screenshot_02_dual_palettes(
        MEDIA_STORE / "02_dual_palettes_obsidian_2560x1440.png",
        MEDIA_STORE / "02_dual_palettes_obsidian_1920x1080.png",
    )
    generate_screenshot_03_window_craft(
        MEDIA_STORE / "03_window_craft_aurorae_2560x1440.png",
        MEDIA_STORE / "03_window_craft_aurorae_1920x1080.png",
    )
    generate_screenshot_04_qt6_controls(
        MEDIA_STORE / "04_system_completeness_qt6_2560x1440.png",
        MEDIA_STORE / "04_system_completeness_qt6_1920x1080.png",
    )
    generate_screenshot_05_plasma_launcher(
        MEDIA_STORE / "05_launcher_and_plasma_shell_2560x1440.png",
        MEDIA_STORE / "05_launcher_and_plasma_shell_1920x1080.png",
    )
    generate_screenshot_06_iconography(
        MEDIA_STORE / "06_original_iconography_2560x1440.png",
        MEDIA_STORE / "06_original_iconography_1920x1080.png",
    )

    generate_store_hero_banner(
        MEDIA_STORE / "store_hero_banner_1280x640.png",
        MEDIA_STORE / "store_hero_banner_1920x1080.png",
    )
    generate_store_thumbnail_and_icon(
        MEDIA_STORE / "s1_store_thumbnail_480x380.png",
        MEDIA_STORE / "store_icon_400x400.png",
    )

    # Update repository canonical media derivatives
    shutil.copyfile(MEDIA_STORE / "store_hero_banner_1280x640.png", ROOT / "media/store-hero.png")
    shutil.copyfile(MEDIA_STORE / "store_hero_banner_1280x640.png", ROOT / "media/github-social-preview.png")
    shutil.copyfile(MEDIA_STORE / "store_icon_400x400.png", ROOT / "media/store-icon.png")

    # Update look-and-feel package preview
    shutil.copyfile(MEDIA_STORE / "s1_store_thumbnail_480x380.png", ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/previews/preview.png")

    # Update v11 captures directory for backward compatibility
    shutil.copyfile(MEDIA_STORE / "01_hero_desktop_showcase_2560x1440.png", v11_media / "desktop.png")
    shutil.copyfile(MEDIA_STORE / "06_original_iconography_2560x1440.png", v11_media / "dolphin.png")
    shutil.copyfile(MEDIA_STORE / "05_launcher_and_plasma_shell_2560x1440.png", v11_media / "launcher.png")
    shutil.copyfile(MEDIA_STORE / "04_system_completeness_qt6_2560x1440.png", v11_media / "system-settings.png")
    shutil.copyfile(MEDIA_STORE / "03_window_craft_aurorae_2560x1440.png", v11_media / "aurorae-tabbox.png")

    print("--- All Store Screenshots & Gallery Assets Successfully Generated! ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
