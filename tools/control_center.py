#!/usr/bin/env python3
"""NoxForge Control Center v3 - Qt 6 Graphical Hub.

Unifies profile switching (Graphite <-> Obsidian), accent color management,
real-time self-theming, depth & opacity configuration, Flatpak overrides,
reversible ecosystem deployment/restoration, and system diagnostics.
"""

from __future__ import annotations

import argparse
import importlib.machinery
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
for _p in (
    str(SCRIPT_DIR),
    str(ROOT / "tools"),
    str(ROOT),
    "/usr/share/noxforge",
    str(Path.home() / ".local/share/noxforge"),
):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import noxforge_core  # noqa: E402


def get_app_version() -> str:
    candidates = [
        ROOT / "VERSION",
        SCRIPT_DIR.parent / "VERSION",
        Path("/usr/share/noxforge/VERSION"),
    ]
    for p in candidates:
        if p.is_file():
            try:
                v = p.read_text(encoding="utf-8").strip()
                if v:
                    return v
            except Exception:
                pass
    return "18.0.0"


APP_VERSION = get_app_version()

# Load noxforge-ctl module
ctl_candidates = [
    ROOT / "tools/noxforge-ctl",
    SCRIPT_DIR / "noxforge-ctl",
    Path(shutil.which("noxforge-ctl") or "/usr/bin/noxforge-ctl"),
    Path.home() / ".local/bin/noxforge-ctl",
    Path("/usr/bin/noxforge-ctl"),
]
ctl_path = next((p for p in ctl_candidates if p.is_file()), None)
if not ctl_path:
    raise FileNotFoundError("Could not find noxforge-ctl executable")

loader_ctl = importlib.machinery.SourceFileLoader("noxforge_ctl", str(ctl_path))
spec_ctl = importlib.util.spec_from_loader("noxforge_ctl", loader_ctl)
assert spec_ctl and spec_ctl.loader
noxforge_ctl = importlib.util.module_from_spec(spec_ctl)
spec_ctl.loader.exec_module(noxforge_ctl)

# Load opacity_gui module
try:
    from tools import opacity_gui
except ImportError:
    try:
        import opacity_gui
    except ImportError:
        opacity_candidates = [
            ROOT / "tools/opacity_gui.py",
            SCRIPT_DIR / "opacity_gui.py",
            Path("/usr/share/noxforge/opacity_gui.py"),
            Path.home() / ".local/share/noxforge/opacity_gui.py",
        ]
        opacity_path = next((p for p in opacity_candidates if p.is_file()), None)
        if not opacity_path:
            raise FileNotFoundError("Could not find opacity_gui.py")
        loader_op = importlib.machinery.SourceFileLoader("opacity_gui", str(opacity_path))
        spec_op = importlib.util.spec_from_loader("opacity_gui", loader_op)
        assert spec_op and spec_op.loader
        opacity_gui = importlib.util.module_from_spec(spec_op)
        spec_op.loader.exec_module(opacity_gui)

STYLE_SHEET = noxforge_core.build_qt_stylesheet()


class ProfileAccentTab(QtWidgets.QWidget):
    statusChanged = QtCore.Signal(str)
    themeChanged = QtCore.Signal(str, str)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Profile Switcher Section
        profile_group = QtWidgets.QGroupBox("Desktop Profile (KDE, GTK, Libadwaita & Terminals)")
        p_layout = QtWidgets.QVBoxLayout(profile_group)

        desc = QtWidgets.QLabel(
            "Switch between standard Graphite gray surfaces and true pitch-black Obsidian OLED with one click:"
        )
        desc.setStyleSheet("color: #A6B4B9; margin-bottom: 8px;")
        p_layout.addWidget(desc)

        btn_row = QtWidgets.QHBoxLayout()
        self.btn_graphite = QtWidgets.QPushButton("NoxForge Graphite (Standard)")
        self.btn_graphite.setMinimumHeight(44)
        self.btn_graphite.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DesktopIcon))
        self.btn_graphite.clicked.connect(lambda: self.apply_profile("graphite"))

        self.btn_obsidian = QtWidgets.QPushButton("NoxForge Obsidian (OLED)")
        self.btn_obsidian.setMinimumHeight(44)
        self.btn_obsidian.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DesktopIcon))
        self.btn_obsidian.clicked.connect(lambda: self.apply_profile("obsidian"))

        btn_row.addWidget(self.btn_graphite)
        btn_row.addWidget(self.btn_obsidian)
        p_layout.addLayout(btn_row)

        # 1-Click Full Setup Action
        setup_row = QtWidgets.QHBoxLayout()
        self.setup_full_btn = QtWidgets.QPushButton(
            "  ⚡  Apply Complete Setup (Global Theme, Icons, Cursors & Wallpaper)"
        )
        self.setup_full_btn.setMinimumHeight(34)
        self.setup_full_btn.setStyleSheet(
            "background-color: #142218; border: 1px solid #A3FF47; border-radius: 5px; "
            "color: #A3FF47; font-weight: bold; font-size: 11px; padding: 4px 12px;"
        )
        self.setup_full_btn.clicked.connect(self.apply_full_active_setup)
        setup_row.addWidget(self.setup_full_btn)
        p_layout.addLayout(setup_row)

        layout.addWidget(profile_group)

        # Accent Color Section
        accent_group = QtWidgets.QGroupBox("Forge Accent Matrix")
        a_layout = QtWidgets.QVBoxLayout(accent_group)

        a_desc = QtWidgets.QLabel(
            "Select signature accent color for controls, focus rings, GTK/Libadwaita, and notch indicators:"
        )
        a_desc.setStyleSheet("color: #A6B4B9; margin-bottom: 8px;")
        a_layout.addWidget(a_desc)

        accent_grid = QtWidgets.QGridLayout()
        self.accent_buttons: dict[str, QtWidgets.QPushButton] = {}
        self.accent_meta: dict[str, tuple[str, str]] = {}
        accents = [
            ("lime", "Electric Lime (#A3FF47)", "#A3FF47"),
            ("cyan", "Forge Cyan (#22D3EE)", "#22D3EE"),
            ("violet", "Cyber Violet (#A78BFA)", "#A78BFA"),
            ("amber", "Molten Amber (#FBBF24)", "#FBBF24"),
            ("system", "System Accent (Plasma Dynamic)", "#FFFFFF"),
        ]

        for idx, (key, label, color) in enumerate(accents):
            btn = QtWidgets.QPushButton(f"  ●  {label}")
            btn.setMinimumHeight(36)
            btn.setStyleSheet(f"text-align: left; padding: 6px 12px; font-weight: bold; color: {color};")
            btn.clicked.connect(lambda _, k=key: self.apply_accent(k))
            self.accent_buttons[key] = btn
            self.accent_meta[key] = (label, color)
            accent_grid.addWidget(btn, idx // 2, idx % 2)

        a_layout.addLayout(accent_grid)
        layout.addWidget(accent_group)

        # Wallpaper Suite Selector Section
        wp_group = QtWidgets.QGroupBox("Wallpaper Suite (Standard, Obsidian, Quiet & Ultrawide)")
        wp_layout = QtWidgets.QHBoxLayout(wp_group)
        wp_lbl = QtWidgets.QLabel("Wallpaper Variant:")
        wp_lbl.setStyleSheet("color: #A6B4B9;")
        self.wallpaper_combo = QtWidgets.QComboBox()
        wp_lbl.setBuddy(self.wallpaper_combo)
        self.wallpaper_combo.setAccessibleName("Wallpaper Variant Selector")
        for var_key, var_info in noxforge_core.WALLPAPER_VARIANTS.items():
            self.wallpaper_combo.addItem(f"{var_info['label']} ({var_info['id']})", var_key)
        self.btn_apply_wallpaper = QtWidgets.QPushButton("Apply Wallpaper")
        self.btn_apply_wallpaper.setAccessibleName("Apply Wallpaper")
        self.btn_apply_wallpaper.clicked.connect(self.apply_selected_wallpaper)
        wp_layout.addWidget(wp_lbl)
        wp_layout.addWidget(self.wallpaper_combo, stretch=1)
        wp_layout.addWidget(self.btn_apply_wallpaper)
        layout.addWidget(wp_group)

        # Live Icon & Kinetic Motion Preview Section
        preview_group = QtWidgets.QGroupBox(
            f"Live Icon & Kinetic Motion Preview (v{APP_VERSION} Adaptive Vector Suite)"
        )
        prev_layout = QtWidgets.QVBoxLayout(preview_group)

        prev_desc = QtWidgets.QLabel(
            "Adaptive vector glyphs (Wi-Fi 0%–100%, Battery, Audio) and kinetic physics simulation:"
        )
        prev_desc.setStyleSheet("color: #A6B4B9; margin-bottom: 6px;")
        prev_layout.addWidget(prev_desc)

        icons_row = QtWidgets.QHBoxLayout()
        icons_row.setSpacing(10)
        self.preview_badges: list[tuple[QtWidgets.QLabel, QtWidgets.QLabel, Path]] = []

        icon_samples = [
            ("Wi-Fi 100%", ROOT / "icons/NoxForge/scalable/status/network-wireless.svg"),
            ("Wi-Fi 75%", ROOT / "icons/NoxForge/scalable/status/network-wireless-connected-75.svg"),
            ("Wi-Fi 50%", ROOT / "icons/NoxForge/scalable/status/network-wireless-connected-50.svg"),
            ("Wi-Fi 25%", ROOT / "icons/NoxForge/scalable/status/network-wireless-connected-25.svg"),
            ("Wi-Fi 0%", ROOT / "icons/NoxForge/scalable/status/network-wireless-connected-00.svg"),
            ("Disconnected", ROOT / "icons/NoxForge/scalable/status/network-wireless-disconnected.svg"),
            ("Battery", ROOT / "icons/NoxForge/scalable/status/battery-100.svg"),
            ("Audio", ROOT / "icons/NoxForge/scalable/status/audio-volume-high.svg"),
        ]

        for title, svg_path in icon_samples:
            col = QtWidgets.QVBoxLayout()
            col.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            img_lbl = QtWidgets.QLabel()
            img_lbl.setFixedSize(36, 36)
            img_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            img_lbl.setStyleSheet("border: 1px solid #2F414B; border-radius: 6px; padding: 4px;")
            if svg_path.is_file():
                img_lbl.setPixmap(QtGui.QIcon(str(svg_path)).pixmap(24, 24))

            txt_lbl = QtWidgets.QLabel(title)
            txt_lbl.setStyleSheet("color: #748289; font-size: 10px; font-weight: 600;")
            txt_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            col.addWidget(img_lbl)
            col.addWidget(txt_lbl)
            icons_row.addLayout(col)
            self.preview_badges.append((img_lbl, txt_lbl, svg_path))

        prev_layout.addLayout(icons_row)

        # Kinetic Motion Test Row
        motion_row = QtWidgets.QHBoxLayout()
        self.test_box = QtWidgets.QLineEdit(f"NoxForge Kinetic Motion v{APP_VERSION}")
        self.test_box.setPlaceholderText("Interactive input field (test kinetic spring physics)")
        self.test_box.setAccessibleName("Kinetic Motion Test Input")
        self.btn_test_shake = QtWidgets.QPushButton("Test Kinetic Spring Motion (220ms)")
        self.btn_test_shake.setMinimumHeight(32)
        self.btn_test_shake.clicked.connect(self.play_test_shake)

        motion_row.addWidget(self.test_box, stretch=1)
        motion_row.addWidget(self.btn_test_shake)
        prev_layout.addLayout(motion_row)

        layout.addWidget(preview_group)

        # Day/Night Automation Section
        sched_group = QtWidgets.QGroupBox("Day / Night Automation")
        s_layout = QtWidgets.QHBoxLayout(sched_group)
        self.sched_check = QtWidgets.QCheckBox("Enable automatic profile switching:")
        self.sched_check.setStyleSheet("color: #E8F0F2; font-weight: 500;")
        self.sched_check.toggled.connect(self.toggle_schedule)
        s_layout.addWidget(self.sched_check)

        day_lbl = QtWidgets.QLabel("Day (Graphite):")
        day_lbl.setStyleSheet("color: #A6B4B9;")
        self.day_time = QtWidgets.QTimeEdit()
        day_lbl.setBuddy(self.day_time)
        self.day_time.setAccessibleName("Day time")
        self.day_time.setDisplayFormat("HH:mm")
        self.day_time.setTime(QtCore.QTime(7, 0))
        self.day_time.timeChanged.connect(self.on_time_changed)

        night_lbl = QtWidgets.QLabel("Night (Obsidian):")
        night_lbl.setStyleSheet("color: #A6B4B9;")
        self.night_time = QtWidgets.QTimeEdit()
        night_lbl.setBuddy(self.night_time)
        self.night_time.setAccessibleName("Night time")
        self.night_time.setDisplayFormat("HH:mm")
        self.night_time.setTime(QtCore.QTime(20, 0))
        self.night_time.timeChanged.connect(self.on_time_changed)

        s_layout.addWidget(day_lbl)
        s_layout.addWidget(self.day_time)
        s_layout.addWidget(night_lbl)
        s_layout.addWidget(self.night_time)
        s_layout.addStretch()
        layout.addWidget(sched_group)

        layout.addStretch()
        self.refresh_state()

    def play_test_shake(self) -> None:
        status = noxforge_ctl.get_current_status()
        profile = status.get("profile", "graphite")
        pal = noxforge_core.resolve_accent_palette(
            status.get("accentHex", "#A3FF47"), is_obsidian=(profile == "obsidian")
        )
        acc = pal["accent"]
        surf_sel = pal["surfaceSelected"]

        orig_rect = self.test_box.geometry()
        anim = QtCore.QSequentialAnimationGroup(self)
        for dx, dur in [(-8, 40), (8, 40), (-4, 40), (4, 40), (0, 60)]:
            step = QtCore.QPropertyAnimation(self.test_box, b"geometry")
            step.setDuration(dur)
            step.setStartValue(self.test_box.geometry())
            target_rect = QtCore.QRect(orig_rect.x() + dx, orig_rect.y(), orig_rect.width(), orig_rect.height())
            step.setEndValue(target_rect)
            anim.addAnimation(step)
        self.test_box.setStyleSheet(
            f"background-color: {surf_sel}; border: 2px solid {acc}; border-radius: 5px; "
            f"color: {acc}; padding: 6px 12px; font-size: 12px; font-weight: bold;"
        )

        def restore():
            self.test_box.setStyleSheet("")
            self.test_box.setGeometry(orig_rect)

        anim.finished.connect(restore)
        self._shake_anim = anim
        anim.start()

    def refresh_state(self) -> None:
        status = noxforge_ctl.get_current_status()
        profile = status.get("profile", "graphite")
        accent_name = status.get("accent", "lime")
        accent_hex = status.get("accentHex", "#A3FF47")
        pal = noxforge_core.resolve_accent_palette(accent_hex, is_obsidian=(profile == "obsidian"))
        acc = pal["accent"]
        surf_sel = pal["surfaceSelected"]

        active_btn_style = f"background-color: {surf_sel}; border: 2px solid {acc}; color: #FFFFFF; font-weight: bold;"
        if profile == "obsidian":
            self.btn_obsidian.setStyleSheet(active_btn_style)
            self.btn_graphite.setStyleSheet("")
        else:
            self.btn_graphite.setStyleSheet(active_btn_style)
            self.btn_obsidian.setStyleSheet("")

        for key, btn in self.accent_buttons.items():
            _, color = self.accent_meta[key]
            is_selected = (key == accent_name) or (key == "lime" and accent_name == "default")
            if is_selected:
                btn.setStyleSheet(
                    f"text-align: left; padding: 6px 12px; font-weight: bold; color: {color}; "
                    f"background-color: {surf_sel}; border: 2px solid {color};"
                )
            else:
                btn.setStyleSheet(f"text-align: left; padding: 6px 12px; font-weight: bold; color: {color};")

        self.setup_full_btn.setStyleSheet(
            f"background-color: {surf_sel}; border: 1px solid {acc}; border-radius: 5px; "
            f"color: {acc}; font-weight: bold; font-size: 11px; padding: 4px 12px;"
        )

        if hasattr(noxforge_ctl, "manage_wallpaper") and hasattr(self, "wallpaper_combo"):
            wp_info = noxforge_ctl.manage_wallpaper("status")
            active_wp = wp_info.get("activeVariant", "obsidian" if profile == "obsidian" else "standard")
            idx = self.wallpaper_combo.findData(active_wp)
            if idx >= 0:
                self.wallpaper_combo.blockSignals(True)
                self.wallpaper_combo.setCurrentIndex(idx)
                self.wallpaper_combo.blockSignals(False)

        if hasattr(self, "preview_badges"):
            for img_lbl, _, svg_path in self.preview_badges:
                if svg_path.is_file():
                    img_lbl.setPixmap(QtGui.QIcon(str(svg_path)).pixmap(24, 24))

        sched = noxforge_ctl.manage_schedule("status")
        is_sched = sched.get("scheduled", False)
        self.sched_check.blockSignals(True)
        self.sched_check.setChecked(is_sched)
        self.sched_check.blockSignals(False)
        sched_desc = sched.get("schedule", "")
        if " / " in sched_desc:
            parts = sched_desc.split(" / ")
            try:
                d_str = parts[0].split()[0]
                n_str = parts[1].split()[0]
                self.day_time.blockSignals(True)
                self.night_time.blockSignals(True)
                self.day_time.setTime(QtCore.QTime.fromString(d_str, "HH:mm"))
                self.night_time.setTime(QtCore.QTime.fromString(n_str, "HH:mm"))
                self.day_time.blockSignals(False)
                self.night_time.blockSignals(False)
            except Exception:
                pass

    def apply_selected_wallpaper(self) -> None:
        variant = self.wallpaper_combo.currentData() or "standard"
        if hasattr(noxforge_ctl, "manage_wallpaper"):
            res = noxforge_ctl.manage_wallpaper(str(variant))
            self.statusChanged.emit(f"Wallpaper applied: {res.get('label')} ({res.get('wallpaperId')})")

    def apply_profile(self, profile: str) -> None:
        if hasattr(noxforge_ctl, "apply_setup"):
            noxforge_ctl.apply_setup(profile)
        else:
            noxforge_ctl.switch_profile(profile)
        self.refresh_state()
        status = noxforge_ctl.get_current_status()
        self.themeChanged.emit(profile, status.get("accentHex", "#A3FF47"))
        self.statusChanged.emit(f"Profile activated: {profile.upper()} (complete desktop synchronized)")

    def apply_full_active_setup(self) -> None:
        status = noxforge_ctl.get_current_status()
        profile = status.get("profile", "graphite")
        if profile not in ("graphite", "obsidian"):
            profile = "graphite"
        if hasattr(noxforge_ctl, "apply_setup"):
            noxforge_ctl.apply_setup(profile)
        else:
            noxforge_ctl.sync_desktop(profile)
        self.refresh_state()
        self.themeChanged.emit(profile, status.get("accentHex", "#A3FF47"))
        self.statusChanged.emit(f"Complete {profile.upper()} setup applied (Theme, Icons, Cursors, Wallpaper)")

    def apply_accent(self, accent: str) -> None:
        res = noxforge_ctl.set_accent(accent)
        self.refresh_state()
        status = noxforge_ctl.get_current_status()
        hex_color = res.get("hex") or status.get("accentHex", "#A3FF47")
        self.themeChanged.emit(status.get("profile", "graphite"), hex_color)
        self.statusChanged.emit(f"Accent color activated: {accent.upper()}")

    def on_time_changed(self) -> None:
        if self.sched_check.isChecked():
            self.toggle_schedule(True)

    def toggle_schedule(self, checked: bool) -> None:
        action = "enable" if checked else "disable"
        dt = self.day_time.time().toString("HH:mm")
        nt = self.night_time.time().toString("HH:mm")
        try:
            noxforge_ctl.manage_schedule(action, day_time=dt, night_time=nt)
            self.statusChanged.emit(f"Day/Night automation: {action.upper()} ({dt} / {nt})")
        except Exception as err:
            self.statusChanged.emit(f"Day/Night schedule error: {err}")


class HealthTab(QtWidgets.QWidget):
    statusChanged = QtCore.Signal(str)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        header = QtWidgets.QLabel("NoxForge System Health & Ecosystem Status")
        header.setStyleSheet("font-size: 15px; font-weight: bold; color: #E8F0F2;")
        layout.addWidget(header)

        # Visual Health Summary Badges
        badges_row = QtWidgets.QHBoxLayout()
        badges_row.setSpacing(8)
        self.badge_core = QtWidgets.QLabel("Core: Checking")
        self.badge_palette = QtWidgets.QLabel("Palette: Checking")
        self.badge_gtk = QtWidgets.QLabel("GTK/Libadwaita: Checking")
        self.badge_flatpak = QtWidgets.QLabel("Flatpak: Checking")
        self.badge_eco = QtWidgets.QLabel("Ecosystem: Checking")
        for b in (self.badge_core, self.badge_palette, self.badge_gtk, self.badge_flatpak, self.badge_eco):
            b.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            b.setStyleSheet(
                "background-color: #141E25; border: 1px solid #2F414B; border-radius: 5px; "
                "padding: 6px 10px; font-size: 11px; font-weight: 700; color: #A6B4B9;"
            )
            badges_row.addWidget(b, stretch=1)
        layout.addLayout(badges_row)

        self.info_text = QtWidgets.QTextEdit()
        self.info_text.setReadOnly(True)
        layout.addWidget(self.info_text)

        btn_row = QtWidgets.QHBoxLayout()
        self.btn_refresh = QtWidgets.QPushButton("Run Health Check (Doctor)")
        self.btn_refresh.clicked.connect(self.run_doctor)
        self.btn_sync = QtWidgets.QPushButton("Synchronize & Remediate Desktop")
        self.btn_sync.setObjectName("applyButton")
        self.btn_sync.clicked.connect(self.align_desktop)

        btn_row.addWidget(self.btn_refresh)
        btn_row.addWidget(self.btn_sync)
        layout.addLayout(btn_row)

        self.run_doctor()

    @staticmethod
    def _style_health_badge(badge: QtWidgets.QLabel, text: str, ok: bool) -> None:
        color = "#A3FF47" if ok else "#FBBF24"
        bg = "#192D1E" if ok else "#261D0E"
        badge.setText(text)
        badge.setStyleSheet(
            f"background-color: {bg}; border: 1px solid {color}; border-radius: 5px; "
            f"padding: 6px 10px; font-size: 11px; font-weight: 700; color: {color};"
        )

    def run_doctor(self) -> None:
        doctor_candidates = [
            ROOT / "tools/noxforge-doctor",
            SCRIPT_DIR / "noxforge-doctor",
            Path(shutil.which("noxforge-doctor") or "/usr/bin/noxforge-doctor"),
            Path.home() / ".local/bin/noxforge-doctor",
            Path("/usr/bin/noxforge-doctor"),
        ]
        tool_doctor = next((p for p in doctor_candidates if p.is_file()), None)
        if not tool_doctor:
            self.info_text.setPlainText("Could not find noxforge-doctor utility.")
            return
        try:
            res = subprocess.run(
                [sys.executable, str(tool_doctor), "--json"], capture_output=True, text=True, check=False
            )
            data = json.loads(res.stdout)
            status = data.get("status", "ok")
            missing = data.get("missing", [])
            edition = data.get("edition", {}).get("kind", "complete-system")
            eco = data.get("ecosystem", {})
            flatpak = eco.get("flatpakThemesOverride", "ok")
            palette_sync = data.get("paletteSynchronization", {}).get("status", "synchronized")
            gtk_chain = data.get("gtkChainStatus", {}).get("status", "ok")
            core_status = data.get("noxforgeCoreStatus", "ok")
            eco_state = data.get("ecosystemState", {})

            self._style_health_badge(self.badge_core, f"● Core: {core_status.upper()}", core_status == "ok")
            self._style_health_badge(
                self.badge_palette, f"● Palette: {palette_sync.upper()}", palette_sync != "desynchronized"
            )
            self._style_health_badge(self.badge_gtk, f"● GTK/Adw: {gtk_chain.upper()}", gtk_chain == "ok")
            self._style_health_badge(
                self.badge_flatpak, f"● Flatpak: {flatpak.upper()}", flatpak in ("ok", "configured")
            )
            self._style_health_badge(self.badge_eco, "● Ecosystem: REVERSIBLE", bool(eco_state.get("reversible", True)))

            text = "=== NOXFORGE DOCTOR REPORT ===\n"
            text += f"Schema Version: {data.get('schemaVersion', 11)}\n"
            text += f"Status: {status.upper()}\n"
            text += f"Edition: {edition}\n"
            text += f"Package Version: {data.get('packageVersion') or 'local / source'}\n"
            text += f"Core Library (noxforge_core.py): {core_status.upper()}\n"
            text += f"Palette Synchronization: {palette_sync.upper()}\n"
            text += f"GTK 3/4 & Libadwaita Chain: {gtk_chain.upper()}\n"
            text += f"Flatpak Themes Override: {flatpak}\n"
            text += f"Missing Components: {len(missing)}\n"
            if missing:
                text += "  - " + "\n  - ".join(missing) + "\n"
            self.info_text.setPlainText(text)
        except Exception as err:
            self.info_text.setPlainText(f"Could not execute noxforge-doctor: {err}")

    def align_desktop(self) -> None:
        status = noxforge_ctl.get_current_status()
        profile = status.get("profile", "graphite")
        if profile not in ("graphite", "obsidian"):
            profile = "graphite"
        noxforge_ctl.sync_desktop(profile)
        self.run_doctor()
        self.statusChanged.emit(f"Desktop successfully synchronized to {profile.upper()}!")


class AccessibilityTab(QtWidgets.QWidget):
    statusChanged = QtCore.Signal(str)
    themeChanged = QtCore.Signal(str, str)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Reduced Motion Section
        motion_group = QtWidgets.QGroupBox("Reduced Motion & Focus Indicators (WCAG 2.2.2 / 2.3.3)")
        m_layout = QtWidgets.QVBoxLayout(motion_group)

        m_desc = QtWidgets.QLabel(
            "Configure accessible kinetic motion policies across Plasma lock screens, "
            "SDDM greeters, and KWin TabBox switchers. When reduced motion is active, "
            "dynamic spring shakes are replaced by high-contrast static 220ms edge-flash borders."
        )
        m_desc.setWordWrap(True)
        m_desc.setStyleSheet("color: #A6B4B9; margin-bottom: 8px;")
        m_layout.addWidget(m_desc)

        # System-Wide Reduced Motion Live Toggle
        toggle_row = QtWidgets.QHBoxLayout()
        self.chk_reduced_motion = QtWidgets.QCheckBox(
            "Enable System-Wide Reduced Motion (0ms animations, static focus rings)"
        )
        self.chk_reduced_motion.setStyleSheet("font-weight: 600;")
        self.chk_reduced_motion.toggled.connect(self.toggle_reduced_motion)

        self.motion_status_badge = QtWidgets.QLabel("Mode: STANDARD KINETIC")
        self.motion_status_badge.setStyleSheet(
            "background-color: #16242C; color: #22D3EE; border: 1px solid #22D3EE; "
            "border-radius: 4px; padding: 3px 8px; font-size: 11px; font-weight: 700;"
        )
        toggle_row.addWidget(self.chk_reduced_motion)
        toggle_row.addStretch()
        toggle_row.addWidget(self.motion_status_badge)
        m_layout.addLayout(toggle_row)

        # Simulation preview box
        sim_row = QtWidgets.QHBoxLayout()
        self.sim_input = QtWidgets.QLineEdit("Authentication Error Indicator")
        self.sim_input.setReadOnly(True)
        self.sim_input.setAccessibleName("Simulation preview box")
        self.sim_input.setStyleSheet(
            "background-color: #10191F; border: 1px solid #2F414B; border-radius: 5px; "
            "color: #E8F0F2; padding: 8px 12px; font-size: 13px;"
        )
        self.btn_sim_kinetic = QtWidgets.QPushButton("Test Kinetic Shake (Standard)")
        self.btn_sim_kinetic.clicked.connect(self.play_kinetic_shake)
        self.btn_sim_edge = QtWidgets.QPushButton("Test Static Edge-Flash (Reduced Motion)")
        self.btn_sim_edge.setStyleSheet(
            "background-color: #1A2832; border: 1px solid #A3FF47; color: #A3FF47; font-weight: bold;"
        )
        self.btn_sim_edge.clicked.connect(self.play_edge_flash)

        sim_row.addWidget(self.sim_input, stretch=1)
        sim_row.addWidget(self.btn_sim_kinetic)
        sim_row.addWidget(self.btn_sim_edge)
        m_layout.addLayout(sim_row)
        layout.addWidget(motion_group)

        # Custom Accent WCAG AA Calculator Section
        accent_group = QtWidgets.QGroupBox("Custom Accent WCAG AA Contrast Calculator")
        a_layout = QtWidgets.QVBoxLayout(accent_group)

        a_desc = QtWidgets.QLabel(
            "Test and apply custom accent colors. Enforces a minimum 4.5:1 contrast ratio against "
            "both dark graphite surfaces (#141E25) and pure OLED obsidian (#000000):"
        )
        a_desc.setWordWrap(True)
        a_desc.setStyleSheet("color: #A6B4B9; margin-bottom: 8px;")
        a_layout.addWidget(a_desc)

        input_row = QtWidgets.QHBoxLayout()
        self.hex_input = QtWidgets.QLineEdit("#A3FF47")
        self.hex_input.setPlaceholderText("#RRGGBB (e.g. #A3FF47)")
        self.hex_input.setMaxLength(7)
        self.hex_input.setAccessibleName("Custom Hex Input")
        self.hex_input.textChanged.connect(self.update_contrast_readout)

        self.btn_pick_color = QtWidgets.QPushButton("Pick Color…")
        self.btn_pick_color.setAccessibleName("Pick Custom Accent Color")
        self.btn_pick_color.clicked.connect(self.open_color_picker)

        self.color_swatch = QtWidgets.QLabel("  PREVIEW  ")
        self.color_swatch.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.color_swatch.setStyleSheet(
            "background-color: #A3FF47; color: #0D1419; font-weight: bold; border-radius: 4px; padding: 6px 12px;"
        )

        self.btn_apply_custom = QtWidgets.QPushButton("Apply Custom Accent")
        self.btn_apply_custom.clicked.connect(self.apply_custom_accent)

        input_row.addWidget(QtWidgets.QLabel("Custom Hex:"))
        input_row.addWidget(self.hex_input)
        input_row.addWidget(self.btn_pick_color)
        input_row.addWidget(self.color_swatch)
        input_row.addWidget(self.btn_apply_custom)
        a_layout.addLayout(input_row)

        self.contrast_label = QtWidgets.QLabel("Contrast: Graphite 13.65:1 (PASS) | Obsidian 16.95:1 (PASS)")
        self.contrast_label.setStyleSheet("color: #A3FF47; font-weight: 600; margin-top: 6px;")
        a_layout.addWidget(self.contrast_label)

        layout.addWidget(accent_group)
        layout.addStretch()
        self.refresh_state()

    def refresh_state(self) -> None:
        if hasattr(noxforge_ctl, "manage_motion"):
            mot = noxforge_ctl.manage_motion("status")
            is_red = bool(mot.get("reducedMotion", False))
            self.chk_reduced_motion.blockSignals(True)
            self.chk_reduced_motion.setChecked(is_red)
            self.chk_reduced_motion.blockSignals(False)
            self._update_motion_badge(is_red)

    def _update_motion_badge(self, is_reduced: bool) -> None:
        if is_reduced:
            self.motion_status_badge.setText("● Mode: REDUCED MOTION (0ms)")
            self.motion_status_badge.setStyleSheet(
                "background-color: #192D1E; color: #A3FF47; border: 1px solid #A3FF47; "
                "border-radius: 4px; padding: 3px 8px; font-size: 11px; font-weight: 700;"
            )
        else:
            self.motion_status_badge.setText("● Mode: STANDARD KINETIC")
            self.motion_status_badge.setStyleSheet(
                "background-color: #16242C; color: #22D3EE; border: 1px solid #22D3EE; "
                "border-radius: 4px; padding: 3px 8px; font-size: 11px; font-weight: 700;"
            )

    def toggle_reduced_motion(self, checked: bool) -> None:
        if hasattr(noxforge_ctl, "manage_motion"):
            action = "reduced" if checked else "standard"
            noxforge_ctl.manage_motion(action)
            self._update_motion_badge(checked)
            self.statusChanged.emit(f"Motion policy set to: {action.upper()}")

    def open_color_picker(self) -> None:
        initial = QtGui.QColor(self.hex_input.text().strip() or "#A3FF47")
        chosen = QtWidgets.QColorDialog.getColor(initial, self, "Select Custom Accent Color")
        if chosen.isValid():
            self.hex_input.setText(chosen.name().upper())

    def play_kinetic_shake(self) -> None:
        orig = self.sim_input.geometry()
        anim = QtCore.QSequentialAnimationGroup(self)
        for dx, dur in [(-8, 40), (8, 40), (-4, 40), (4, 40), (0, 60)]:
            step = QtCore.QPropertyAnimation(self.sim_input, b"geometry")
            step.setDuration(dur)
            step.setStartValue(self.sim_input.geometry())
            step.setEndValue(QtCore.QRect(orig.x() + dx, orig.y(), orig.width(), orig.height()))
            anim.addAnimation(step)
        self.sim_input.setStyleSheet(
            "background-color: #2D1418; border: 2px solid #FF5555; border-radius: 5px; "
            "color: #FF7777; padding: 8px 12px; font-size: 13px; font-weight: bold;"
        )

        def restore():
            self.sim_input.setStyleSheet(
                "background-color: #10191F; border: 1px solid #2F414B; border-radius: 5px; "
                "color: #E8F0F2; padding: 8px 12px; font-size: 13px;"
            )
            self.sim_input.setGeometry(orig)

        anim.finished.connect(restore)
        anim.start()
        self.statusChanged.emit("Simulating kinetic spring shake (220ms)...")

    def play_edge_flash(self) -> None:
        self.sim_input.setStyleSheet(
            "background-color: #10191F; border: 2px solid #FF5555; border-radius: 5px; "
            "color: #FF5555; padding: 8px 12px; font-size: 13px; font-weight: bold;"
        )

        def restore():
            self.sim_input.setStyleSheet(
                "background-color: #10191F; border: 1px solid #2F414B; border-radius: 5px; "
                "color: #E8F0F2; padding: 8px 12px; font-size: 13px;"
            )

        QtCore.QTimer.singleShot(220, restore)
        self.statusChanged.emit("Simulating static edge-flash indicator (220ms, 0px translation)...")

    def update_contrast_readout(self, hex_text: str) -> None:
        clean = hex_text.strip()
        if len(clean) == 7 and clean.startswith("#"):
            try:
                cg, co = noxforge_ctl.validate_custom_accent_contrast(clean)
                self.color_swatch.setStyleSheet(
                    f"background-color: {clean}; color: #0D1419; font-weight: bold; border-radius: 4px; padding: 6px 12px;"
                )
                self.contrast_label.setText(f"Contrast: Graphite {cg:.2f}:1 (PASS) | Obsidian {co:.2f}:1 (PASS)")
                self.contrast_label.setStyleSheet("color: #A3FF47; font-weight: 600; margin-top: 6px;")
                self.btn_apply_custom.setEnabled(True)
            except Exception as err:
                self.contrast_label.setText(f"FAIL: {err}")
                self.contrast_label.setStyleSheet("color: #FF5555; font-weight: 600; margin-top: 6px;")
                self.btn_apply_custom.setEnabled(False)
        else:
            self.contrast_label.setText("Enter valid 7-character hex code (e.g. #A3FF47)")
            self.contrast_label.setStyleSheet("color: #A6B4B9; margin-top: 6px;")
            self.btn_apply_custom.setEnabled(False)

    def apply_custom_accent(self) -> None:
        clean = self.hex_input.text().strip()
        try:
            noxforge_ctl.set_accent("custom", custom_hex=clean)
            status = noxforge_ctl.get_current_status()
            self.themeChanged.emit(status.get("profile", "graphite"), clean.upper())
            self.statusChanged.emit(f"Custom accent applied: {clean}")
        except Exception as err:
            self.statusChanged.emit(f"Error applying accent: {err}")


class EcosystemTab(QtWidgets.QWidget):
    statusChanged = QtCore.Signal(str)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QtWidgets.QLabel("Developer Tools, Reversible Ecosystem & Flatpak")
        header.setStyleSheet("font-size: 15px; font-weight: bold; color: #E8F0F2;")
        layout.addWidget(header)

        desc = QtWidgets.QLabel(
            "Synchronize NoxForge themes with external developer applications, editors, and terminals. "
            "Deployments automatically create .noxforge.bak backups and stay synchronized when switching profiles or accents."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #A6B4B9; margin-bottom: 4px;")
        layout.addWidget(desc)

        # Flatpak Theme & Libadwaita Override Card
        self.flatpak_group = QtWidgets.QGroupBox("Flatpak & Libadwaita Sandbox Theme Access")
        fp_layout = QtWidgets.QHBoxLayout(self.flatpak_group)
        self.flatpak_status_lbl = QtWidgets.QLabel("Status: Checking...")
        self.flatpak_status_lbl.setStyleSheet("color: #A6B4B9; font-weight: 600;")
        self.btn_flatpak_enable = QtWidgets.QPushButton("Enable Flatpak Override")
        self.btn_flatpak_enable.setAccessibleName("Enable Flatpak Override")
        self.btn_flatpak_enable.clicked.connect(lambda: self.toggle_flatpak("enable"))
        self.btn_flatpak_disable = QtWidgets.QPushButton("Disable Override")
        self.btn_flatpak_disable.setAccessibleName("Disable Flatpak Override")
        self.btn_flatpak_disable.clicked.connect(lambda: self.toggle_flatpak("disable"))

        fp_layout.addWidget(self.flatpak_status_lbl, stretch=1)
        fp_layout.addWidget(self.btn_flatpak_enable)
        fp_layout.addWidget(self.btn_flatpak_disable)
        layout.addWidget(self.flatpak_group)

        # Table for ecosystem apps
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Application", "Status", "Theme Installed", "Deploy", "Restore Backup"])
        self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # Buttons row
        btn_row = QtWidgets.QHBoxLayout()
        self.btn_apply_all = QtWidgets.QPushButton("Deploy All Detected Themes")
        self.btn_apply_all.setObjectName("applyButton")
        self.btn_apply_all.setMinimumHeight(36)
        self.btn_apply_all.clicked.connect(self.apply_all_detected)

        self.btn_restore_all = QtWidgets.QPushButton("Restore All Backups")
        self.btn_restore_all.setAccessibleName("Restore All Backups")
        self.btn_restore_all.setMinimumHeight(36)
        self.btn_restore_all.clicked.connect(self.restore_all_backups)

        self.btn_refresh = QtWidgets.QPushButton("Refresh Status")
        self.btn_refresh.setMinimumHeight(36)
        self.btn_refresh.clicked.connect(self.refresh_table)

        btn_row.addWidget(self.btn_apply_all)
        btn_row.addWidget(self.btn_restore_all)
        btn_row.addWidget(self.btn_refresh)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.refresh_table()

    def toggle_flatpak(self, action: str) -> None:
        res = noxforge_ctl.manage_flatpak(action)
        self.refresh_table()
        self.statusChanged.emit(f"Flatpak override {action}: {res.get('status')}")

    def refresh_table(self) -> None:
        fp_info = (
            noxforge_ctl.manage_flatpak("status")
            if hasattr(noxforge_ctl, "manage_flatpak")
            else {"status": "unknown", "enabled": False}
        )
        fp_enabled = bool(fp_info.get("enabled"))
        self.flatpak_status_lbl.setText(
            f"Flatpak GTK/Libadwaita Override: {'● ENABLED (xdg-data/themes + gtk-3.0/4.0)' if fp_enabled else '○ NOT CONFIGURED'}"
        )
        self.flatpak_status_lbl.setStyleSheet(f"color: {'#A3FF47' if fp_enabled else '#A6B4B9'}; font-weight: 600;")

        status = noxforge_ctl.ecosystem_status()
        self.table.setRowCount(len(status))
        for row, (app_id, info) in enumerate(status.items()):
            # Col 0: App Name + desc
            name_item = QtWidgets.QTableWidgetItem(f"{info['name']} ({app_id})")
            name_item.setToolTip(info["description"])
            self.table.setItem(row, 0, name_item)

            # Col 1: Detected
            det_str = "● Detected" if info["detected"] else "○ Not Found"
            det_item = QtWidgets.QTableWidgetItem(det_str)
            det_item.setForeground(QtGui.QBrush(QtGui.QColor("#A3FF47" if info["detected"] else "#748289")))
            det_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, det_item)

            # Col 2: Installed + Sync state
            synced_prof = info.get("syncedProfile")
            if info["installed"]:
                inst_str = f"✓ Synced ({synced_prof.capitalize()})" if synced_prof else "✓ Synced"
            else:
                inst_str = "○ Not Deployed"
            inst_item = QtWidgets.QTableWidgetItem(inst_str)
            inst_item.setForeground(QtGui.QBrush(QtGui.QColor("#22D3EE" if info["installed"] else "#748289")))
            inst_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, inst_item)

            # Col 3: Deploy Action button
            action_btn = QtWidgets.QPushButton(f"Deploy Theme to {info['name']}")
            action_btn.setStyleSheet("padding: 4px 10px; font-size: 11px;")
            action_btn.clicked.connect(lambda _, a=app_id: self.apply_app(a))
            self.table.setCellWidget(row, 3, action_btn)

            # Col 4: Restore Backup button
            restore_btn = QtWidgets.QPushButton("Restore Backup")
            restore_btn.setStyleSheet("padding: 4px 10px; font-size: 11px;")
            restore_btn.setEnabled(bool(info.get("hasBackup") or info.get("installed")))
            restore_btn.clicked.connect(lambda _, a=app_id: self.restore_app(a))
            self.table.setCellWidget(row, 4, restore_btn)

    def apply_app(self, app_id: str) -> None:
        res = noxforge_ctl.ecosystem_apply([app_id])
        if res.get("errors"):
            self.statusChanged.emit(f"Error deploying to {app_id}: {res['errors'].get(app_id)}")
        elif app_id in res.get("applied", []):
            self.statusChanged.emit(f"Successfully deployed theme to {app_id}!")
        elif app_id in res.get("skipped", []):
            self.statusChanged.emit(f"Skipped {app_id} (target configuration not detected).")
        self.refresh_table()

    def restore_app(self, app_id: str) -> None:
        if hasattr(noxforge_ctl, "ecosystem_restore"):
            res = noxforge_ctl.ecosystem_restore([app_id])
            if res.get("errors"):
                self.statusChanged.emit(f"Error restoring {app_id}: {res['errors'].get(app_id)}")
            elif app_id in res.get("restored", []):
                self.statusChanged.emit(f"Restored original configuration for {app_id}.")
            else:
                self.statusChanged.emit(f"No backup to restore for {app_id}.")
        self.refresh_table()

    def apply_all_detected(self) -> None:
        res = noxforge_ctl.ecosystem_apply()
        applied = res.get("applied", [])
        self.statusChanged.emit(f"Ecosystem themes applied: {len(applied)} applications updated.")
        self.refresh_table()

    def restore_all_backups(self) -> None:
        if hasattr(noxforge_ctl, "ecosystem_restore"):
            res = noxforge_ctl.ecosystem_restore()
            restored = res.get("restored", [])
            self.statusChanged.emit(f"Restored backups for {len(restored)} applications.")
        self.refresh_table()


class ControlCenterWindow(QtWidgets.QMainWindow):
    def __init__(self, initial_tab: str | None = None) -> None:
        super().__init__()
        self.setWindowTitle("NoxForge Control Center")
        self.setMinimumSize(900, 720)
        self.active_profile = "graphite"
        self.active_accent_hex = "#A3FF47"

        icon_candidates = [
            ROOT / "icons/hicolor/scalable/apps/io.github.loofiboss.noxforge.controlcenter.svg",
            Path("/usr/share/icons/hicolor/scalable/apps/io.github.loofiboss.noxforge.controlcenter.svg"),
            Path.home() / ".local/share/icons/hicolor/scalable/apps/io.github.loofiboss.noxforge.controlcenter.svg",
        ]
        icon_path = next((p for p in icon_candidates if p.is_file()), None)
        if icon_path:
            self.setWindowIcon(QtGui.QIcon(str(icon_path)))

        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Top Status Header Banner
        self.header_banner = QtWidgets.QFrame()
        self.header_banner.setObjectName("headerBanner")
        hb_layout = QtWidgets.QHBoxLayout(self.header_banner)
        hb_layout.setContentsMargins(14, 8, 14, 8)
        hb_layout.setSpacing(10)

        self.header_title_lbl = QtWidgets.QLabel(f"◆  NOXFORGE CONTROL CENTER v{APP_VERSION}")
        self.header_title_lbl.setStyleSheet("font-size: 13px; font-weight: 800; letter-spacing: 0.8px;")

        self.header_profile_badge = QtWidgets.QLabel("● GRAPHITE")
        self.header_accent_badge = QtWidgets.QLabel("● #A3FF47")

        self.btn_export_preset = QtWidgets.QPushButton("Export Preset…")
        self.btn_export_preset.setAccessibleName("Export Preset")
        self.btn_export_preset.setStyleSheet("padding: 4px 10px; font-size: 11px;")
        self.btn_export_preset.clicked.connect(self.export_preset_dialog)

        self.btn_import_preset = QtWidgets.QPushButton("Import Preset…")
        self.btn_import_preset.setAccessibleName("Import Preset")
        self.btn_import_preset.setStyleSheet("padding: 4px 10px; font-size: 11px;")
        self.btn_import_preset.clicked.connect(self.import_preset_dialog)

        hb_layout.addWidget(self.header_title_lbl)
        hb_layout.addStretch()
        hb_layout.addWidget(self.header_profile_badge)
        hb_layout.addWidget(self.header_accent_badge)
        hb_layout.addWidget(self.btn_export_preset)
        hb_layout.addWidget(self.btn_import_preset)
        main_layout.addWidget(self.header_banner)

        # Tab Widget
        self.tabs = QtWidgets.QTabWidget()

        # Tab 1: Profile & Accent Hub
        self.tab_profile = ProfileAccentTab()
        self.tab_profile.statusChanged.connect(self.show_status)
        self.tab_profile.themeChanged.connect(self.refresh_theme)
        self.tabs.addTab(self.tab_profile, "Profile && Accent")

        # Tab 2: Opacity & Depth Configurator
        self.opacity_window = opacity_gui.OpacityConfiguratorWindow()
        self.tab_opacity = self.opacity_window
        opacity_inner = self.opacity_window.centralWidget()
        self.tabs.addTab(opacity_inner, "Transparency && Depth")

        # Tab 3: Accessibility & Motion
        self.tab_a11y = AccessibilityTab()
        self.tab_a11y.statusChanged.connect(self.show_status)
        self.tab_a11y.themeChanged.connect(self.refresh_theme)
        self.tabs.addTab(self.tab_a11y, "Accessibility && Motion")

        # Tab 4: Health & Diagnostics
        self.tab_health = HealthTab()
        self.tab_health.statusChanged.connect(self.show_status)
        self.tabs.addTab(self.tab_health, "System Health && Doctor")

        # Tab 5: Ecosystem & Developer Tools
        self.tab_eco = EcosystemTab()
        self.tab_eco.statusChanged.connect(self.show_status)
        self.tabs.addTab(self.tab_eco, "Ecosystem && Apps")

        tab_map = {
            "profile": 0,
            "accent": 0,
            "opacity": 1,
            "transparency": 1,
            "depth": 1,
            "a11y": 2,
            "accessibility": 2,
            "motion": 2,
            "health": 3,
            "doctor": 3,
            "ecosystem": 4,
            "apps": 4,
        }
        if initial_tab and initial_tab.lower() in tab_map:
            self.tabs.setCurrentIndex(tab_map[initial_tab.lower()])

        main_layout.addWidget(self.tabs)

        # Apply initial dynamic theme from active status
        status = noxforge_ctl.get_current_status()
        init_prof = status.get("profile", "graphite")
        if init_prof not in ("graphite", "obsidian"):
            init_prof = "graphite"
        init_acc = status.get("accentHex", "#A3FF47")
        self.refresh_theme(init_prof, init_acc)

        # Status Bar
        self.statusBar().showMessage(f"NoxForge Control Center v{APP_VERSION} ready.")

    def refresh_theme(self, profile: str = "graphite", accent_hex: str = "#A3FF47") -> None:
        """Dynamically re-skin the Control Center GUI to match the active profile and accent."""
        self.active_profile = profile.lower() if profile.lower() in ("graphite", "obsidian") else "graphite"
        pal = noxforge_core.resolve_accent_palette(
            accent_hex or "#A3FF47", is_obsidian=(self.active_profile == "obsidian")
        )
        self.active_accent_hex = pal["accent"]
        surf_sel = pal["surfaceSelected"]
        qss = noxforge_core.build_qt_stylesheet(profile=self.active_profile, accent_hex=self.active_accent_hex)
        self.setStyleSheet(qss)

        self.header_title_lbl.setStyleSheet(
            f"font-size: 13px; font-weight: 800; color: {self.active_accent_hex}; letter-spacing: 0.8px;"
        )
        prof_label = "OBSIDIAN OLED" if self.active_profile == "obsidian" else "GRAPHITE"
        self.header_profile_badge.setText(f"● {prof_label}")
        self.header_profile_badge.setStyleSheet(
            f"background-color: {surf_sel}; color: #E8F0F2; border: 1px solid {self.active_accent_hex}; "
            "border-radius: 4px; padding: 3px 8px; font-size: 11px; font-weight: 700;"
        )
        self.header_accent_badge.setText(f"● {self.active_accent_hex}")
        self.header_accent_badge.setStyleSheet(
            f"background-color: {self.active_accent_hex}; color: {pal['accentInk']}; "
            "border-radius: 4px; padding: 3px 8px; font-size: 11px; font-weight: 800;"
        )

        if hasattr(self.opacity_window, "refresh_theme"):
            self.opacity_window.refresh_theme(self.active_profile, self.active_accent_hex)
        self.tab_profile.refresh_state()
        self.tab_a11y.refresh_state()
        self.tab_eco.refresh_table()

    def export_preset_dialog(self) -> None:
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Export NoxForge Preset",
            str(Path.home() / "noxforge-preset.json"),
            "JSON Files (*.json)",
        )
        if path and hasattr(noxforge_ctl, "export_preset"):
            noxforge_ctl.export_preset(path)
            self.show_status(f"Exported NoxForge preset to {path}")

    def import_preset_dialog(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Import NoxForge Preset",
            str(Path.home()),
            "JSON Files (*.json)",
        )
        if path and hasattr(noxforge_ctl, "import_preset"):
            try:
                res = noxforge_ctl.import_preset(path)
                self.refresh_theme(res.get("profile", "graphite"), res.get("accentHex", "#A3FF47"))
                self.show_status(f"Imported NoxForge preset from {path}")
            except Exception as err:
                self.show_status(f"Error importing preset: {err}")

    def show_status(self, msg: str) -> None:
        self.statusBar().showMessage(msg, 5000)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NoxForge Control Center")
    parser.add_argument(
        "--tab",
        choices=[
            "profile",
            "accent",
            "opacity",
            "transparency",
            "depth",
            "a11y",
            "accessibility",
            "motion",
            "health",
            "doctor",
            "ecosystem",
            "apps",
        ],
        default=None,
        help="Initial tab to display",
    )
    parser.add_argument("-v", "--version", action="version", version=f"control-center {APP_VERSION}")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    win = ControlCenterWindow(initial_tab=args.tab)
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
