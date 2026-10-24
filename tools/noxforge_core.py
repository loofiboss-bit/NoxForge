#!/usr/bin/env python3
"""NoxForge Shared Core Library (noxforge_core).

Provides single-source version resolution, XDG directory discovery, KDE KConfig
readers/writers, WCAG 2.1 contrast calculation, dynamic accent color derivation,
and real-time Qt 6 stylesheet generation across NoxForge CLI and GUI tools.
"""

from __future__ import annotations

import configparser
import os
import shutil
import subprocess
from pathlib import Path

DEFAULT_VERSION = "18.0.0"

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent

THEME_GRAPHITE_ID = "io.github.loofiboss.noxforge.desktop"
THEME_OBSIDIAN_ID = "io.github.loofiboss.noxforge.obsidian.desktop"

ACCENT_COLORS: dict[str, str] = {
    "lime": "#A3FF47",
    "cyan": "#22D3EE",
    "violet": "#A78BFA",
    "amber": "#FBBF24",
}

ACCENT_PRESSED: dict[str, str] = {
    "lime": "#82D936",
    "cyan": "#06B6D4",
    "violet": "#8B5CF6",
    "amber": "#F59E0B",
}

ACCENT_SURFACE_SELECTED: dict[str, tuple[str, str]] = {
    "lime": ("#223429", "#192D1E"),
    "cyan": ("#15313B", "#0E242C"),
    "violet": ("#26203D", "#1B152E"),
    "amber": ("#332918", "#261D0E"),
}

GRAPHITE_SURFACE = "#141E25"
OBSIDIAN_SURFACE = "#000000"


def get_app_version(fallback: str = DEFAULT_VERSION) -> str:
    """Resolve active NoxForge version from repo or installed system paths."""
    candidates = [
        ROOT / "VERSION",
        SCRIPT_DIR.parent / "VERSION",
        Path("/usr/share/noxforge/VERSION"),
        Path.home() / ".local/share/noxforge/VERSION",
    ]
    for path in candidates:
        if path.is_file():
            try:
                version = path.read_text(encoding="utf-8").strip()
                if version:
                    return version
            except OSError:
                pass
    return fallback


def get_xdg_config_home() -> Path:
    env = os.environ.get("XDG_CONFIG_HOME")
    if env and env.startswith("/"):
        return Path(env)
    return Path.home() / ".config"


def get_xdg_data_home() -> Path:
    env = os.environ.get("XDG_DATA_HOME")
    if env and env.startswith("/"):
        return Path(env)
    return Path.home() / ".local/share"


def get_xdg_cache_home() -> Path:
    env = os.environ.get("XDG_CACHE_HOME")
    if env and env.startswith("/"):
        return Path(env)
    return Path.home() / ".cache"


def get_kde_config_dir() -> Path:
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config)
    return Path.home() / ".config"


def run_cmd(cmd: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def read_kconfig(file_name: str, group: str, key: str, fallback: str = "") -> str:
    reader = shutil.which("kreadconfig6") or shutil.which("kreadconfig5") or shutil.which("kreadconfig")
    if reader:
        try:
            res = subprocess.run(
                [reader, "--file", file_name, "--group", group, "--key", key],
                capture_output=True,
                text=True,
                check=False,
            )
            val = res.stdout.strip()
            if val:
                return val
        except Exception:
            pass
    path = get_kde_config_dir() / file_name
    if not path.is_file():
        return fallback
    parser = configparser.ConfigParser(interpolation=None, strict=False)
    parser.optionxform = str  # type: ignore[assignment]
    try:
        parser.read(path, encoding="utf-8")
        return parser.get(group, key, fallback=fallback)
    except Exception:
        return fallback


def write_kconfig(file_name: str, group: str, key: str, value: str) -> None:
    if shutil.which("kwriteconfig6"):
        run_cmd(["kwriteconfig6", "--file", file_name, "--group", group, "--key", key, str(value)])
        return
    path = get_kde_config_dir() / file_name
    path.parent.mkdir(parents=True, exist_ok=True)
    parser = configparser.ConfigParser(interpolation=None, strict=False)
    parser.optionxform = str  # type: ignore[assignment]
    if path.is_file():
        try:
            parser.read(path, encoding="utf-8")
        except Exception:
            pass
    if not parser.has_section(group):
        parser.add_section(group)
    parser.set(group, key, str(value))
    with path.open("w", encoding="utf-8") as handle:
        parser.write(handle)


def delete_kconfig(file_name: str, group: str, key: str) -> None:
    if shutil.which("kwriteconfig6"):
        run_cmd(["kwriteconfig6", "--file", file_name, "--group", group, "--key", key, "--delete", ""])
        return
    path = get_kde_config_dir() / file_name
    if not path.is_file():
        return
    parser = configparser.ConfigParser(interpolation=None, strict=False)
    parser.optionxform = str  # type: ignore[assignment]
    try:
        parser.read(path, encoding="utf-8")
        if parser.has_section(group) and parser.has_option(group, key):
            parser.remove_option(group, key)
            with path.open("w", encoding="utf-8") as handle:
                parser.write(handle)
    except Exception:
        pass


def hex_to_rgb_tuple(hex_color: str) -> tuple[int, int, int]:
    clean = hex_color.strip().lstrip("#")
    if len(clean) != 6:
        return (163, 255, 71)
    return (int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16))


def blend_hex(fg_hex: str, bg_hex: str, alpha: float) -> str:
    fr, fg, fb = hex_to_rgb_tuple(fg_hex)
    br, bg, bb = hex_to_rgb_tuple(bg_hex)
    r = max(0, min(255, round(fr * alpha + br * (1.0 - alpha))))
    g = max(0, min(255, round(fg * alpha + bg * (1.0 - alpha))))
    b = max(0, min(255, round(fb * alpha + bb * (1.0 - alpha))))
    return f"#{r:02X}{g:02X}{b:02X}"


def relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first: str, second: str) -> float:
    light, dark = sorted(
        (relative_luminance(first), relative_luminance(second)),
        reverse=True,
    )
    return (light + 0.05) / (dark + 0.05)


def validate_custom_accent_contrast(hex_code: str) -> tuple[float, float]:
    clean_hex = hex_code.strip()
    if (
        not clean_hex.startswith("#")
        or len(clean_hex) != 7
        or not all(c in "0123456789abcdefABCDEF" for c in clean_hex[1:])
    ):
        raise ValueError(f"Invalid hex color format: {hex_code!r}. Must be '#RRGGBB'.")
    c_graphite = contrast_ratio(clean_hex, GRAPHITE_SURFACE)
    c_obsidian = contrast_ratio(clean_hex, OBSIDIAN_SURFACE)
    if c_graphite < 4.5 or c_obsidian < 4.5:
        raise ValueError(
            f"Custom accent {clean_hex} fails WCAG AA 4.5:1 contrast requirement. "
            f"Contrast on Graphite (#141E25): {c_graphite:.2f}:1, "
            f"Contrast on Obsidian (#000000): {c_obsidian:.2f}:1."
        )
    return c_graphite, c_obsidian


def resolve_accent_palette(accent_key_or_hex: str, is_obsidian: bool = False) -> dict[str, str]:
    """Return harmonized accent tokens (accent, accentPressed, accentInk, surfaceSelected)."""
    key = (accent_key_or_hex or "lime").strip().lower()
    matched_matrix_key = key if key in ACCENT_COLORS else next(
        (k for k, v in ACCENT_COLORS.items() if v.lower() == key),
        None,
    )
    if matched_matrix_key:
        accent_hex = ACCENT_COLORS[matched_matrix_key]
        pressed_hex = ACCENT_PRESSED[matched_matrix_key]
        sel_g, sel_o = ACCENT_SURFACE_SELECTED[matched_matrix_key]
        selected_hex = sel_o if is_obsidian else sel_g
    elif key.startswith("#") and len(key) == 7:
        accent_hex = key.upper()
        pressed_hex = blend_hex(accent_hex, "#000000", 0.82)
        base_surface = OBSIDIAN_SURFACE if is_obsidian else GRAPHITE_SURFACE
        selected_hex = blend_hex(accent_hex, base_surface, 0.16)
    else:
        accent_hex = ACCENT_COLORS["lime"]
        pressed_hex = ACCENT_PRESSED["lime"]
        sel_g, sel_o = ACCENT_SURFACE_SELECTED["lime"]
        selected_hex = sel_o if is_obsidian else sel_g

    ink_hex = "#000000" if is_obsidian else "#0D1419"
    return {
        "accent": accent_hex,
        "accentPressed": pressed_hex,
        "accentInk": ink_hex,
        "surfaceSelected": selected_hex,
    }


def build_qt_stylesheet(profile: str = "graphite", accent_hex: str = "#A3FF47") -> str:
    """Generate dynamic Qt 6 stylesheet adapting to Graphite/Obsidian and active accent."""
    is_obsidian = profile.strip().lower() == "obsidian"
    bg_canvas = "#000000" if is_obsidian else "#0D1419"
    bg_sunken = "#05080A" if is_obsidian else "#10191F"
    bg_surface = "#0A0F13" if is_obsidian else "#141E25"
    bg_raised = "#121B21" if is_obsidian else "#1B2831"
    bg_hover = "#202E38" if is_obsidian else "#283942"

    pal = resolve_accent_palette(accent_hex, is_obsidian=is_obsidian)
    acc = pal["accent"]
    acc_pressed = pal["accentPressed"]
    acc_ink = pal["accentInk"]
    surf_sel = pal["surfaceSelected"]
    acc_hover = blend_hex("#FFFFFF", acc, 0.18)

    return f"""
QWidget {{
    background-color: {bg_canvas};
    color: #E8F0F2;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans", sans-serif;
    font-size: 13px;
}}

QGroupBox {{
    background-color: {bg_surface};
    border: 1px solid #2F414B;
    border-radius: 6px;
    margin-top: 20px;
    padding: 16px 12px 12px 12px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: #A6B4B9;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QPushButton {{
    background-color: {bg_raised};
    color: #E8F0F2;
    border: 1px solid #2F414B;
    border-radius: 5px;
    padding: 7px 14px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {bg_hover};
    border-color: #4B606A;
}}

QPushButton:pressed {{
    background-color: {bg_sunken};
}}

QPushButton:disabled {{
    color: #55636A;
    border-color: {bg_raised};
}}

QPushButton.presetBtn {{
    text-align: left;
    padding: 7px 10px;
    font-size: 11px;
    border-radius: 5px;
}}

QPushButton.presetBtnActive {{
    border: 1px solid {acc};
    background-color: {surf_sel};
    color: #FFFFFF;
}}

QPushButton#applyButton {{
    background-color: {acc};
    color: {acc_ink};
    font-weight: 700;
    font-size: 14px;
    border: none;
    border-radius: 6px;
    padding: 10px 24px;
}}

QPushButton#applyButton:hover {{
    background-color: {acc_hover};
}}

QPushButton#applyButton:pressed {{
    background-color: {acc_pressed};
}}

QSlider {{
    min-height: 26px;
}}

QSlider::groove:horizontal {{
    height: 6px;
    background: {bg_sunken};
    border: 1px solid #2F414B;
    border-radius: 3px;
}}

QSlider::sub-page:horizontal {{
    background: {acc};
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: #E8F0F2;
    border: 2px solid {acc};
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 9px;
}}

QSlider::handle:horizontal:hover {{
    background: {acc};
    border-color: #FFFFFF;
}}

QComboBox {{
    background-color: {bg_raised};
    border: 1px solid #2F414B;
    border-radius: 5px;
    padding: 6px 12px;
    color: #E8F0F2;
}}

QComboBox:hover {{
    border-color: #4B606A;
}}

QComboBox QAbstractItemView {{
    background-color: {bg_surface};
    border: 1px solid #2F414B;
    selection-background-color: {surf_sel};
    selection-color: {acc};
}}

QLineEdit, QTimeEdit {{
    background-color: {bg_sunken};
    border: 1px solid #2F414B;
    border-radius: 5px;
    color: #E8F0F2;
    padding: 6px 10px;
}}

QLineEdit:focus, QTimeEdit:focus {{
    border: 1px solid {acc};
}}

QStatusBar {{
    background-color: {bg_sunken};
    color: #A6B4B9;
    border-top: 1px solid #1B2831;
    font-size: 12px;
}}

QTabWidget::pane {{
    border: 1px solid #2F414B;
    background-color: {bg_canvas};
    border-radius: 6px;
    top: -1px;
}}

QTabBar::tab {{
    background-color: {bg_surface};
    color: #A6B4B9;
    border: 1px solid #2F414B;
    border-bottom: none;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    padding: 8px 18px;
    margin-right: 4px;
    font-weight: 600;
    font-size: 12px;
}}

QTabBar::tab:selected {{
    background-color: {bg_raised};
    color: #E8F0F2;
    border-top: 2px solid {acc};
}}

QTabBar::tab:hover:!selected {{
    background-color: {bg_hover};
    color: #E8F0F2;
}}
"""
