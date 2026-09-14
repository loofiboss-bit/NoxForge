#!/usr/bin/env python3
"""Render professional, captivating marketing and gallery screenshots for NoxForge on KDE Store."""

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
BRAND = ROOT / "design/brand"
ICONS = ROOT / "icons/NoxForge/scalable"
AURORAE = ROOT / "aurorae/io.github.loofiboss.noxforge.desktop"

# Palette Tokens
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

ACCENT_LIME = QColor("#A3FF47")
ACCENT_LIME_MUTED = QColor("#71994F")
ACCENT_LIME_SOFT = QColor("#243528")
ACCENT_LIME_PRESSED = QColor("#82D936")
ACCENT_INK = QColor("#0D1419")

DETAIL_CYAN = QColor("#22D3EE")
DETAIL_VIOLET = QColor("#A78BFA")
ALERT_RED = QColor("#FF6B7A")
WARN_YELLOW = QColor("#FBBF24")

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

    p.setPen(QPen(border, 1.0))
    p.drawLine(QPointF(rect.left(), rect.top() + titlebar_height), QPointF(rect.right(), rect.top() + titlebar_height))

    p.setFont(get_font("Inter", 11, QFont.Weight.Medium if is_active else QFont.Weight.Normal))
    p.setPen(TEXT_PRIMARY if is_active else TEXT_SECONDARY)
    title_rect = QRectF(rect.left() + notch + 14, rect.top(), rect.width() - notch - 140, titlebar_height)
    p.drawText(title_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, title)

    btn_y = rect.top() + (titlebar_height - 18) / 2
    right = rect.right() - 14

    # Close button
    close_rect = QRectF(right - 20, btn_y, 18, 18)
    p.setPen(QPen(ALERT_RED if is_active else TEXT_DISABLED, 1.8))
    p.drawLine(QPointF(close_rect.left() + 4, close_rect.top() + 4), QPointF(close_rect.right() - 4, close_rect.bottom() - 4))
    p.drawLine(QPointF(close_rect.left() + 4, close_rect.bottom() - 4), QPointF(close_rect.right() - 4, close_rect.top() + 4))

    # Maximize button
    max_rect = QRectF(right - 44, btn_y, 18, 18)
    p.setPen(QPen(DETAIL_CYAN if is_active else TEXT_DISABLED, 1.6))
    p.drawRoundedRect(QRectF(max_rect.left() + 4, max_rect.top() + 4, 10, 10), 1.5, 1.5)

    # Minimize button
    min_rect = QRectF(right - 68, btn_y, 18, 18)
    p.setPen(QPen(ACCENT_LIME if is_active else TEXT_DISABLED, 1.6))
    p.drawLine(QPointF(min_rect.left() + 4, min_rect.top() + 9), QPointF(min_rect.right() - 4, min_rect.top() + 9))

    p.setClipping(False)
    p.setPen(QPen(border, 1.2))
    p.drawPath(path)

    if is_active:
        notch_path = QPainterPath()
        notch_path.moveTo(rect.left(), rect.top() + notch)
        notch_path.lineTo(rect.left() + notch, rect.top())
        p.setPen(QPen(ACCENT_LIME, 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
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


def add_drop_shadow(base: Image.Image, element: Image.Image, pos: tuple[int, int], radius: int = 24, offset: tuple[int, int] = (0, 14), opacity: float = 0.5) -> None:
    alpha = element.split()[-1]
    shadow_mask = alpha.point(lambda p: int(p * opacity))
    shadow = Image.new("RGBA", element.size, (5, 8, 12, 255))
    padding = radius * 2
    expanded = Image.new("RGBA", (element.width + padding * 2, element.height + padding * 2), (0, 0, 0, 0))
    expanded.paste(shadow, (padding, padding), mask=shadow_mask)
    blurred = expanded.filter(ImageFilter.GaussianBlur(radius))
    
    sx = pos[0] + offset[0] - padding
    sy = pos[1] + offset[1] - padding
    base.alpha_composite(blurred, (sx, sy))
    base.alpha_composite(element, pos)


def create_dolphin_window(width: int = 1080, height: int = 700, is_active: bool = False) -> Image.Image:
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    content = draw_window_frame(p, QRectF(0, 0, width, height), "Projects — Dolphin", is_active=is_active, is_obsidian=False)

    # Breadcrumb toolbar
    tb_h = 42
    tb_rect = QRectF(content.left(), content.top(), content.width(), tb_h)
    p.fillRect(tb_rect, SURFACE_RAISED)
    p.setPen(QPen(BORDER_DEFAULT, 1.0))
    p.drawLine(QPointF(tb_rect.left(), tb_rect.bottom()), QPointF(tb_rect.right(), tb_rect.bottom()))

    # Back / Forward buttons
    p.setFont(get_font("Inter", 13, QFont.Weight.Bold))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(content.left() + 16, content.top(), 20, tb_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter, "‹")
    p.drawText(QRectF(content.left() + 40, content.top(), 20, tb_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter, "›")

    # Path pills
    p.setFont(get_font("Inter", 10, QFont.Weight.Medium))
    path_x = content.left() + 80
    for segment in ["Home", "Projects", "NoxForge"]:
        seg_rect = QRectF(path_x, content.top() + 7, 72, 28)
        p.setPen(BORDER_DEFAULT)
        p.setBrush(SURFACE_GRAPHITE)
        p.drawRoundedRect(seg_rect, 4, 4)
        p.setPen(TEXT_PRIMARY if segment == "NoxForge" else TEXT_SECONDARY)
        p.drawText(seg_rect, Qt.AlignmentFlag.AlignCenter, segment)
        path_x += 80
        p.setPen(TEXT_DISABLED)
        p.drawText(QRectF(path_x - 7, content.top() + 7, 10, 28), Qt.AlignmentFlag.AlignCenter, "›")

    # Search bar on right
    search_rect = QRectF(content.right() - 220, content.top() + 7, 200, 28)
    p.setPen(BORDER_DEFAULT)
    p.setBrush(SURFACE_SUNKEN)
    p.drawRoundedRect(search_rect, 5, 5)
    render_svg(p, ICONS / "actions/system-search.svg", QRectF(search_rect.left() + 8, search_rect.top() + 6, 16, 16))
    p.setFont(get_font("Inter", 9, QFont.Weight.Normal))
    p.setPen(TEXT_DISABLED)
    p.drawText(QRectF(search_rect.left() + 30, search_rect.top(), 160, 28), Qt.AlignmentFlag.AlignVCenter, "Search NoxForge...")

    # Sidebar (Places)
    side_w = 210
    side_rect = QRectF(content.left(), content.top() + tb_h, side_w, content.height() - tb_h - 30)
    p.fillRect(side_rect, SURFACE_SUNKEN)
    p.setPen(QPen(BORDER_DEFAULT, 1.0))
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
            p.setBrush(ACCENT_LIME)
            p.drawRoundedRect(QRectF(item_rect.left(), item_rect.top() + 6, 3, 20), 1.5, 1.5)

        render_svg(p, ICONS / icon, QRectF(item_rect.left() + 12, item_rect.top() + 6, 20, 20))
        p.setFont(get_font("Inter", 10, QFont.Weight.Medium if is_selected else QFont.Weight.Normal))
        p.setPen(ACCENT_LIME if is_selected else (TEXT_PRIMARY if not is_selected else TEXT_SECONDARY))
        p.drawText(QRectF(item_rect.left() + 40, item_rect.top(), 140, 32), Qt.AlignmentFlag.AlignVCenter, name)
        item_y += 36

    # Main Grid Area
    main_rect = QRectF(side_rect.right() + 1, content.top() + tb_h, content.width() - side_w - 1, content.height() - tb_h - 30)
    p.fillRect(main_rect, SURFACE_GRAPHITE)

    folders_and_files = [
        ("aurorae", "places/folder.svg", True, "Directory"),
        ("color-schemes", "places/folder.svg", True, "Directory"),
        ("cursors", "places/folder.svg", True, "Directory"),
        ("design", "places/folder.svg", True, "Directory"),
        ("icons", "places/folder.svg", True, "Directory"),
        ("konsole", "places/folder.svg", True, "Directory"),
        ("plasma", "places/folder.svg", True, "Directory"),
        ("wallpapers", "places/folder.svg", True, "Directory"),
        ("CMakeLists.txt", "mimetypes/text-x-generic.svg", False, "CMake Script"),
        ("DESIGN.md", "mimetypes/text-x-generic.svg", False, "Markdown Spec"),
        ("VERSION", "mimetypes/text-x-generic.svg", False, "Plain Text"),
        ("LICENSE", "mimetypes/text-x-generic.svg", False, "MIT License"),
    ]

    grid_cols = 4
    col_w = (main_rect.width() - 40) / grid_cols
    row_h = 92
    gx = main_rect.left() + 20
    gy = main_rect.top() + 20

    for i, (fname, ficon, is_dir, fdesc) in enumerate(folders_and_files):
        c = i % grid_cols
        r = i // grid_cols
        bx = gx + c * col_w
        by = gy + r * row_h
        card_rect = QRectF(bx + 4, by + 4, col_w - 8, row_h - 8)

        p.setPen(BORDER_DEFAULT)
        p.setBrush(SURFACE_RAISED)
        p.drawRoundedRect(card_rect, 6, 6)

        render_svg(p, ICONS / ficon, QRectF(card_rect.left() + 12, card_rect.top() + (row_h - 8 - 36) / 2, 36, 36))

        p.setFont(get_font("Inter", 10, QFont.Weight.Medium))
        p.setPen(TEXT_PRIMARY)
        p.drawText(QRectF(card_rect.left() + 56, card_rect.top() + 14, card_rect.width() - 60, 20), Qt.AlignmentFlag.AlignVCenter, fname)

        p.setFont(get_font("Inter", 8, QFont.Weight.Normal))
        p.setPen(ACCENT_LIME if is_dir else DETAIL_CYAN)
        p.drawText(QRectF(card_rect.left() + 56, card_rect.top() + 34, card_rect.width() - 60, 16), Qt.AlignmentFlag.AlignVCenter, fdesc)

    # Status Bar
    stat_rect = QRectF(content.left(), content.bottom() - 30, content.width(), 30)
    p.fillRect(stat_rect, SURFACE_SUNKEN)
    p.setPen(QPen(BORDER_DEFAULT, 1.0))
    p.drawLine(QPointF(stat_rect.left(), stat_rect.top()), QPointF(stat_rect.right(), stat_rect.top()))
    p.setFont(get_font("Inter", 9, QFont.Weight.Normal))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(stat_rect.left() + 16, stat_rect.top(), 300, 30), Qt.AlignmentFlag.AlignVCenter, "12 items | 182.4 GiB free")

    slider_rect = QRectF(stat_rect.right() - 140, stat_rect.top() + 13, 100, 4)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(BORDER_STRONG)
    p.drawRoundedRect(slider_rect, 2, 2)
    p.setBrush(ACCENT_LIME)
    p.drawRoundedRect(QRectF(slider_rect.left(), slider_rect.top(), 40, 4), 2, 2)
    p.setBrush(TEXT_PRIMARY)
    p.drawEllipse(QPointF(slider_rect.left() + 40, slider_rect.center().y()), 5, 5)

    p.end()
    return qimage_to_pil(img)


def create_konsole_window(width: int = 1120, height: int = 740, is_active: bool = True, custom_content: str = "fastfetch") -> Image.Image:
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    content = draw_window_frame(p, QRectF(0, 0, width, height), "loofi@fedora: ~/Projects/NoxForge — Konsole", is_active=is_active, is_obsidian=True)

    p.fillRect(content, BG_OBSIDIAN)

    tab_h = 32
    tab_bar = QRectF(content.left(), content.top(), content.width(), tab_h)
    p.fillRect(tab_bar, SURFACE_OBSIDIAN_RAISED)
    p.setPen(QPen(BORDER_OBSIDIAN, 1.0))
    p.drawLine(QPointF(tab_bar.left(), tab_bar.bottom()), QPointF(tab_bar.right(), tab_bar.bottom()))

    tab1 = QRectF(tab_bar.left() + 10, tab_bar.top() + 3, 240, 29)
    p.fillRect(tab1, BG_OBSIDIAN)
    p.setPen(QPen(BORDER_OBSIDIAN, 1.0))
    p.drawRect(tab1)
    p.setPen(QPen(ACCENT_LIME, 2.0))
    p.drawLine(QPointF(tab1.left(), tab1.top() + 1), QPointF(tab1.right(), tab1.top() + 1))

    render_svg(p, ICONS / "actions/utilities-terminal.svg", QRectF(tab1.left() + 10, tab1.top() + 7, 15, 15))
    p.setFont(get_font("Inter", 9, QFont.Weight.Medium))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(tab1.left() + 32, tab1.top(), 200, 29), Qt.AlignmentFlag.AlignVCenter, "loofi@fedora: ~/Projects/NoxForge")

    p.setFont(get_font("Inter", 12, QFont.Weight.Bold))
    p.setPen(TEXT_DISABLED)
    p.drawText(QRectF(tab_bar.left() + 260, tab_bar.top(), 25, 29), Qt.AlignmentFlag.AlignCenter, "+")

    body = QRectF(content.left() + 24, content.top() + tab_h + 20, content.width() - 48, content.height() - tab_h - 40)
    mono_font = get_font("JetBrains Mono", 11)
    mono_bold = get_font("JetBrains Mono", 11, QFont.Weight.Bold)

    y = body.top()

    p.setFont(mono_bold)
    p.setPen(ACCENT_LIME)
    p.drawText(QPointF(body.left(), y), "loofi@fedora")
    p.setPen(TEXT_SECONDARY)
    p.drawText(QPointF(body.left() + 105, y), ":")
    p.setPen(DETAIL_CYAN)
    p.drawText(QPointF(body.left() + 115, y), "~/Projects/NoxForge")
    p.setPen(DETAIL_VIOLET)
    p.drawText(QPointF(body.left() + 300, y), "(feature/v11-deep-focus)")
    p.setPen(TEXT_PRIMARY)
    p.drawText(QPointF(body.left() + 540, y), "$ fastfetch")
    y += 28

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
        ("OS", "Fedora Linux 44 (Plasma Desktop) x86_64"),
        ("Host", "Precision Engineering Workstation"),
        ("Kernel", "Linux 7.2.5-200.fc44.x86_64"),
        ("Uptime", "4 hours, 28 mins"),
        ("Packages", "3586 (rpm), 23 (flatpak)"),
        ("Shell", "zsh 5.9 (x86_64-linux-gnu)"),
        ("Display", "2560x1440 @ 165Hz (Wayland)"),
        ("DE", "KDE Plasma 6.7.5"),
        ("WM", "KWin (Wayland)"),
        ("WM Theme", "NoxForge Deep Focus (Forge Notch)"),
        ("Theme", "NoxForge Obsidian [Qt6 Complete]"),
        ("Icons", "NoxForge Scalable [Original Vector]"),
        ("Terminal", "Konsole (NoxForge Obsidian OLED)"),
        ("Memory", "8.42 GiB / 32.00 GiB (26%)"),
    ]

    logo_x = body.left() + 10
    specs_x = body.left() + 340
    start_y = y

    p.setFont(mono_bold)
    for i, line in enumerate(logo_lines):
        ly = start_y + i * 22
        p.setPen(DETAIL_CYAN if i < 6 else ACCENT_LIME)
        p.drawText(QPointF(logo_x, ly), line)

    for i, (k, v) in enumerate(specs):
        sy = start_y + i * 20
        p.setFont(mono_bold)
        p.setPen(ACCENT_LIME)
        p.drawText(QPointF(specs_x, sy), f"{k:<10}")
        p.setPen(TEXT_SECONDARY)
        p.drawText(QPointF(specs_x + 90, sy), "➜")
        p.setFont(mono_font)
        p.setPen(TEXT_PRIMARY if any(x in v for x in ["Obsidian", "Forge Notch", "Vector"]) else TEXT_SECONDARY)
        p.drawText(QPointF(specs_x + 115, sy), v)

    swatch_y = start_y + len(specs) * 20 + 16
    p.setFont(mono_bold)
    p.setPen(TEXT_DISABLED)
    p.drawText(QPointF(specs_x, swatch_y + 14), "PALETTE   ➜")

    ansi_colors = [
        QColor("#141E25"), QColor("#FF6B7A"), QColor("#A3FF47"), QColor("#FBBF24"),
        QColor("#22D3EE"), QColor("#A78BFA"), QColor("#38BDF8"), QColor("#E8F0F2")
    ]
    for idx, col in enumerate(ansi_colors):
        dot_x = specs_x + 115 + idx * 28
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(col)
        p.drawRoundedRect(QRectF(dot_x, swatch_y + 2, 22, 16), 3, 3)

    y = swatch_y + 44

    p.setFont(mono_bold)
    p.setPen(ACCENT_LIME)
    p.drawText(QPointF(body.left(), y), "loofi@fedora")
    p.setPen(TEXT_SECONDARY)
    p.drawText(QPointF(body.left() + 105, y), ":")
    p.setPen(DETAIL_CYAN)
    p.drawText(QPointF(body.left() + 115, y), "~/Projects/NoxForge")
    p.setPen(DETAIL_VIOLET)
    p.drawText(QPointF(body.left() + 300, y), "(feature/v11-deep-focus)")
    p.setPen(TEXT_PRIMARY)
    p.drawText(QPointF(body.left() + 540, y), "$ git status -s")
    y += 24

    p.setFont(mono_font)
    p.setPen(ACCENT_LIME)
    p.drawText(QPointF(body.left() + 20, y), " M")
    p.setPen(TEXT_PRIMARY)
    p.drawText(QPointF(body.left() + 45, y), "design/tokens.json (Obsidian OLED & high contrast qualified)")
    y += 20

    p.setPen(DETAIL_CYAN)
    p.drawText(QPointF(body.left() + 20, y), " M")
    p.setPen(TEXT_PRIMARY)
    p.drawText(QPointF(body.left() + 45, y), "aurorae/io.github.loofiboss.noxforge.desktop (Forge Notch 18px)")
    y += 20

    p.setPen(ACCENT_LIME)
    p.drawText(QPointF(body.left() + 20, y), " M")
    p.setPen(TEXT_PRIMARY)
    p.drawText(QPointF(body.left() + 45, y), "src/style/noxforgestyle.cpp (Qt 6 native style engine complete)")
    y += 28

    p.setFont(mono_bold)
    p.setPen(ACCENT_LIME)
    p.drawText(QPointF(body.left(), y), "loofi@fedora")
    p.setPen(TEXT_SECONDARY)
    p.drawText(QPointF(body.left() + 105, y), ":")
    p.setPen(DETAIL_CYAN)
    p.drawText(QPointF(body.left() + 115, y), "~/Projects/NoxForge")
    p.setPen(DETAIL_VIOLET)
    p.drawText(QPointF(body.left() + 300, y), "(feature/v11-deep-focus)")
    p.setPen(TEXT_PRIMARY)
    p.drawText(QPointF(body.left() + 540, y), "$ ")
    p.fillRect(QRectF(body.left() + 558, y - 14, 9, 17), ACCENT_LIME)

    p.end()
    return qimage_to_pil(img)


def create_plasma_panel(width: int = 2160, height: int = 56) -> Image.Image:
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    panel_rect = QRectF(0, 0, width, height)
    p.setPen(QPen(BORDER_STRONG, 1.2))
    p.setBrush(QColor(13, 20, 25, 235))
    p.drawRoundedRect(panel_rect, 14, 14)

    render_svg(p, BRAND / "noxforge-mark.svg", QRectF(16, 12, 32, 32))

    tasks = [
        ("Projects", "places/folder.svg", True),
        ("Konsole", "actions/utilities-terminal.svg", True),
        ("Kate", "actions/document-new.svg", False),
        ("Firefox", "categories/applications-internet.svg", False),
        ("Settings", "preferences/preferences-system.svg", False),
    ]

    tx = 68
    for name, icon, is_active in tasks:
        item_w = 120 if is_active else 44
        task_rect = QRectF(tx, 8, item_w, height - 16)
        if is_active:
            p.setPen(BORDER_DEFAULT)
            p.setBrush(SURFACE_RAISED)
            p.drawRoundedRect(task_rect, 8, 8)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(ACCENT_LIME)
            p.drawRoundedRect(QRectF(task_rect.left() + 16, task_rect.bottom() - 3, task_rect.width() - 32, 3), 1.5, 1.5)

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

    rx = width - 20
    p.setPen(QPen(BORDER_STRONG, 1.5))
    p.drawLine(QPointF(rx - 10, 14), QPointF(rx - 10, height - 14))

    rx -= 110
    p.setFont(get_font("Inter", 10, QFont.Weight.DemiBold))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(rx, 8, 90, 20), Qt.AlignmentFlag.AlignCenter, "14:28")
    p.setFont(get_font("Inter", 8, QFont.Weight.Normal))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(rx, 28, 90, 18), Qt.AlignmentFlag.AlignCenter, "Mon, 14 Sep")

    tray_icons = [
        "status/battery-good.svg",
        "status/audio-volume-high.svg",
        "status/network-wireless.svg",
    ]
    rx -= 30
    for ticon in tray_icons:
        rx -= 32
        render_svg(p, ICONS / ticon, QRectF(rx, 17, 22, 22))

    p.end()
    return qimage_to_pil(img)


def create_qt6_gallery_window(width: int = 1040, height: int = 680, is_active: bool = True) -> Image.Image:
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    content = draw_window_frame(p, QRectF(0, 0, width, height), "Qt 6 Native Controls & Style Primitives — NoxForge", is_active=is_active, is_obsidian=False)

    tab_h = 42
    tab_rect = QRectF(content.left(), content.top(), content.width(), tab_h)
    p.fillRect(tab_rect, SURFACE_SUNKEN)
    p.setPen(QPen(BORDER_DEFAULT, 1.0))
    p.drawLine(QPointF(tab_rect.left(), tab_rect.bottom()), QPointF(tab_rect.right(), tab_rect.bottom()))

    tabs = ["Controls", "Data & Views", "Menus & Dialogs", "States & Motion"]
    tx = content.left() + 16
    for i, tname in enumerate(tabs):
        is_sel = (i == 0)
        tw = 130
        tpath = notched_path(QRectF(tx, tab_rect.top() + 6, tw, tab_h - 6), radius=4, notch=10 if is_sel else 0)
        p.setPen(BORDER_STRONG if is_sel else BORDER_DEFAULT)
        p.setBrush(SURFACE_GRAPHITE if is_sel else SURFACE_RAISED)
        p.drawPath(tpath)
        if is_sel:
            p.setPen(QPen(ACCENT_LIME, 2.5))
            p.drawLine(QPointF(tx, tab_rect.top() + 16), QPointF(tx + 10, tab_rect.top() + 6))
        p.setFont(get_font("Inter", 9, QFont.Weight.Medium if is_sel else QFont.Weight.Normal))
        p.setPen(ACCENT_LIME if is_sel else TEXT_SECONDARY)
        p.drawText(QRectF(tx, tab_rect.top() + 6, tw, tab_h - 6), Qt.AlignmentFlag.AlignCenter, tname)
        tx += tw + 10

    body = QRectF(content.left() + 24, content.top() + tab_h + 20, content.width() - 48, content.height() - tab_h - 36)
    left_w = (body.width() - 32) / 2
    right_w = left_w

    lx = body.left()
    ly = body.top()

    p.setFont(get_font("Inter", 10, QFont.Weight.Bold))
    p.setPen(ACCENT_LIME)
    p.drawText(QRectF(lx, ly, left_w, 24), Qt.AlignmentFlag.AlignVCenter, "BUTTONS & ACTIONS")
    ly += 32

    btn_p = QRectF(lx, ly, left_w, 38)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(ACCENT_LIME)
    p.drawRoundedRect(btn_p, 6, 6)
    p.setFont(get_font("Inter", 10, QFont.Weight.Bold))
    p.setPen(ACCENT_INK)
    p.drawText(btn_p, Qt.AlignmentFlag.AlignCenter, "Primary Action (Default Focus)")
    ly += 48

    btn_s = QRectF(lx, ly, left_w / 2 - 6, 36)
    p.setPen(BORDER_STRONG)
    p.setBrush(SURFACE_RAISED)
    p.drawRoundedRect(btn_s, 6, 6)
    p.setFont(get_font("Inter", 9, QFont.Weight.Medium))
    p.setPen(TEXT_PRIMARY)
    p.drawText(btn_s, Qt.AlignmentFlag.AlignCenter, "Secondary")

    btn_d = QRectF(lx + left_w / 2 + 6, ly, left_w / 2 - 6, 36)
    p.setPen(BORDER_DEFAULT)
    p.setBrush(SURFACE_SUNKEN)
    p.drawRoundedRect(btn_d, 6, 6)
    p.setPen(TEXT_DISABLED)
    p.drawText(btn_d, Qt.AlignmentFlag.AlignCenter, "Disabled")
    ly += 54

    p.setFont(get_font("Inter", 10, QFont.Weight.Bold))
    p.setPen(ACCENT_LIME)
    p.drawText(QRectF(lx, ly, left_w, 24), Qt.AlignmentFlag.AlignVCenter, "INPUTS & SELECTIONS")
    ly += 32

    inp_rect = QRectF(lx, ly, left_w, 36)
    p.setPen(QPen(ACCENT_LIME, 1.5))
    p.setBrush(SURFACE_SUNKEN)
    p.drawRoundedRect(inp_rect, 6, 6)
    p.setFont(get_font("Inter", 10, QFont.Weight.Normal))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(inp_rect.left() + 12, inp_rect.top(), inp_rect.width() - 30, 36), Qt.AlignmentFlag.AlignVCenter, "Kinetic Precision Visual Architecture")
    p.fillRect(QRectF(inp_rect.left() + 295, inp_rect.top() + 9, 2, 18), ACCENT_LIME)
    ly += 48

    combo_rect = QRectF(lx, ly, left_w, 36)
    p.setPen(BORDER_STRONG)
    p.setBrush(SURFACE_RAISED)
    p.drawRoundedRect(combo_rect, 6, 6)
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(combo_rect.left() + 12, combo_rect.top(), combo_rect.width() - 40, 36), Qt.AlignmentFlag.AlignVCenter, "Color Variant: Obsidian OLED (True-Black)")
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(combo_rect.right() - 26, combo_rect.top(), 20, 36), Qt.AlignmentFlag.AlignCenter, "▼")
    ly += 52

    p.setFont(get_font("Inter", 9, QFont.Weight.Medium))
    chk1 = QRectF(lx, ly + 2, 18, 18)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(ACCENT_LIME)
    p.drawRoundedRect(chk1, 4, 4)
    p.setPen(QPen(ACCENT_INK, 2.0))
    p.drawLine(QPointF(chk1.left() + 4, chk1.top() + 9), QPointF(chk1.left() + 8, chk1.top() + 13))
    p.drawLine(QPointF(chk1.left() + 8, chk1.top() + 13), QPointF(chk1.left() + 14, chk1.top() + 5))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(lx + 28, ly, 180, 22), Qt.AlignmentFlag.AlignVCenter, "Forge Notch Titlebars")

    rad_x = lx + left_w / 2 + 10
    rad1 = QRectF(rad_x, ly + 2, 18, 18)
    p.setPen(QPen(ACCENT_LIME, 1.8))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(rad1)
    p.setBrush(ACCENT_LIME)
    p.drawEllipse(QPointF(rad1.center().x(), rad1.center().y()), 4.5, 4.5)
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(rad_x + 28, ly, 180, 22), Qt.AlignmentFlag.AlignVCenter, "Hardware Acceleration")
    ly += 42

    p.setFont(get_font("Inter", 9, QFont.Weight.Normal))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(lx, ly, left_w, 18), Qt.AlignmentFlag.AlignVCenter, "Accent Intensity: 85%")
    ly += 22
    sl_rect = QRectF(lx, ly + 6, left_w, 6)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(SURFACE_SUNKEN)
    p.drawRoundedRect(sl_rect, 3, 3)
    p.setBrush(ACCENT_LIME)
    p.drawRoundedRect(QRectF(sl_rect.left(), sl_rect.top(), left_w * 0.85, 6), 3, 3)
    p.setBrush(TEXT_PRIMARY)
    p.drawEllipse(QPointF(sl_rect.left() + left_w * 0.85, sl_rect.center().y()), 8, 8)
    ly += 36

    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(lx, ly, left_w, 18), Qt.AlignmentFlag.AlignVCenter, "Native Style Compilation: 100% Complete")
    ly += 22
    pb_rect = QRectF(lx, ly, left_w, 10)
    p.setBrush(SURFACE_SUNKEN)
    p.drawRoundedRect(pb_rect, 5, 5)
    grad = QLinearGradient(pb_rect.left(), pb_rect.top(), pb_rect.right(), pb_rect.top())
    grad.setColorAt(0.0, DETAIL_CYAN)
    grad.setColorAt(1.0, ACCENT_LIME)
    p.setBrush(grad)
    p.drawRoundedRect(pb_rect, 5, 5)

    # Right Column: System Settings Theme Preview
    rx = body.left() + left_w + 32
    ry = body.top()

    p.setFont(get_font("Inter", 10, QFont.Weight.Bold))
    p.setPen(ACCENT_LIME)
    p.drawText(QRectF(rx, ry, right_w, 24), Qt.AlignmentFlag.AlignVCenter, "KDE SYSTEM INTEGRATION")
    ry += 32

    sett_card = QRectF(rx, ry, right_w, body.height() - 32)
    p.setPen(BORDER_STRONG)
    p.setBrush(SURFACE_SUNKEN)
    p.drawRoundedRect(sett_card, 8, 8)

    p.fillRect(QRectF(sett_card.left(), sett_card.top(), sett_card.width(), 40), SURFACE_RAISED)
    p.setFont(get_font("Inter", 10, QFont.Weight.DemiBold))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(sett_card.left() + 16, sett_card.top(), sett_card.width() - 32, 40), Qt.AlignmentFlag.AlignVCenter, "Appearance > Colors & Themes")

    themes = [
        ("NoxForge Deep Focus (Graphite)", "Original graphite surfaces with electric lime", True),
        ("NoxForge Obsidian (OLED True-Black)", "Zero-power deep black palette for OLED", False),
        ("Breeze Dark (Fallback baseline)", "KDE default dark styling", False),
    ]

    ty = sett_card.top() + 56
    for t_title, t_desc, t_sel in themes:
        t_box = QRectF(sett_card.left() + 16, ty, sett_card.width() - 32, 64)
        p.setPen(QPen(ACCENT_LIME if t_sel else BORDER_DEFAULT, 1.5 if t_sel else 1.0))
        p.setBrush(SURFACE_SELECTED if t_sel else SURFACE_GRAPHITE)
        p.drawRoundedRect(t_box, 6, 6)

        render_svg(p, BRAND / "noxforge-mark.svg", QRectF(t_box.left() + 14, t_box.top() + 14, 36, 36))

        p.setFont(get_font("Inter", 10, QFont.Weight.Bold if t_sel else QFont.Weight.Medium))
        p.setPen(ACCENT_LIME if t_sel else TEXT_PRIMARY)
        p.drawText(QRectF(t_box.left() + 60, t_box.top() + 14, t_box.width() - 120, 20), Qt.AlignmentFlag.AlignVCenter, t_title)

        p.setFont(get_font("Inter", 8, QFont.Weight.Normal))
        p.setPen(TEXT_SECONDARY)
        p.drawText(QRectF(t_box.left() + 60, t_box.top() + 34, t_box.width() - 120, 16), Qt.AlignmentFlag.AlignVCenter, t_desc)

        if t_sel:
            badge_r = QRectF(t_box.right() - 76, t_box.top() + 20, 64, 24)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(ACCENT_LIME)
            p.drawRoundedRect(badge_r, 4, 4)
            p.setFont(get_font("Inter", 8, QFont.Weight.Bold))
            p.setPen(ACCENT_INK)
            p.drawText(badge_r, Qt.AlignmentFlag.AlignCenter, "ACTIVE")

        ty += 76

    app_btn = QRectF(sett_card.right() - 120, sett_card.bottom() - 44, 104, 32)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(ACCENT_LIME)
    p.drawRoundedRect(app_btn, 6, 6)
    p.setFont(get_font("Inter", 9, QFont.Weight.Bold))
    p.setPen(ACCENT_INK)
    p.drawText(app_btn, Qt.AlignmentFlag.AlignCenter, "Apply Theme")

    p.end()
    return qimage_to_pil(img)


def create_launcher_window(width: int = 740, height: int = 580) -> Image.Image:
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    box = QRectF(0, 0, width, height)
    p.setPen(QPen(BORDER_STRONG, 1.2))
    p.setBrush(QColor(16, 25, 31, 250))
    p.drawRoundedRect(box, 12, 12)

    hdr = QRectF(0, 0, width, 56)
    p.fillRect(hdr, SURFACE_RAISED)
    p.setPen(QPen(BORDER_DEFAULT, 1.0))
    p.drawLine(QPointF(hdr.left(), hdr.bottom()), QPointF(hdr.right(), hdr.bottom()))

    avatar_rect = QRectF(18, 10, 36, 36)
    p.setPen(QPen(ACCENT_LIME, 2.0))
    p.setBrush(SURFACE_SUNKEN)
    p.drawEllipse(avatar_rect)
    p.setFont(get_font("Inter", 11, QFont.Weight.Bold))
    p.setPen(ACCENT_LIME)
    p.drawText(avatar_rect, Qt.AlignmentFlag.AlignCenter, "DU")

    p.setFont(get_font("Inter", 11, QFont.Weight.DemiBold))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(64, 10, 200, 36), Qt.AlignmentFlag.AlignVCenter, "Demo User")

    search_r = QRectF(width - 340, 12, 320, 32)
    p.setPen(QPen(ACCENT_LIME, 1.5))
    p.setBrush(SURFACE_SUNKEN)
    p.drawRoundedRect(search_r, 6, 6)
    render_svg(p, ICONS / "actions/system-search.svg", QRectF(search_r.left() + 8, search_r.top() + 7, 18, 18))
    p.setFont(get_font("Inter", 9, QFont.Weight.Normal))
    p.setPen(TEXT_DISABLED)
    p.drawText(QRectF(search_r.left() + 32, search_r.top(), 260, 32), Qt.AlignmentFlag.AlignVCenter, "Search applications, files...")

    cat_w = 200
    cat_rect = QRectF(0, 56, cat_w, height - 56 - 44)
    p.fillRect(cat_rect, SURFACE_SUNKEN)
    p.setPen(QPen(BORDER_DEFAULT, 1.0))
    p.drawLine(QPointF(cat_rect.right(), cat_rect.top()), QPointF(cat_rect.right(), cat_rect.bottom()))

    categories = [
        ("Favorites", "emblems/emblem-favorite.svg", False),
        ("All Applications", "categories/applications-system.svg", False),
        ("Development", "categories/applications-development.svg", True),
        ("Graphics", "categories/applications-graphics.svg", False),
        ("Internet", "categories/applications-internet.svg", False),
        ("Multimedia", "categories/applications-multimedia.svg", False),
        ("System", "preferences/preferences-system.svg", False),
        ("Utilities", "categories/applications-utilities.svg", False),
    ]

    cy = 70
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
        cy += 42

    apps = [
        ("Konsole", "Terminal emulator", "actions/utilities-terminal.svg"),
        ("Dolphin", "File management", "places/folder.svg"),
        ("Kate", "Advanced text editor", "actions/document-new.svg"),
        ("System Settings", "Configuration center", "preferences/preferences-system.svg"),
        ("KDevelop", "IDE workspace", "categories/applications-development.svg"),
        ("Qt Designer", "UI form designer", "categories/applications-development.svg"),
    ]

    ax = cat_w + 20
    ay = 72
    app_w = (width - cat_w - 40) / 2

    for i, (aname, adesc, aicon) in enumerate(apps):
        col = i % 2
        row = i // 2
        cur_x = ax + col * app_w
        cur_y = ay + row * 94
        app_box = QRectF(cur_x, cur_y, app_w - 12, 82)

        p.setPen(BORDER_DEFAULT)
        p.setBrush(SURFACE_RAISED)
        p.drawRoundedRect(app_box, 8, 8)

        render_svg(p, ICONS / aicon, QRectF(app_box.left() + 14, app_box.top() + 21, 40, 40))

        p.setFont(get_font("Inter", 11, QFont.Weight.DemiBold))
        p.setPen(TEXT_PRIMARY)
        p.drawText(QRectF(app_box.left() + 66, app_box.top() + 20, app_box.width() - 72, 22), Qt.AlignmentFlag.AlignVCenter, aname)

        p.setFont(get_font("Inter", 8, QFont.Weight.Normal))
        p.setPen(TEXT_SECONDARY)
        p.drawText(QRectF(app_box.left() + 66, app_box.top() + 42, app_box.width() - 72, 18), Qt.AlignmentFlag.AlignVCenter, adesc)

    ftr = QRectF(0, height - 44, width, 44)
    p.fillRect(ftr, SURFACE_SUNKEN)
    p.setPen(QPen(BORDER_DEFAULT, 1.0))
    p.drawLine(QPointF(ftr.left(), ftr.top()), QPointF(ftr.right(), ftr.top()))

    p.setFont(get_font("Inter", 9, QFont.Weight.Medium))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(20, height - 44, 200, 44), Qt.AlignmentFlag.AlignVCenter, "Session Controls")

    actions = ["Lock", "Sleep", "Restart", "Shut Down"]
    rx = width - 20
    for act in reversed(actions):
        rx -= 80
        p.drawText(QRectF(rx, height - 44, 75, 44), Qt.AlignmentFlag.AlignCenter, act)

    p.end()
    return qimage_to_pil(img)


def create_alt_tab_switcher(width: int = 860, height: int = 260) -> Image.Image:
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    box = QRectF(0, 0, width, height)
    p.setPen(QPen(BORDER_STRONG, 1.5))
    p.setBrush(QColor(13, 20, 25, 245))
    p.drawRoundedRect(box, 14, 14)

    cards = [
        ("Dolphin — Projects", "places/folder.svg", False),
        ("Konsole — fastfetch", "actions/utilities-terminal.svg", True),
        ("System Settings", "preferences/preferences-system.svg", False),
        ("Kate — main.cpp", "actions/document-new.svg", False),
    ]

    card_w = (width - 60) / 4
    for i, (ctitle, cicon, csel) in enumerate(cards):
        cx = 24 + i * (card_w + 4)
        cy = 28
        c_rect = QRectF(cx, cy, card_w - 8, 170)

        cpath = notched_path(c_rect, radius=6, notch=12 if csel else 0)
        p.setPen(QPen(ACCENT_LIME if csel else BORDER_DEFAULT, 2.0 if csel else 1.0))
        p.setBrush(SURFACE_SELECTED if csel else SURFACE_RAISED)
        p.drawPath(cpath)

        if csel:
            p.setPen(QPen(ACCENT_LIME, 2.5))
            p.drawLine(QPointF(c_rect.left(), c_rect.top() + 12), QPointF(c_rect.left() + 12, c_rect.top()))

        thumb = QRectF(c_rect.left() + 12, c_rect.top() + 14, c_rect.width() - 24, 100)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(BG_OBSIDIAN if csel else SURFACE_SUNKEN)
        p.drawRoundedRect(thumb, 4, 4)
        render_svg(p, ICONS / cicon, QRectF(thumb.left() + (thumb.width() - 48) / 2, thumb.top() + (thumb.height() - 48) / 2, 48, 48))

        p.setFont(get_font("Inter", 9, QFont.Weight.DemiBold if csel else QFont.Weight.Medium))
        p.setPen(ACCENT_LIME if csel else TEXT_PRIMARY)
        p.drawText(QRectF(c_rect.left() + 6, c_rect.bottom() - 42, c_rect.width() - 12, 34), Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, ctitle)

    p.setFont(get_font("Inter", 10, QFont.Weight.DemiBold))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(0, height - 36, width, 24), Qt.AlignmentFlag.AlignCenter, "Active Window: Konsole (NoxForge Obsidian)")

    p.end()
    return qimage_to_pil(img)


def create_icon_palette_card(width: int = 1100, height: int = 400) -> Image.Image:
    """Card displaying representative original vector icons categorized with optical scales."""
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    box = QRectF(0, 0, width, height)
    p.setPen(QPen(BORDER_STRONG, 1.2))
    p.setBrush(QColor(16, 25, 31, 240))
    p.drawRoundedRect(box, 12, 12)

    p.fillRect(QRectF(0, 0, width, 44), SURFACE_RAISED)
    p.setPen(QPen(BORDER_DEFAULT, 1.0))
    p.drawLine(QPointF(0, 44), QPointF(width, 44))

    p.setFont(get_font("Inter", 11, QFont.Weight.Bold))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(20, 0, 400, 44), Qt.AlignmentFlag.AlignVCenter, "ORIGINAL VECTOR ICON SET • 16 / 22 / 32 / 48px")

    p.setFont(get_font("Inter", 9, QFont.Weight.DemiBold))
    p.setPen(ACCENT_LIME)
    p.drawText(QRectF(width - 320, 0, 300, 44), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, "Dual-Tone Line Art & Precision Accents")

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
            ("drive-harddisk.svg", "Drive"),
            ("audio-card.svg", "Audio"),
            ("input-keyboard.svg", "Keyboard"),
            ("phone.svg", "Phone"),
        ]),
        ("ACTIONS", [
            ("document-new.svg", "New"),
            ("document-open.svg", "Open"),
            ("document-save.svg", "Save"),
            ("edit-copy.svg", "Copy"),
            ("system-search.svg", "Search"),
        ]),
        ("STATUS", [
            ("network-wireless.svg", "Wireless"),
            ("audio-volume-high.svg", "Volume"),
            ("battery-good.svg", "Battery"),
            ("security-high.svg", "Security"),
            ("dialog-warning.svg", "Warning"),
        ]),
    ]

    gy = 60
    col_w = (width - 40) / len(icon_groups)
    for g_idx, (gname, items) in enumerate(icon_groups):
        gx = 20 + g_idx * col_w
        p.setFont(get_font("Inter", 9, QFont.Weight.Bold))
        p.setPen(DETAIL_CYAN)
        p.drawText(QRectF(gx, gy, col_w, 20), Qt.AlignmentFlag.AlignLeft, gname)

        iy = gy + 26
        for ifile, ilabel in items:
            # Icon row
            i_box = QRectF(gx, iy, col_w - 16, 52)
            p.setPen(BORDER_DEFAULT)
            p.setBrush(SURFACE_GRAPHITE)
            p.drawRoundedRect(i_box, 6, 6)

            full_p = ICONS / f"{gname.lower()}/{ifile}"
            render_svg(p, full_p, QRectF(i_box.left() + 10, i_box.top() + 10, 32, 32))

            p.setFont(get_font("Inter", 10, QFont.Weight.Medium))
            p.setPen(TEXT_PRIMARY)
            p.drawText(QRectF(i_box.left() + 52, i_box.top() + 10, i_box.width() - 60, 18), Qt.AlignmentFlag.AlignVCenter, ilabel)

            p.setFont(get_font("Inter", 8, QFont.Weight.Normal))
            p.setPen(ACCENT_LIME)
            p.drawText(QRectF(i_box.left() + 52, i_box.top() + 28, i_box.width() - 60, 16), Qt.AlignmentFlag.AlignVCenter, "Scalable SVG")

            iy += 58

    p.end()
    return qimage_to_pil(img)


def create_header_banner(title: str, subtitle: str, width: int = 2560) -> Image.Image:
    h = 140
    img = QImage(width, h, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    grad = QLinearGradient(0, 0, 0, h)
    grad.setColorAt(0.0, QColor(9, 14, 18, 230))
    grad.setColorAt(1.0, QColor(9, 14, 18, 0))
    p.fillRect(QRect(0, 0, width, h), grad)

    render_svg(p, BRAND / "noxforge-lockup.svg", QRectF(80, 24, 240, 58))

    p.setFont(get_font("Inter", 26, QFont.Weight.Bold))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(360, 22, width - 400, 36), Qt.AlignmentFlag.AlignVCenter, title)

    p.setFont(get_font("Inter", 13, QFont.Weight.Medium))
    p.setPen(ACCENT_LIME)
    p.drawText(QRectF(360, 60, width - 400, 26), Qt.AlignmentFlag.AlignVCenter, subtitle)

    p.setPen(QPen(ACCENT_LIME, 2.0))
    p.drawLine(QPointF(360, 92), QPointF(520, 92))

    p.end()
    return qimage_to_pil(img)


# -------------------------------------------------------------------------
# Screenshot Composition Generators
# -------------------------------------------------------------------------

def generate_screenshot_01_hero_desktop(out_path_1440: Path, out_path_1080: Path) -> None:
    print("Generating 01_hero_desktop_showcase...")
    wp_path = WALLPAPERS / "2560x1440.png"
    canvas = Image.open(wp_path).convert("RGBA")

    dolphin = create_dolphin_window(width=1160, height=720, is_active=False)
    konsole = create_konsole_window(width=1240, height=780, is_active=True)
    panel = create_plasma_panel(width=2200, height=56)

    add_drop_shadow(canvas, dolphin, (100, 160), radius=32, offset=(0, 16), opacity=0.55)
    add_drop_shadow(canvas, konsole, (1200, 260), radius=36, offset=(0, 20), opacity=0.65)
    add_drop_shadow(canvas, panel, (180, 1360), radius=20, offset=(0, 8), opacity=0.45)

    canvas.save(out_path_1440, "PNG")
    canvas.resize((1920, 1080), Image.Resampling.LANCZOS).save(out_path_1080, "PNG")
    print(f"Saved {out_path_1440.name} and {out_path_1080.name}")


def generate_screenshot_02_dual_palettes(out_path_1440: Path, out_path_1080: Path) -> None:
    print("Generating 02_dual_palettes_obsidian...")
    wp_path = WALLPAPERS / "2560x1440.png"
    canvas = Image.open(wp_path).convert("RGBA")

    banner = create_header_banner(
        "DUAL PALETTE ARCHITECTURE • GRAPHITE & OBSIDIAN OLED",
        "Select your visual balance: refined dark graphite surfaces or pure true-black OLED depth"
    )
    canvas.alpha_composite(banner, (0, 0))

    dolphin_graphite = create_dolphin_window(width=1120, height=840, is_active=True)
    konsole_obsidian = create_konsole_window(width=1120, height=840, is_active=True)

    add_drop_shadow(canvas, dolphin_graphite, (100, 240), radius=32, offset=(0, 16), opacity=0.55)
    add_drop_shadow(canvas, konsole_obsidian, (1320, 240), radius=32, offset=(0, 16), opacity=0.65)

    panel = create_plasma_panel(width=2200, height=56)
    add_drop_shadow(canvas, panel, (180, 1360), radius=20, offset=(0, 8), opacity=0.45)

    canvas.save(out_path_1440, "PNG")
    canvas.resize((1920, 1080), Image.Resampling.LANCZOS).save(out_path_1080, "PNG")
    print(f"Saved {out_path_1440.name}")


def generate_screenshot_03_window_craft(out_path_1440: Path, out_path_1080: Path) -> None:
    print("Generating 03_window_craft_aurorae...")
    wp_path = WALLPAPERS / "2560x1440.png"
    canvas = Image.open(wp_path).convert("RGBA")

    banner = create_header_banner(
        "ARCHITECTURAL WINDOW CRAFT • THE FORGE NOTCH",
        "Signature 18px top-left notch geometry, tactile Aurorae controls & kinetic TabBox switcher"
    )
    canvas.alpha_composite(banner, (0, 0))

    konsole = create_konsole_window(width=1200, height=720, is_active=True)
    alt_tab = create_alt_tab_switcher(width=1000, height=300)
    panel = create_plasma_panel(width=2200, height=56)

    add_drop_shadow(canvas, konsole, (680, 220), radius=32, offset=(0, 16), opacity=0.6)
    add_drop_shadow(canvas, alt_tab, (780, 840), radius=40, offset=(0, 24), opacity=0.7)
    add_drop_shadow(canvas, panel, (180, 1360), radius=20, offset=(0, 8), opacity=0.45)

    canvas.save(out_path_1440, "PNG")
    canvas.resize((1920, 1080), Image.Resampling.LANCZOS).save(out_path_1080, "PNG")
    print(f"Saved {out_path_1440.name}")


def generate_screenshot_04_qt6_controls(out_path_1440: Path, out_path_1080: Path) -> None:
    print("Generating 04_system_completeness_qt6...")
    wp_path = WALLPAPERS / "2560x1440.png"
    canvas = Image.open(wp_path).convert("RGBA")

    banner = create_header_banner(
        "NATIVE QT 6 STYLE & SYSTEM SETTINGS INTEGRATION",
        "Complete visual system primitives: notched tabs, lime action states, custom sliders & high-contrast inputs"
    )
    canvas.alpha_composite(banner, (0, 0))

    qt_window = create_qt6_gallery_window(width=1380, height=840, is_active=True)
    panel = create_plasma_panel(width=2200, height=56)

    add_drop_shadow(canvas, qt_window, (590, 240), radius=36, offset=(0, 18), opacity=0.6)
    add_drop_shadow(canvas, panel, (180, 1360), radius=20, offset=(0, 8), opacity=0.45)

    canvas.save(out_path_1440, "PNG")
    canvas.resize((1920, 1080), Image.Resampling.LANCZOS).save(out_path_1080, "PNG")
    print(f"Saved {out_path_1440.name}")


def generate_screenshot_05_plasma_launcher(out_path_1440: Path, out_path_1080: Path) -> None:
    print("Generating 05_launcher_and_plasma_shell...")
    wp_path = WALLPAPERS / "2560x1440.png"
    canvas = Image.open(wp_path).convert("RGBA")

    banner = create_header_banner(
        "PLASMA 6 SHELL & APPLICATION LAUNCHER",
        "Restrained graphite shell, tactile kickoff categories, and unified system tray popups"
    )
    canvas.alpha_composite(banner, (0, 0))

    konsole = create_konsole_window(width=1300, height=800, is_active=False)
    add_drop_shadow(canvas, konsole, (1000, 240), radius=32, offset=(0, 16), opacity=0.5)

    launcher = create_launcher_window(width=820, height=640)
    add_drop_shadow(canvas, launcher, (180, 680), radius=40, offset=(0, 24), opacity=0.7)

    panel = create_plasma_panel(width=2200, height=56)
    add_drop_shadow(canvas, panel, (180, 1360), radius=20, offset=(0, 8), opacity=0.45)

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

    dolphin = create_dolphin_window(width=1180, height=620, is_active=True)
    add_drop_shadow(canvas, dolphin, (100, 220), radius=32, offset=(0, 16), opacity=0.6)

    icon_card = create_icon_palette_card(width=1160, height=360)
    add_drop_shadow(canvas, icon_card, (1300, 220), radius=36, offset=(0, 18), opacity=0.65)

    panel = create_plasma_panel(width=2200, height=56)
    add_drop_shadow(canvas, panel, (180, 1360), radius=20, offset=(0, 8), opacity=0.45)

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
    grad.setColorAt(0.0, QColor(13, 20, 25, 248))
    grad.setColorAt(0.55, QColor(13, 20, 25, 220))
    grad.setColorAt(1.0, QColor(13, 20, 25, 120))
    p.fillRect(QRect(0, 0, width, height), grad)

    render_svg(p, BRAND / "noxforge-lockup.svg", QRectF(60, 50, 360, 86))

    p.setFont(get_font("Inter", 32, QFont.Weight.ExtraBold))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(64, 150, 600, 48), Qt.AlignmentFlag.AlignVCenter, "DEEP FOCUS")

    p.setFont(get_font("Inter", 13, QFont.Weight.Bold))
    p.setPen(ACCENT_LIME)
    p.drawText(QRectF(64, 202, 600, 26), Qt.AlignmentFlag.AlignVCenter, "KDE PLASMA 6 • EVERYDAY PRECISION VISUAL SYSTEM")

    features = [
        "✦ Dual Palettes: Refined Graphite & Obsidian OLED True-Black",
        "✦ Signature Forge Notch 18px Aurorae Window Decorations",
        "✦ Complete Native Qt 6 Style Primitives & Notched Tabs",
        "✦ 100% Original Scalable Vector Icon Theme with Lime Accents",
        "✦ Matching Konsole Color Schemes & Geometric Wallpapers",
    ]

    p.setFont(get_font("Inter", 11, QFont.Weight.Medium))
    fy = 246
    for feat in features:
        p.setPen(ACCENT_LIME if "Obsidian" in feat or "Forge Notch" in feat else TEXT_SECONDARY)
        p.drawText(QRectF(64, fy, 600, 24), Qt.AlignmentFlag.AlignVCenter, feat)
        fy += 28

    badges = ["Plasma 6.7+", "Qt 6.11+", "Wayland Native", "MIT Licensed"]
    bx = 64
    for btext in badges:
        bw = 105
        br = QRectF(bx, 420, bw, 28)
        p.setPen(BORDER_STRONG)
        p.setBrush(SURFACE_RAISED)
        p.drawRoundedRect(br, 5, 5)
        p.setFont(get_font("Inter", 9, QFont.Weight.DemiBold))
        p.setPen(ACCENT_LIME if "Plasma" in btext else TEXT_PRIMARY)
        p.drawText(br, Qt.AlignmentFlag.AlignCenter, btext)
        bx += bw + 10

    p.end()
    pil_base = qimage_to_pil(img)

    # Mini Konsole fitted perfectly inside frame
    mini_konsole = create_konsole_window(width=620, height=460, is_active=True)
    add_drop_shadow(pil_base, mini_konsole, (620, 90), radius=28, offset=(0, 14), opacity=0.65)

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
    grad.setColorAt(0.0, QColor(13, 20, 25, 240))
    grad.setColorAt(1.0, QColor(13, 20, 25, 0))
    p.fillRect(QRect(0, 0, w, 80), grad)

    render_svg(p, BRAND / "noxforge-lockup.svg", QRectF(16, 12, 160, 40))

    p.setFont(get_font("Inter", 8, QFont.Weight.Bold))
    p.setPen(ACCENT_LIME)
    p.drawText(QRectF(190, 20, 270, 24), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, "DEEP FOCUS • PLASMA 6")

    # Center floating card showcase
    card = QRectF(24, 76, w - 48, h - 130)
    p.setPen(QPen(ACCENT_LIME, 1.5))
    p.setBrush(QColor(10, 15, 19, 245))
    p.drawPath(notched_path(card, radius=8, notch=14))

    # Card Titlebar
    p.fillRect(QRectF(card.left(), card.top(), card.width(), 28), SURFACE_OBSIDIAN_RAISED)
    p.setFont(get_font("Inter", 8, QFont.Weight.Medium))
    p.setPen(TEXT_PRIMARY)
    p.drawText(QRectF(card.left() + 20, card.top(), 200, 28), Qt.AlignmentFlag.AlignVCenter, "Konsole & Dolphin — NoxForge")

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
    p.drawText(QPointF(tx, cy + 14), "OS      ➜")
    p.setFont(mono)
    p.setPen(TEXT_PRIMARY)
    p.drawText(QPointF(tx + 56, cy + 14), "Fedora Linux (Plasma 6.7)")

    p.setFont(mono_b)
    p.setPen(ACCENT_LIME)
    p.drawText(QPointF(tx, cy + 30), "THEME   ➜")
    p.setFont(mono)
    p.setPen(TEXT_PRIMARY)
    p.drawText(QPointF(tx + 56, cy + 30), "NoxForge Obsidian OLED")

    p.setFont(mono_b)
    p.setPen(ACCENT_LIME)
    p.drawText(QPointF(tx, cy + 46), "DECOR   ➜")
    p.setFont(mono)
    p.setPen(TEXT_PRIMARY)
    p.drawText(QPointF(tx + 56, cy + 46), "Forge Notch Aurorae")

    # Color dots
    ansi = [QColor("#FF6B7A"), QColor("#A3FF47"), QColor("#FBBF24"), QColor("#22D3EE"), QColor("#A78BFA")]
    for idx, ac in enumerate(ansi):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(ac)
        p.drawRoundedRect(QRectF(tx + idx * 24, cy + 62, 18, 12), 2, 2)

    # Second row inside card: Feature badges
    by = card.bottom() - 36
    feats = ["Graphite", "Obsidian OLED", "Qt 6 Engine", "Vector Icons"]
    fx = card.left() + 14
    for f in feats:
        fw = (card.width() - 40) / 4
        fr = QRectF(fx, by, fw, 22)
        p.setPen(BORDER_STRONG)
        p.setBrush(SURFACE_RAISED)
        p.drawRoundedRect(fr, 4, 4)
        p.setFont(get_font("Inter", 7, QFont.Weight.DemiBold))
        p.setPen(ACCENT_LIME if "OLED" in f else TEXT_PRIMARY)
        p.drawText(fr, Qt.AlignmentFlag.AlignCenter, f)
        fx += fw + 4

    # Bottom dock pill
    dock_r = QRectF(50, h - 38, w - 100, 26)
    p.setPen(BORDER_STRONG)
    p.setBrush(QColor(13, 20, 25, 230))
    p.drawRoundedRect(dock_r, 6, 6)
    render_svg(p, BRAND / "noxforge-mark.svg", QRectF(dock_r.left() + 8, dock_r.top() + 4, 18, 18))
    render_svg(p, ICONS / "places/folder.svg", QRectF(dock_r.left() + 36, dock_r.top() + 4, 18, 18))
    render_svg(p, ICONS / "actions/utilities-terminal.svg", QRectF(dock_r.left() + 64, dock_r.top() + 4, 18, 18))
    p.setFont(get_font("Inter", 7, QFont.Weight.DemiBold))
    p.setPen(TEXT_SECONDARY)
    p.drawText(QRectF(dock_r.right() - 60, dock_r.top(), 50, 26), Qt.AlignmentFlag.AlignCenter, "14:28")

    p.end()
    qimage_to_pil(img).save(out_path_thumb, "PNG")

    # Store Icon (400x400)
    icon_img = QImage(400, 400, QImage.Format.Format_ARGB32_Premultiplied)
    ip = QPainter(icon_img)
    ip.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    ip.fillRect(QRect(0, 0, 400, 400), BG_GRAPHITE)

    ip.drawPixmap(QRect(0, 0, 400, 400), wp, QRect(300, 200, 800, 800))
    ip.fillRect(QRect(0, 0, 400, 400), QColor(13, 20, 25, 180))

    ip.setPen(QPen(ACCENT_LIME, 2.5))
    ip.drawRect(QRectF(1, 1, 398, 398))

    render_svg(ip, BRAND / "noxforge-mark.svg", QRectF(70, 70, 260, 200))

    ip.setFont(get_font("Inter", 16, QFont.Weight.ExtraBold))
    ip.setPen(TEXT_PRIMARY)
    ip.drawText(QRectF(0, 285, 400, 32), Qt.AlignmentFlag.AlignCenter, "NOXFORGE")

    ip.setFont(get_font("Inter", 10, QFont.Weight.Bold))
    ip.setPen(ACCENT_LIME)
    ip.drawText(QRectF(0, 320, 400, 22), Qt.AlignmentFlag.AlignCenter, "DEEP FOCUS • PLASMA 6")

    ip.end()
    qimage_to_pil(icon_img).save(out_path_icon, "PNG")
    print(f"Saved {out_path_thumb.name} and {out_path_icon.name}")


def main() -> int:
    MEDIA_STORE.mkdir(parents=True, exist_ok=True)
    v11_media = ROOT / "media/v11"
    v11_media.mkdir(parents=True, exist_ok=True)

    print("--- Starting NoxForge Store Screenshot Generation ---")
    generate_screenshot_01_hero_desktop(MEDIA_STORE / "01_hero_desktop_showcase_2560x1440.png", MEDIA_STORE / "01_hero_desktop_showcase_1920x1080.png")
    generate_screenshot_02_dual_palettes(MEDIA_STORE / "02_dual_palettes_obsidian_2560x1440.png", MEDIA_STORE / "02_dual_palettes_obsidian_1920x1080.png")
    generate_screenshot_03_window_craft(MEDIA_STORE / "03_window_craft_aurorae_2560x1440.png", MEDIA_STORE / "03_window_craft_aurorae_1920x1080.png")
    generate_screenshot_04_qt6_controls(MEDIA_STORE / "04_system_completeness_qt6_2560x1440.png", MEDIA_STORE / "04_system_completeness_qt6_1920x1080.png")
    generate_screenshot_05_plasma_launcher(MEDIA_STORE / "05_launcher_and_plasma_shell_2560x1440.png", MEDIA_STORE / "05_launcher_and_plasma_shell_1920x1080.png")
    generate_screenshot_06_iconography(MEDIA_STORE / "06_original_iconography_2560x1440.png", MEDIA_STORE / "06_original_iconography_1920x1080.png")

    generate_store_hero_banner(MEDIA_STORE / "store_hero_banner_1280x640.png", MEDIA_STORE / "store_hero_banner_1920x1080.png")
    generate_store_thumbnail_and_icon(MEDIA_STORE / "s1_store_thumbnail_480x380.png", MEDIA_STORE / "store_icon_400x400.png")

    # Update repository canonical media derivatives
    shutil.copyfile(MEDIA_STORE / "store_hero_banner_1280x640.png", ROOT / "media/store-hero.png")
    shutil.copyfile(MEDIA_STORE / "store_hero_banner_1280x640.png", ROOT / "media/github-social-preview.png")
    shutil.copyfile(MEDIA_STORE / "store_icon_400x400.png", ROOT / "media/store-icon.png")

    # Update look-and-feel preview
    shutil.copyfile(MEDIA_STORE / "s1_store_thumbnail_480x380.png", ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/previews/preview.png")
    shutil.copyfile(MEDIA_STORE / "01_hero_desktop_showcase_1920x1080.png", ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/previews/fullscreenpreview.png")

    # Copy to v11 captures directory
    shutil.copyfile(MEDIA_STORE / "01_hero_desktop_showcase_2560x1440.png", v11_media / "desktop.png")
    shutil.copyfile(MEDIA_STORE / "06_original_iconography_2560x1440.png", v11_media / "dolphin.png")
    shutil.copyfile(MEDIA_STORE / "05_launcher_and_plasma_shell_2560x1440.png", v11_media / "launcher.png")
    shutil.copyfile(MEDIA_STORE / "04_system_completeness_qt6_2560x1440.png", v11_media / "system-settings.png")
    shutil.copyfile(MEDIA_STORE / "03_window_craft_aurorae_2560x1440.png", v11_media / "aurorae-tabbox.png")

    print("--- All Store Screenshots & Gallery Assets Successfully Generated! ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
