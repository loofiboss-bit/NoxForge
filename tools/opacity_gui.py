#!/usr/bin/env python3
"""NoxForge Depth & Transparency Configurator - Qt 6 Graphical Interface.

Provides a modern, high-precision desktop GUI with interactive sliders,
instant preset selection, live 60fps rendering preview, and non-blocking
asynchronous background application.
"""

from __future__ import annotations

import os
import sys
import urllib.parse
from pathlib import Path
from typing import TYPE_CHECKING, Any

from PySide6 import QtCore, QtGui, QtWidgets

if TYPE_CHECKING:
    from tools.noxforge_opacity import OpacityRecipe
else:
    # When imported or executed directly
    try:
        from tools.noxforge_opacity import (
            PRESETS,
            PRESET_DESCRIPTIONS,
            OpacityRecipe,
            apply_opacity,
            clear_cache_and_reload,
            get_status,
        )
    except ImportError:
        # Fallback to local import if run from tools directory
        import importlib.machinery
        import importlib.util

        tool_path = Path(__file__).resolve().parent / "noxforge-opacity"
        loader = importlib.machinery.SourceFileLoader("noxforge_opacity", str(tool_path))
        spec = importlib.util.spec_from_loader("noxforge_opacity", loader)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        sys.modules["noxforge_opacity"] = mod
        spec.loader.exec_module(mod)
        PRESETS = mod.PRESETS
        PRESET_DESCRIPTIONS = mod.PRESET_DESCRIPTIONS
        OpacityRecipe = mod.OpacityRecipe
        apply_opacity = mod.apply_opacity
        clear_cache_and_reload = mod.clear_cache_and_reload
        get_status = mod.get_status

ROOT = Path(__file__).resolve().parents[1]

# NoxForge Everyday Precision QSS
STYLE_SHEET = """
QWidget {
    background-color: #0D1419;
    color: #E8F0F2;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans", sans-serif;
    font-size: 13px;
}

QGroupBox {
    background-color: #141E25;
    border: 1px solid #2F414B;
    border-radius: 6px;
    margin-top: 20px;
    padding: 16px 12px 12px 12px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: #A6B4B9;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QPushButton {
    background-color: #1B2831;
    color: #E8F0F2;
    border: 1px solid #2F414B;
    border-radius: 5px;
    padding: 7px 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #283942;
    border-color: #4B606A;
}

QPushButton:pressed {
    background-color: #10191F;
}

QPushButton:disabled {
    color: #55636A;
    border-color: #1B2831;
}

QPushButton.presetBtn {
    text-align: left;
    padding: 7px 10px;
    font-size: 11px;
    border-radius: 5px;
}

QPushButton.presetBtnActive {
    border: 1px solid #A3FF47;
    background-color: #1A2E20;
    color: #FFFFFF;
}

QPushButton#applyButton {
    background-color: #A3FF47;
    color: #0D1419;
    font-weight: 700;
    font-size: 14px;
    border: none;
    border-radius: 6px;
    padding: 10px 24px;
}

QPushButton#applyButton:hover {
    background-color: #B4FF6B;
}

QPushButton#applyButton:pressed {
    background-color: #82D936;
}

QSlider {
    min-height: 26px;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #10191F;
    border: 1px solid #2F414B;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #A3FF47;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #E8F0F2;
    border: 1px solid #4B606A;
    width: 16px;
    height: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #22D3EE;
    border-color: #22D3EE;
}

QCheckBox {
    spacing: 8px;
    font-size: 12px;
    min-height: 22px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #2F414B;
    border-radius: 3px;
    background-color: #10191F;
}

QCheckBox::indicator:checked {
    background-color: #A3FF47;
    border-color: #A3FF47;
}

QRadioButton {
    spacing: 6px;
    font-size: 12px;
    min-height: 20px;
}

QRadioButton::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #2F414B;
    border-radius: 7px;
    background-color: #10191F;
}

QRadioButton::indicator:checked {
    background-color: #A3FF47;
    border-color: #A3FF47;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    border: none;
    background: #0D1419;
    width: 7px;
    margin: 0px;
    border-radius: 3px;
}

QScrollBar::handle:vertical {
    background: #2F414B;
    min-height: 25px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: #4B606A;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
"""


class ApplyWorker(QtCore.QThread):
    """Background thread to perform SVG opacity modifications and cache reloads."""

    finished = QtCore.Signal(list, list, bool)  # modified_files, reload_actions, is_dry_run
    error = QtCore.Signal(str)

    def __init__(
        self,
        recipe: OpacityRecipe,
        theme_filter: str,
        include_root: bool,
        include_aurorae: bool,
        reload_cache: bool,
        dry_run: bool = False,
    ) -> None:
        super().__init__()
        self.recipe = recipe
        self.theme_filter = theme_filter
        self.include_root = include_root
        self.include_aurorae = include_aurorae
        self.reload_cache = reload_cache
        self.dry_run = dry_run

    def run(self) -> None:
        try:
            modified = apply_opacity(
                recipe=self.recipe,
                theme_filter=self.theme_filter,
                include_root=self.include_root,
                include_aurorae=self.include_aurorae,
                dry_run=self.dry_run,
            )
            reload_actions: list[str] = []
            if self.reload_cache and modified:
                reload_actions = clear_cache_and_reload(dry_run=self.dry_run)
            self.finished.emit(modified, reload_actions, self.dry_run)
        except Exception as exc:
            self.error.emit(str(exc))


def detect_active_plasma_wallpaper() -> Path | None:
    """Detect the active Plasma desktop wallpaper from KDE configuration."""
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    config_dir = Path(xdg_config) if xdg_config else Path.home() / ".config"
    config_path = config_dir / "plasma-org.kde.plasma.desktop-appletsrc"
    if not config_path.is_file():
        return None
    try:
        text = config_path.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("Image="):
                val = line.split("=", 1)[1].strip()
                if val.startswith("file://"):
                    val = urllib.parse.unquote(val[7:])
                elif "%" in val:
                    val = urllib.parse.unquote(val)
                p = Path(val)
                if p.is_file():
                    return p
                if p.is_dir():
                    for sub in (
                        "contents/images/1920x1080.png",
                        "contents/images/1920x1080.jpg",
                        "contents/images/2560x1440.png",
                    ):
                        sub_p = p / sub
                        if sub_p.is_file():
                            return sub_p
    except Exception:
        pass
    return None


class PreviewCanvasWidget(QtWidgets.QWidget):
    """Real-time desktop canvas rendering a simulated Plasma shell and window."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(360, 480)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

        self.panel_opacity = 0.78
        self.dialog_opacity = 0.78
        self.widget_opacity = 0.76
        self.tooltip_opacity = 0.88
        self.aurorae_active = 0.85
        self.aurorae_inactive = 0.75
        self.variant = "graphite"
        self.simulate_blur = True

        self.wallpaper_image: QtGui.QImage | None = None
        self._cached_size: tuple[int, int] | None = None
        self._cached_scaled_wallpaper: QtGui.QImage | None = None
        self._cached_blurred_wallpaper: QtGui.QImage | None = None

        self._load_wallpaper()

    def set_simulate_blur(self, enabled: bool) -> None:
        self.simulate_blur = enabled
        self.update()

    def _load_wallpaper(self) -> None:
        active = detect_active_plasma_wallpaper()
        if active and active.is_file():
            img = QtGui.QImage(str(active))
            if not img.isNull():
                self.wallpaper_image = img
                self._invalidate_cache()
                return

        candidates = [
            ROOT / "wallpapers/NoxForge-Quiet/contents/images/1920x1080.png",
            ROOT / "wallpapers/NoxForge/contents/images/1920x1080.png",
            ROOT / "wallpapers/NoxForge-Obsidian/contents/images/1920x1080.png",
            Path.home() / ".local/share/wallpapers/NoxForge-Quiet/contents/images/1920x1080.png",
            Path("/usr/share/wallpapers/NoxForge-Quiet/contents/images/1920x1080.png"),
            Path("/usr/share/wallpapers/Next/contents/images/1920x1080.png"),
        ]
        for c in candidates:
            if c.is_file():
                img = QtGui.QImage(str(c))
                if not img.isNull():
                    self.wallpaper_image = img
                    self._invalidate_cache()
                    return

    def _invalidate_cache(self) -> None:
        self._cached_size = None
        self._cached_scaled_wallpaper = None
        self._cached_blurred_wallpaper = None

    def update_values(
        self,
        panel: float,
        dialog: float,
        widget: float,
        tooltip: float,
        aurorae_act: float,
        aurorae_inact: float,
        variant: str,
    ) -> None:
        self.panel_opacity = panel
        self.dialog_opacity = dialog
        self.widget_opacity = widget
        self.tooltip_opacity = tooltip
        self.aurorae_active = aurorae_act
        self.aurorae_inactive = aurorae_inact
        self.variant = variant
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)

        w = self.width()
        h = self.height()

        # 1. Background (Wallpaper or Atmospheric Gradient)
        if self.wallpaper_image and not self.wallpaper_image.isNull():
            if self._cached_scaled_wallpaper is None or self._cached_size != (w, h):
                scaled = self.wallpaper_image.scaled(
                    w, h,
                    QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    QtCore.Qt.TransformationMode.SmoothTransformation
                )
                self._cached_size = (w, h)
                # Center crop to exact widget bounds
                sx = max(0, (scaled.width() - w) // 2)
                sy = max(0, (scaled.height() - h) // 2)
                self._cached_scaled_wallpaper = scaled.copy(sx, sy, w, h)

                # Create fast frosted blur on the exact same cropped canvas
                blur_w = max(16, w // 8)
                blur_h = max(16, h // 8)
                small = self._cached_scaled_wallpaper.scaled(
                    blur_w, blur_h,
                    QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
                    QtCore.Qt.TransformationMode.SmoothTransformation
                )
                self._cached_blurred_wallpaper = small.scaled(
                    w, h,
                    QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
                    QtCore.Qt.TransformationMode.SmoothTransformation
                )

            painter.drawImage(0, 0, self._cached_scaled_wallpaper)
        else:
            grad = QtGui.QLinearGradient(0, 0, w, h)
            if self.variant == "obsidian":
                grad.setColorAt(0.0, QtGui.QColor("#000000"))
                grad.setColorAt(1.0, QtGui.QColor("#080D11"))
            else:
                grad.setColorAt(0.0, QtGui.QColor("#0D1419"))
                grad.setColorAt(0.5, QtGui.QColor("#10191F"))
                grad.setColorAt(1.0, QtGui.QColor("#141E25"))
            painter.fillRect(0, 0, w, h, grad)

        # Subtle dark overlay vignette
        painter.fillRect(0, 0, w, h, QtGui.QColor(0, 0, 0, 40))

        # Base surface color according to variant
        surf_rgb = (0, 0, 0) if self.variant == "obsidian" else (20, 30, 37)
        overlay_rgb = (10, 14, 17) if self.variant == "obsidian" else (34, 50, 59)

        def draw_frosted_surface(rect: QtCore.QRect, surf_col: QtGui.QColor, radius: int = 0) -> None:
            if (
                self.simulate_blur
                and self._cached_blurred_wallpaper is not None
                and not self._cached_blurred_wallpaper.isNull()
            ):
                painter.save()
                if radius > 0:
                    path = QtGui.QPainterPath()
                    path.addRoundedRect(QtCore.QRectF(rect), radius, radius)
                    painter.setClipPath(path)
                else:
                    painter.setClipRect(rect)
                painter.drawImage(0, 0, self._cached_blurred_wallpaper)
                painter.restore()

            if radius > 0:
                painter.setBrush(surf_col)
                painter.setPen(QtCore.Qt.PenStyle.NoPen)
                painter.drawRoundedRect(rect, radius, radius)
                painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            else:
                painter.fillRect(rect, surf_col)

        # 2. Window (Aurorae window decoration + client area)
        win_x = 24
        win_y = 28
        win_w = w - 48
        win_h = min(220, h - 180)

        if win_h > 80:
            # Titlebar with Aurorae active opacity
            tb_h = 32
            titlebar_col = QtGui.QColor(*surf_rgb, int(self.aurorae_active * 255))
            tb_rect = QtCore.QRect(win_x, win_y, win_w, tb_h)
            draw_frosted_surface(tb_rect, titlebar_col)

            # Forge Notch (4px corner cut top-left)
            painter.fillRect(QtCore.QRect(win_x, win_y, 4, 1), QtGui.QColor("#4B606A"))
            painter.fillRect(QtCore.QRect(win_x + 6, win_y, 20, 2), QtGui.QColor("#A3FF47"))  # Lime active rail

            # Titlebar Top Edge Highlight
            painter.fillRect(QtCore.QRect(win_x + 4, win_y, win_w - 4, 1), QtGui.QColor(75, 96, 106, 160))

            # Titlebar Text
            painter.setPen(QtGui.QColor("#E8F0F2"))
            font = painter.font()
            font.setPointSize(10)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(win_x + 32, win_y + 20, "Dolphin - Files")

            # Window Buttons (Close, Max, Min)
            btn_r = win_x + win_w - 18
            # Close
            painter.setBrush(QtGui.QColor("#FF6B7A"))
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawEllipse(btn_r - 8, win_y + 11, 10, 10)
            # Maximize
            painter.setBrush(QtGui.QColor("#748289"))
            painter.drawEllipse(btn_r - 26, win_y + 11, 10, 10)
            # Minimize
            painter.drawEllipse(btn_r - 44, win_y + 11, 10, 10)

            # Window Body (Client Area)
            body_col = QtGui.QColor(*surf_rgb, int(min(1.0, self.panel_opacity + 0.1) * 255))
            body_rect = QtCore.QRect(win_x, win_y + tb_h, win_w, win_h - tb_h)
            draw_frosted_surface(body_rect, body_col)

            # Inner subtle content preview
            painter.fillRect(QtCore.QRect(win_x + 12, win_y + tb_h + 12, 70, win_h - tb_h - 24), QtGui.QColor(16, 25, 31, 180))
            painter.setPen(QtGui.QColor("#A6B4B9"))
            font.setPointSize(9)
            font.setBold(False)
            painter.setFont(font)
            painter.drawText(win_x + 20, win_y + tb_h + 32, "Home")
            painter.drawText(win_x + 20, win_y + tb_h + 52, "Documents")
            painter.drawText(win_x + 20, win_y + tb_h + 72, "Downloads")

            # Active selection item with lime marker
            painter.fillRect(QtCore.QRect(win_x + 12, win_y + tb_h + 20, 2, 16), QtGui.QColor("#A3FF47"))

        # 3. Application Launcher Popup Dialog (Translucent Overlay)
        popup_w = min(190, int(w * 0.52))
        popup_h = min(170, int(h * 0.40))
        popup_x = 24
        popup_y = h - 56 - popup_h - 10

        if popup_y > 40:
            popup_col = QtGui.QColor(*overlay_rgb, int(self.dialog_opacity * 255))
            popup_rect = QtCore.QRect(popup_x, popup_y, popup_w, popup_h)
            draw_frosted_surface(popup_rect, popup_col)

            # Forge Notch on popup dialog (top-left)
            painter.fillRect(QtCore.QRect(popup_x, popup_y, 4, 1), QtGui.QColor("#4B606A"))
            # Outer 1px edge highlight
            painter.setPen(QtGui.QColor(75, 96, 106, int(0.72 * 255)))
            painter.drawRect(popup_rect)

            # Search bar in popup
            search_rect = QtCore.QRect(popup_x + 10, popup_y + 10, popup_w - 20, 24)
            painter.fillRect(search_rect, QtGui.QColor(16, 25, 31, int(self.widget_opacity * 255)))
            painter.setPen(QtGui.QColor(75, 96, 106, 120))
            painter.drawRect(search_rect)
            painter.setPen(QtGui.QColor("#748289"))
            font.setPointSize(8)
            painter.setFont(font)
            painter.drawText(popup_x + 18, popup_y + 26, "Search apps...")

            # Menu entries in popup
            entries = ["Terminal", "System Settings", "Text Editor"]
            for idx, item in enumerate(entries):
                ey = popup_y + 44 + idx * 24
                if idx == 0:
                    # Hover item with lime bar
                    painter.fillRect(QtCore.QRect(popup_x + 8, ey - 2, popup_w - 16, 22), QtGui.QColor(40, 57, 66, 140))
                    painter.fillRect(QtCore.QRect(popup_x + 8, ey - 2, 2, 22), QtGui.QColor("#A3FF47"))
                    painter.setPen(QtGui.QColor("#E8F0F2"))
                else:
                    painter.setPen(QtGui.QColor("#A6B4B9"))
                painter.drawText(popup_x + 18, ey + 13, item)

        # 4. Floating Tooltip
        tip_x = w - 150
        tip_y = h - 140
        tip_w = 126
        tip_h = 32
        tip_col = QtGui.QColor(*overlay_rgb, int(self.tooltip_opacity * 255))
        tip_rect = QtCore.QRect(tip_x, tip_y, tip_w, tip_h)
        draw_frosted_surface(tip_rect, tip_col)
        painter.setPen(QtGui.QColor(75, 96, 106, 200))
        painter.drawRect(tip_rect)
        painter.setPen(QtGui.QColor("#E8F0F2"))
        font.setPointSize(9)
        painter.setFont(font)
        painter.drawText(tip_x + 10, tip_y + 20, "NoxForge Precision")

        # 5. Plasma Panel at Bottom
        panel_h = 44
        panel_y = h - panel_h - 10
        panel_x = 16
        panel_w = w - 32
        panel_rect = QtCore.QRect(panel_x, panel_y, panel_w, panel_h)

        panel_col = QtGui.QColor(*surf_rgb, int(self.panel_opacity * 255))
        draw_frosted_surface(panel_rect, panel_col, radius=6)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.setPen(QtGui.QColor(75, 96, 106, int(0.72 * 255)))
        painter.drawRoundedRect(panel_rect, 6, 6)

        # Launcher button on panel (Forge icon)
        painter.fillRect(QtCore.QRect(panel_x + 10, panel_y + 10, 24, 24), QtGui.QColor(27, 40, 49, 200))
        painter.setPen(QtGui.QColor("#A3FF47"))
        painter.setBrush(QtGui.QColor("#A3FF47"))
        painter.drawPolygon([
            QtCore.QPoint(panel_x + 14, panel_y + 14),
            QtCore.QPoint(panel_x + 30, panel_y + 14),
            QtCore.QPoint(panel_x + 22, panel_y + 30),
        ])

        # Active task on panel
        task_w = 110
        painter.fillRect(QtCore.QRect(panel_x + 44, panel_y + 8, task_w, 28), QtGui.QColor(27, 40, 49, 160))
        painter.fillRect(QtCore.QRect(panel_x + 44, panel_y + panel_h - 2, task_w, 2), QtGui.QColor("#A3FF47"))  # Lime bottom rail
        painter.setPen(QtGui.QColor("#E8F0F2"))
        font.setPointSize(9)
        painter.setFont(font)
        painter.drawText(panel_x + 52, panel_y + 26, "Dolphin")

        # Clock on panel right
        painter.setPen(QtGui.QColor("#A6B4B9"))
        painter.drawText(panel_x + panel_w - 56, panel_y + 26, "13:37")


class OpacityConfiguratorWindow(QtWidgets.QMainWindow):
    """Main window for the NoxForge Depth & Transparency Configurator."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("NoxForge Depth & Opacity Configurator")
        self.resize(920, 680)
        self.setMinimumSize(820, 540)
        self.setStyleSheet(STYLE_SHEET)

        mark_path = ROOT / "kwin/tabbox/io.github.loofiboss.noxforge.desktop/contents/ui/NoxForgeMark.svg"
        if mark_path.is_file():
            self.setWindowIcon(QtGui.QIcon(str(mark_path)))

        self.worker: ApplyWorker | None = None
        self.preset_buttons: dict[str, QtWidgets.QPushButton] = {}

        self._build_ui()
        self._load_current_status()

    def _build_ui(self) -> None:
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # ----------------- Left Panel: Controls with Scrolling -----------------
        left_panel = QtWidgets.QWidget()
        left_panel_layout = QtWidgets.QVBoxLayout(left_panel)
        left_panel_layout.setContentsMargins(0, 0, 0, 0)
        left_panel_layout.setSpacing(10)

        # Fixed Header (Title + Re-check)
        title_box = QtWidgets.QHBoxLayout()
        header_vbox = QtWidgets.QVBoxLayout()
        header_vbox.setSpacing(2)
        title_lbl = QtWidgets.QLabel("NOXFORGE // DEPTH & OPACITY")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: 800; color: #A3FF47; letter-spacing: 1px;")
        sub_lbl = QtWidgets.QLabel("Surface Transparency Configurator - KDE Plasma 6")
        sub_lbl.setStyleSheet("font-size: 11px; color: #A6B4B9;")
        header_vbox.addWidget(title_lbl)
        header_vbox.addWidget(sub_lbl)
        title_box.addLayout(header_vbox)
        title_box.addStretch()

        self.btn_refresh = QtWidgets.QPushButton("Re-check")
        self.btn_refresh.setToolTip("Re-read current theme opacity values from disk")
        self.btn_refresh.clicked.connect(self._load_current_status)
        title_box.addWidget(self.btn_refresh)

        left_panel_layout.addLayout(title_box)

        # Scrollable Configuration Controls
        left_scroll = QtWidgets.QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        left_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 4, 8, 4)
        scroll_layout.setSpacing(12)

        # Palette Variant Switcher
        var_group = QtWidgets.QGroupBox("Palette Target")
        var_layout = QtWidgets.QHBoxLayout(var_group)
        self.radio_graphite = QtWidgets.QRadioButton("Graphite")
        self.radio_obsidian = QtWidgets.QRadioButton("Obsidian OLED")
        self.radio_all = QtWidgets.QRadioButton("Both (Synchronized)")
        self.radio_all.setChecked(True)
        var_layout.addWidget(self.radio_all)
        var_layout.addWidget(self.radio_graphite)
        var_layout.addWidget(self.radio_obsidian)
        self.radio_graphite.toggled.connect(self._on_variant_changed)
        self.radio_obsidian.toggled.connect(self._on_variant_changed)
        self.radio_all.toggled.connect(self._on_variant_changed)
        scroll_layout.addWidget(var_group)

        # Preset Profiles Group
        preset_group = QtWidgets.QGroupBox("Quick Presets")
        preset_layout = QtWidgets.QVBoxLayout(preset_group)
        preset_layout.setSpacing(6)

        for p_key, p_desc in PRESET_DESCRIPTIONS.items():
            btn = QtWidgets.QPushButton(p_desc)
            btn.setProperty("class", "presetBtn")
            btn.clicked.connect(lambda checked=False, k=p_key: self._on_preset_clicked(k))
            preset_layout.addWidget(btn)
            self.preset_buttons[p_key] = btn
        scroll_layout.addWidget(preset_group)

        # Fine-Tuning Sliders Group
        slider_group = QtWidgets.QGroupBox("Precision Sliders")
        slider_layout = QtWidgets.QVBoxLayout(slider_group)
        slider_layout.setSpacing(8)

        # Helper to create a slider with percentage badge inside a guaranteed-height container
        def make_slider_row(
            label_text: str, default_val: int, target_layout: QtWidgets.QLayout
        ) -> tuple[QtWidgets.QSlider, QtWidgets.QLabel]:
            row_w = QtWidgets.QWidget()
            row_w.setMinimumHeight(28)
            row = QtWidgets.QHBoxLayout(row_w)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(8)
            lbl = QtWidgets.QLabel(label_text)
            lbl.setFixedWidth(130)
            slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            slider.setRange(10, 100)
            slider.setValue(default_val)
            slider.setMinimumHeight(24)
            val_lbl = QtWidgets.QLabel(f"{default_val}%")
            val_lbl.setFixedWidth(40)
            val_lbl.setStyleSheet("font-weight: 700; color: #A3FF47;")
            slider.valueChanged.connect(lambda v: val_lbl.setText(f"{v}%"))
            slider.valueChanged.connect(self._on_slider_changed)
            row.addWidget(lbl)
            row.addWidget(slider)
            row.addWidget(val_lbl)
            target_layout.addWidget(row_w)
            return slider, val_lbl

        self.slider_panel, self.val_panel = make_slider_row("Panel:", 78, slider_layout)
        self.slider_dialog, self.val_dialog = make_slider_row("Dialogs & Menus:", 78, slider_layout)
        self.slider_widget, self.val_widget = make_slider_row("Widgets & Popups:", 76, slider_layout)
        self.slider_tooltip, self.val_tooltip = make_slider_row("Tooltips:", 88, slider_layout)

        # Aurorae Window Decorations Checkbox & Sliders
        self.chk_aurorae = QtWidgets.QCheckBox("Enable Titlebar Transparency (Aurorae)")
        self.chk_aurorae.setChecked(False)
        self.chk_aurorae.toggled.connect(self._on_aurorae_toggled)
        slider_layout.addWidget(self.chk_aurorae)

        self.aurorae_container = QtWidgets.QWidget()
        aur_layout = QtWidgets.QVBoxLayout(self.aurorae_container)
        aur_layout.setContentsMargins(16, 2, 0, 2)
        aur_layout.setSpacing(6)
        self.slider_aurorae_act, self.val_aurorae_act = make_slider_row("Active Titlebar:", 85, aur_layout)
        self.slider_aurorae_inact, self.val_aurorae_inact = make_slider_row("Inactive Titlebar:", 75, aur_layout)
        self.aurorae_container.setEnabled(False)
        self.aurorae_container.setVisible(False)
        slider_layout.addWidget(self.aurorae_container)

        # Additional Options
        self.chk_include_root = QtWidgets.QCheckBox("Apply to root panel/dialog SVGs (fallback support)")
        self.chk_include_root.setChecked(True)
        self.chk_reload = QtWidgets.QCheckBox("Automatically refresh Plasma shell & KWin")
        self.chk_reload.setChecked(True)
        self.chk_dry_run = QtWidgets.QCheckBox("Dry-run simulation (preview without writing)")
        self.chk_dry_run.setChecked(False)
        slider_layout.addWidget(self.chk_include_root)
        slider_layout.addWidget(self.chk_reload)
        slider_layout.addWidget(self.chk_dry_run)

        scroll_layout.addWidget(slider_group)

        # Blur Tips Banner
        blur_tip = QtWidgets.QFrame()
        blur_tip.setStyleSheet("background-color: #10191F; border: 1px solid #2F414B; border-radius: 5px;")
        blur_layout = QtWidgets.QHBoxLayout(blur_tip)
        blur_layout.setContentsMargins(10, 6, 10, 6)
        tip_text = QtWidgets.QLabel("Tip: Enable <b>Blur</b> in KDE Desktop Effects for frosted glass depth.")
        tip_text.setStyleSheet("font-size: 11px; color: #A6B4B9;")
        btn_effects = QtWidgets.QPushButton("KDE Effects...")
        btn_effects.setStyleSheet("font-size: 11px; padding: 4px 10px; background-color: #141E25;")
        btn_effects.clicked.connect(self._open_kde_effects)
        btn_restart = QtWidgets.QPushButton("Restart Shell...")
        btn_restart.setStyleSheet("font-size: 11px; padding: 4px 10px; background-color: #141E25;")
        btn_restart.setToolTip("Restart the Plasma desktop shell session safely")
        btn_restart.clicked.connect(self._restart_plasma_shell)
        blur_layout.addWidget(tip_text)
        blur_layout.addStretch()
        blur_layout.addWidget(btn_effects)
        blur_layout.addWidget(btn_restart)
        scroll_layout.addWidget(blur_tip)

        scroll_layout.addStretch()
        left_scroll.setWidget(scroll_content)
        left_panel_layout.addWidget(left_scroll, 1)

        # Action Buttons (Fixed Footer at Bottom)
        footer_widget = QtWidgets.QWidget()
        footer_layout = QtWidgets.QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(0, 4, 0, 0)
        footer_layout.setSpacing(6)

        action_layout = QtWidgets.QHBoxLayout()
        self.btn_reset = QtWidgets.QPushButton("Reset Defaults")
        self.btn_reset.clicked.connect(self._on_reset_clicked)

        self.btn_apply = QtWidgets.QPushButton("Apply Transparency")
        self.btn_apply.setObjectName("applyButton")
        self.btn_apply.clicked.connect(self._on_apply_clicked)

        action_layout.addWidget(self.btn_reset)
        action_layout.addStretch()
        action_layout.addWidget(self.btn_apply)
        footer_layout.addLayout(action_layout)

        # Status Message Label
        self.status_lbl = QtWidgets.QLabel("")
        self.status_lbl.setStyleSheet("font-size: 12px; color: #22D3EE; min-height: 18px;")
        footer_layout.addWidget(self.status_lbl)

        left_panel_layout.addWidget(footer_widget)

        # ----------------- Right Panel: Live Preview -----------------
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        self.preview_canvas = PreviewCanvasWidget(self)

        preview_header = QtWidgets.QHBoxLayout()
        preview_title = QtWidgets.QLabel("LIVE DESKTOP PREVIEW")
        preview_title.setStyleSheet("font-size: 12px; font-weight: 700; color: #A6B4B9; letter-spacing: 0.5px;")

        self.chk_simulate_blur = QtWidgets.QCheckBox("Simulate KWin Blur")
        self.chk_simulate_blur.setStyleSheet("font-size: 11px; color: #A6B4B9;")
        self.chk_simulate_blur.setChecked(True)
        self.chk_simulate_blur.toggled.connect(self.preview_canvas.set_simulate_blur)

        self.btn_refresh_wallpaper = QtWidgets.QPushButton("Reload BG")
        self.btn_refresh_wallpaper.setStyleSheet("font-size: 11px; padding: 3px 8px; background-color: #141E25;")
        self.btn_refresh_wallpaper.setToolTip("Reload active desktop wallpaper image")
        self.btn_refresh_wallpaper.clicked.connect(self._on_reload_wallpaper)

        self.preview_badge = QtWidgets.QLabel("78% Frost (Recommended)")
        self.preview_badge.setStyleSheet(
            "background-color: #1A2E20; color: #A3FF47; border: 1px solid #A3FF47; "
            "border-radius: 3px; padding: 2px 6px; font-size: 11px; font-weight: 700;"
        )
        preview_header.addWidget(preview_title)
        preview_header.addStretch()
        preview_header.addWidget(self.chk_simulate_blur)
        preview_header.addWidget(self.btn_refresh_wallpaper)
        preview_header.addWidget(self.preview_badge)
        right_layout.addLayout(preview_header)
        right_layout.addWidget(self.preview_canvas)

        # Assemble Panels
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_widget, 1)

        # Global Shortcuts
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+S"), self, self._on_apply_clicked)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Return"), self, self._on_apply_clicked)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+R"), self, self._on_reset_clicked)
        QtGui.QShortcut(QtGui.QKeySequence("Escape"), self, self.close)

    def _load_current_status(self) -> None:
        """Query installed themes and sync slider values."""
        try:
            status = get_status()
            themes = status.get("themes", {})
            for t_info in themes.values():
                files = t_info.get("files", {})
                if "panel" in files and files["panel"].get("opacity") is not None:
                    op = files["panel"]["opacity"]
                    self.slider_panel.setValue(int(round(op * 100)))
                if "dialog" in files and files["dialog"].get("opacity") is not None:
                    op = files["dialog"]["opacity"]
                    self.slider_dialog.setValue(int(round(op * 100)))
                if "widget" in files and files["widget"].get("opacity") is not None:
                    op = files["widget"]["opacity"]
                    self.slider_widget.setValue(int(round(op * 100)))
                if "tooltip" in files and files["tooltip"].get("opacity") is not None:
                    op = files["tooltip"]["opacity"]
                    self.slider_tooltip.setValue(int(round(op * 100)))
                break
        except Exception:
            pass
        self._highlight_active_preset()
        self._sync_preview()

    def _on_variant_changed(self) -> None:
        self._sync_preview()

    def _on_aurorae_toggled(self, checked: bool) -> None:
        self.aurorae_container.setEnabled(checked)
        self.aurorae_container.setVisible(checked)
        self._sync_preview()

    def _on_preset_clicked(self, preset_name: str) -> None:
        recipe = OpacityRecipe.from_preset(preset_name)
        # Block signals temporarily to prevent redundant updates
        self.slider_panel.blockSignals(True)
        self.slider_dialog.blockSignals(True)
        self.slider_widget.blockSignals(True)
        self.slider_tooltip.blockSignals(True)
        self.slider_aurorae_act.blockSignals(True)
        self.slider_aurorae_inact.blockSignals(True)

        self.slider_panel.setValue(int(round(recipe.panel * 100)))
        self.slider_dialog.setValue(int(round(recipe.dialog * 100)))
        self.slider_widget.setValue(int(round(recipe.widget * 100)))
        self.slider_tooltip.setValue(int(round(recipe.tooltip * 100)))
        self.slider_aurorae_act.setValue(int(round(recipe.aurorae_active * 100)))
        self.slider_aurorae_inact.setValue(int(round(recipe.aurorae_inactive * 100)))

        self.val_panel.setText(f"{self.slider_panel.value()}%")
        self.val_dialog.setText(f"{self.slider_dialog.value()}%")
        self.val_widget.setText(f"{self.slider_widget.value()}%")
        self.val_tooltip.setText(f"{self.slider_tooltip.value()}%")
        self.val_aurorae_act.setText(f"{self.slider_aurorae_act.value()}%")
        self.val_aurorae_inact.setText(f"{self.slider_aurorae_inact.value()}%")

        self.slider_panel.blockSignals(False)
        self.slider_dialog.blockSignals(False)
        self.slider_widget.blockSignals(False)
        self.slider_tooltip.blockSignals(False)
        self.slider_aurorae_act.blockSignals(False)
        self.slider_aurorae_inact.blockSignals(False)

        self._highlight_active_preset(preset_name)
        self._sync_preview()

    def _on_slider_changed(self) -> None:
        self._highlight_active_preset(None)
        self._sync_preview()

    def _highlight_active_preset(self, active_key: str | None = None) -> None:
        current_panel = self.slider_panel.value()
        for key, btn in self.preset_buttons.items():
            preset_val = int(round(PRESETS[key]["panel"] * 100))
            is_active = (active_key == key) or (active_key is None and current_panel == preset_val)
            if is_active:
                btn.setStyleSheet("border: 1px solid #A3FF47; background-color: #1A2E20; color: #FFFFFF;")
            else:
                btn.setStyleSheet("")

    def _sync_preview(self) -> None:
        variant = "obsidian" if self.radio_obsidian.isChecked() else "graphite"
        p_op = self.slider_panel.value() / 100.0
        d_op = self.slider_dialog.value() / 100.0
        w_op = self.slider_widget.value() / 100.0
        t_op = self.slider_tooltip.value() / 100.0
        a_act = (self.slider_aurorae_act.value() / 100.0) if self.chk_aurorae.isChecked() else 1.0
        a_inact = (self.slider_aurorae_inact.value() / 100.0) if self.chk_aurorae.isChecked() else 0.9

        # Identify if current settings match a preset exactly
        matched_preset = None
        for p_key, p_vals in PRESETS.items():
            if (
                self.slider_panel.value() == int(round(p_vals["panel"] * 100))
                and self.slider_dialog.value() == int(round(p_vals["dialog"] * 100))
                and self.slider_widget.value() == int(round(p_vals["widget"] * 100))
                and self.slider_tooltip.value() == int(round(p_vals["tooltip"] * 100))
            ):
                matched_preset = p_key
                break

        if matched_preset == "frost":
            self.preview_badge.setText("78% Frost (Recommended)")
            self.preview_badge.setStyleSheet(
                "background-color: #1A2E20; color: #A3FF47; border: 1px solid #A3FF47; "
                "border-radius: 3px; padding: 2px 6px; font-size: 11px; font-weight: 700;"
            )
        elif matched_preset:
            self.preview_badge.setText(f"{self.slider_panel.value()}% {matched_preset.capitalize()}")
            self.preview_badge.setStyleSheet(
                "background-color: #16242C; color: #22D3EE; border: 1px solid #22D3EE; "
                "border-radius: 3px; padding: 2px 6px; font-size: 11px; font-weight: 700;"
            )
        else:
            self.preview_badge.setText(f"Custom ({self.slider_panel.value()}%)")
            self.preview_badge.setStyleSheet(
                "background-color: #262016; color: #F59E0B; border: 1px solid #F59E0B; "
                "border-radius: 3px; padding: 2px 6px; font-size: 11px; font-weight: 700;"
            )

        self.preview_canvas.update_values(p_op, d_op, w_op, t_op, a_act, a_inact, variant)

    def _on_reset_clicked(self) -> None:
        self._on_preset_clicked("original")
        self.status_lbl.setText("Reset sliders to original factory defaults.")

    def _on_reload_wallpaper(self) -> None:
        self.preview_canvas._load_wallpaper()
        self.preview_canvas.update()
        self.status_lbl.setText("Reloaded desktop background wallpaper.")

    def _restart_plasma_shell(self) -> None:
        reply = QtWidgets.QMessageBox.question(
            self,
            "Restart Plasma Shell",
            "This will clear the theme cache and restart the Plasma shell session in-place. Proceed?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No,
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            import subprocess
            try:
                clear_cache_and_reload()
                subprocess.Popen(["systemctl", "--user", "restart", "plasma-plasmashell"])
                self.status_lbl.setText("Plasma Shell restart command dispatched.")
            except Exception as exc:
                self.status_lbl.setText(f"Could not restart shell: {exc}")

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self.worker and self.worker.isRunning():
            self.status_lbl.setText("Waiting for pending theme write to complete...")
            self.worker.wait(5000)
            if self.worker.isRunning():
                event.ignore()
                return
        event.accept()

    def _on_apply_clicked(self) -> None:
        if self.worker and self.worker.isRunning():
            return
        recipe = OpacityRecipe(
            panel=self.slider_panel.value() / 100.0,
            dialog=self.slider_dialog.value() / 100.0,
            widget=self.slider_widget.value() / 100.0,
            tooltip=self.slider_tooltip.value() / 100.0,
            aurorae_active=self.slider_aurorae_act.value() / 100.0,
            aurorae_inactive=self.slider_aurorae_inact.value() / 100.0,
        )

        theme_filter = (
            "graphite" if self.radio_graphite.isChecked() else
            "obsidian" if self.radio_obsidian.isChecked() else "all"
        )

        self.btn_apply.setEnabled(False)
        self.btn_apply.setText("Applying...")
        self.status_lbl.setText("Modifying theme assets and refreshing caches...")

        self.worker = ApplyWorker(
            recipe=recipe,
            theme_filter=theme_filter,
            include_root=self.chk_include_root.isChecked(),
            include_aurorae=self.chk_aurorae.isChecked(),
            reload_cache=self.chk_reload.isChecked(),
            dry_run=self.chk_dry_run.isChecked(),
        )
        self.worker.finished.connect(self._on_apply_finished)
        self.worker.error.connect(self._on_apply_error)
        self.worker.start()

    def _on_apply_finished(self, modified: list[str], reloads: list[str], is_dry_run: bool) -> None:
        self.btn_apply.setEnabled(True)
        self.btn_apply.setText("Apply Transparency")
        count = len(modified)
        if is_dry_run:
            self.status_lbl.setText(f"[dry-run] Would update {count} file(s). No files written.")
            self.status_lbl.setStyleSheet("font-size: 12px; color: #22D3EE; padding-top: 4px; font-weight: 600;")
        else:
            self.status_lbl.setText(f"Successfully applied {self.slider_panel.value()}% opacity to {count} file(s)!")
            self.status_lbl.setStyleSheet("font-size: 12px; color: #A3FF47; padding-top: 4px; font-weight: 600;")

    def _on_apply_error(self, err_msg: str) -> None:
        self.btn_apply.setEnabled(True)
        self.btn_apply.setText("Apply Transparency")
        self.status_lbl.setText(f"Error: {err_msg}")
        self.status_lbl.setStyleSheet("font-size: 12px; color: #FF6B7A; padding-top: 4px;")

    def _open_kde_effects(self) -> None:
        import subprocess
        for cmd in (["systemsettings", "kcm_kwin_effects"], ["kcmshell6", "kcm_kwin_effects"]):
            try:
                subprocess.Popen(cmd)
                return
            except OSError:
                continue


def launch_gui() -> int:
    """Entry point to start the Qt 6 GUI application."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("NoxForge Depth & Opacity Configurator")

    window = OpacityConfiguratorWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(launch_gui())
