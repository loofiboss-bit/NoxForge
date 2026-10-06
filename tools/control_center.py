#!/usr/bin/env python3
"""NoxForge Control Center - Qt 6 Graphical Hub.

Unifies profile switching (Graphite <-> Obsidian), accent color management,
depth & opacity configuration, and system diagnostics into a modern tabbed hub.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from PySide6 import QtCore, QtGui, QtWidgets

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
for p in (str(SCRIPT_DIR), str(ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

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

STYLE_SHEET = opacity_gui.STYLE_SHEET + """
QTabWidget::pane {
    border: 1px solid #2F414B;
    background-color: #0D1419;
    border-radius: 6px;
    top: -1px;
}

QTabBar::tab {
    background-color: #141E25;
    color: #A6B4B9;
    border: 1px solid #2F414B;
    border-bottom: none;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    padding: 8px 18px;
    margin-right: 4px;
    font-weight: 600;
    font-size: 12px;
}

QTabBar::tab:selected {
    background-color: #1B2831;
    color: #E8F0F2;
    border-top: 2px solid #A3FF47;
}

QTabBar::tab:hover:!selected {
    background-color: #22323B;
    color: #E8F0F2;
}
"""


class ProfileAccentTab(QtWidgets.QWidget):
    statusChanged = QtCore.Signal(str)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Profile Switcher Section
        profile_group = QtWidgets.QGroupBox("Skrivbordsprofil (KDE, GTK & Terminals)")
        p_layout = QtWidgets.QVBoxLayout(profile_group)

        desc = QtWidgets.QLabel("Växla mellan standard grafitgrå ytor och sann pitch-black OLED-svärta med ett klick:")
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
        layout.addWidget(profile_group)

        # Accent Color Section
        accent_group = QtWidgets.QGroupBox("Forge Accent Matrix")
        a_layout = QtWidgets.QVBoxLayout(accent_group)

        a_desc = QtWidgets.QLabel("Välj signaturaccentfärg för kontroller, fokusramar och notch-markeringar:")
        a_desc.setStyleSheet("color: #A6B4B9; margin-bottom: 8px;")
        a_layout.addWidget(a_desc)

        accent_grid = QtWidgets.QGridLayout()
        self.accent_buttons: dict[str, QtWidgets.QPushButton] = {}
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
            accent_grid.addWidget(btn, idx // 2, idx % 2)

        a_layout.addLayout(accent_grid)
        layout.addWidget(accent_group)

        # Live Icon & Kinetic Motion Preview Section (v15.0.0)
        preview_group = QtWidgets.QGroupBox("Live Ikon- & Rörelseförhandsgranskning (v15.0.0 Adaptive Vector Suite)")
        prev_layout = QtWidgets.QVBoxLayout(preview_group)

        prev_desc = QtWidgets.QLabel("Adaptiva vektorsymboler (Wi-Fi 0%–100%, Batteri, Ljud) och kinetisk skakningstest:")
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
            ("Frånkopplad", ROOT / "icons/NoxForge/scalable/status/network-wireless-disconnected.svg"),
            ("Batteri", ROOT / "icons/NoxForge/scalable/status/battery-100.svg"),
            ("Ljud", ROOT / "icons/NoxForge/scalable/status/audio-volume-high.svg"),
        ]

        for title, svg_path in icon_samples:
            col = QtWidgets.QVBoxLayout()
            col.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            img_lbl = QtWidgets.QLabel()
            img_lbl.setFixedSize(36, 36)
            img_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            img_lbl.setStyleSheet("background-color: #10191F; border: 1px solid #2F414B; border-radius: 6px; padding: 4px;")
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
        self.test_box = QtWidgets.QLineEdit("Lösenordsprov / Feltest")
        self.test_box.setReadOnly(True)
        self.test_box.setStyleSheet(
            "background-color: #10191F; border: 1px solid #2F414B; border-radius: 5px; "
            "color: #E8F0F2; padding: 6px 12px; font-size: 12px;"
        )
        self.btn_test_shake = QtWidgets.QPushButton("Testa Kinetisk Skakning (220ms)")
        self.btn_test_shake.setMinimumHeight(32)
        self.btn_test_shake.clicked.connect(self.play_test_shake)

        motion_row.addWidget(self.test_box, stretch=1)
        motion_row.addWidget(self.btn_test_shake)
        prev_layout.addLayout(motion_row)

        layout.addWidget(preview_group)

        # Day/Night Automation Section
        sched_group = QtWidgets.QGroupBox("Dag / Natt Automatisering")
        s_layout = QtWidgets.QHBoxLayout(sched_group)
        self.sched_check = QtWidgets.QCheckBox("Aktivera automatisk profilväxling: Graphite (07:00) / Obsidian (20:00)")
        self.sched_check.setStyleSheet("color: #E8F0F2; font-weight: 500;")
        self.sched_check.toggled.connect(self.toggle_schedule)
        s_layout.addWidget(self.sched_check)
        layout.addWidget(sched_group)

        layout.addStretch()
        self.refresh_state()

    def play_test_shake(self) -> None:
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
            "background-color: #1A1215; border: 2px solid #FF6B7A; border-radius: 5px; "
            "color: #FF6B7A; padding: 6px 12px; font-size: 12px; font-weight: bold;"
        )
        def restore():
            self.test_box.setStyleSheet(
                "background-color: #10191F; border: 1px solid #2F414B; border-radius: 5px; "
                "color: #E8F0F2; padding: 6px 12px; font-size: 12px;"
            )
            self.test_box.setGeometry(orig_rect)
        anim.finished.connect(restore)
        self._shake_anim = anim
        anim.start()

    def refresh_state(self) -> None:
        status = noxforge_ctl.get_current_status()
        profile = status.get("profile", "graphite")
        if profile == "obsidian":
            self.btn_obsidian.setStyleSheet("background-color: #1A2E20; border: 2px solid #A3FF47; color: #FFFFFF; font-weight: bold;")
            self.btn_graphite.setStyleSheet("")
        else:
            self.btn_graphite.setStyleSheet("background-color: #1A2E20; border: 2px solid #A3FF47; color: #FFFFFF; font-weight: bold;")
            self.btn_obsidian.setStyleSheet("")

        # Update preview badges
        if hasattr(self, "preview_badges"):
            for img_lbl, _, svg_path in self.preview_badges:
                if svg_path.is_file():
                    img_lbl.setPixmap(QtGui.QIcon(str(svg_path)).pixmap(24, 24))

        sched = noxforge_ctl.manage_schedule("status")
        self.sched_check.blockSignals(True)
        self.sched_check.setChecked(sched.get("scheduled", False))
        self.sched_check.blockSignals(False)

    def apply_profile(self, profile: str) -> None:
        res = noxforge_ctl.switch_profile(profile)
        self.refresh_state()
        self.statusChanged.emit(f"Profil aktiverad: {profile.upper()}")

    def apply_accent(self, accent: str) -> None:
        res = noxforge_ctl.set_accent(accent)
        self.refresh_state()
        self.statusChanged.emit(f"Accentfärg aktiverad: {accent.upper()}")

    def toggle_schedule(self, checked: bool) -> None:
        action = "enable" if checked else "disable"
        noxforge_ctl.manage_schedule(action)
        self.statusChanged.emit(f"Dag/Natt-automatisering: {action.upper()}")


class HealthTab(QtWidgets.QWidget):
    statusChanged = QtCore.Signal(str)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        header = QtWidgets.QLabel("NoxForge Systemhälsa & Ekosystemstatus")
        header.setStyleSheet("font-size: 15px; font-weight: bold; color: #E8F0F2;")
        layout.addWidget(header)

        self.info_text = QtWidgets.QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet(
            "background-color: #10191F; border: 1px solid #2F414B; border-radius: 6px; "
            "font-family: monospace; font-size: 11px; padding: 10px; color: #A6B4B9;"
        )
        layout.addWidget(self.info_text)

        btn_row = QtWidgets.QHBoxLayout()
        self.btn_refresh = QtWidgets.QPushButton("Kör hälsokontroll (Doctor)")
        self.btn_refresh.clicked.connect(self.run_doctor)
        self.btn_sync = QtWidgets.QPushButton("Synkronisera hela skrivbordet")
        self.btn_sync.setStyleSheet("background-color: #A3FF47; color: #0D1419; font-weight: bold;")
        self.btn_sync.clicked.connect(self.align_desktop)

        btn_row.addWidget(self.btn_refresh)
        btn_row.addWidget(self.btn_sync)
        layout.addLayout(btn_row)

        self.run_doctor()

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
            self.info_text.setPlainText("Kunde inte hitta noxforge-doctor verktyget.")
            return
        try:
            res = subprocess.run([sys.executable, str(tool_doctor), "--json"], capture_output=True, text=True, check=False)
            data = json.loads(res.stdout)
            status = data.get("status", "ok")
            missing = data.get("missing", [])
            edition = data.get("edition", {}).get("kind", "portable")
            eco = data.get("ecosystem", {})
            flatpak = eco.get("flatpakThemesOverride", "ok")
            palette_sync = data.get("paletteSynchronization", {}).get("status", "synchronized")

            text = f"=== NOXFORGE DOCTOR RAPPORT ===\n"
            text += f"Status: {status.upper()}\n"
            text += f"Utgåva: {edition}\n"
            text += f"Paketversion: {data.get('packageVersion') or 'lokal / källa'}\n"
            text += f"Palettsynkronisering: {palette_sync.upper()}\n"
            text += f"Flatpak-temaåtkomst: {flatpak}\n"
            text += f"Saknade komponenter: {len(missing)}\n"
            if missing:
                text += f"  - " + "\n  - ".join(missing) + "\n"
            self.info_text.setPlainText(text)
        except Exception as err:
            self.info_text.setPlainText(f"Kunde inte köra noxforge-doctor: {err}")

    def align_desktop(self) -> None:
        status = noxforge_ctl.get_current_status()
        profile = status.get("profile", "graphite")
        if profile not in ("graphite", "obsidian"):
            profile = "graphite"
        noxforge_ctl.switch_profile(profile)
        self.run_doctor()
        self.statusChanged.emit(f"Hela skrivbordet synkroniserat till {profile.upper()}!")


class ControlCenterWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("NoxForge Control Center")
        self.setMinimumSize(880, 680)
        self.setStyleSheet(STYLE_SHEET)

        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Tab Widget
        self.tabs = QtWidgets.QTabWidget()
        
        # Tab 1: Profile & Accent Hub
        self.tab_profile = ProfileAccentTab()
        self.tab_profile.statusChanged.connect(self.show_status)
        self.tabs.addTab(self.tab_profile, "Profil & Accent")

        # Tab 2: Opacity & Depth Configurator
        self.opacity_window = opacity_gui.OpacityConfiguratorWindow()
        # Embed opacity central widget into tab
        opacity_inner = self.opacity_window.centralWidget()
        self.tabs.addTab(opacity_inner, "Transparens & Djup")

        # Tab 3: Health & Diagnostics
        self.tab_health = HealthTab()
        self.tab_health.statusChanged.connect(self.show_status)
        self.tabs.addTab(self.tab_health, "Systemhälsa & Doctor")

        main_layout.addWidget(self.tabs)

        # Status Bar
        self.statusBar().showMessage("NoxForge Control Center v14.0.0 redo.")

    def show_status(self, msg: str) -> None:
        self.statusBar().showMessage(msg, 5000)


def main() -> int:
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    win = ControlCenterWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
