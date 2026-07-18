# Plasma 6 compatibility record

Verified structurally on 2026-07-18 against Fedora KDE 44: Plasma/KWin 6.7.3,
KDE Frameworks 6.28 and Qt 6.11.1. Plasma 5, Qt 5 and legacy metadata are not
supported.

## Package contracts

| Component | Installed path |
| --- | --- |
| Global Theme | `~/.local/share/plasma/look-and-feel/io.github.loofiboss.noxforge.desktop/` |
| Plasma Style | `~/.local/share/plasma/desktoptheme/io.github.loofiboss.noxforge.desktop/` |
| Color scheme | `~/.local/share/color-schemes/NoxForgeDark.colors` |
| Aurorae | `~/.local/share/aurorae/themes/io.github.loofiboss.noxforge.desktop/` |
| KWin switcher | `~/.local/share/kwin/tabbox/io.github.loofiboss.noxforge.desktop/` |
| Icons | `~/.local/share/icons/NoxForge/` |
| Cursors | `~/.local/share/icons/NoxForge-Cursors/` |
| Sounds | `~/.local/share/sounds/NoxForge/` |
| Wallpaper | `~/.local/share/wallpapers/NoxForge/` |
| Qt style plugin | `/usr/lib64/qt6/plugins/styles/libnoxforge6.so` |
| SDDM | `/usr/share/sddm/themes/NoxForge/` |

The Look-and-Feel package declares `Plasma/LookAndFeel`; the task switcher
declares `KWin/WindowSwitcher`. Packages contain no symlinks. The icon theme
inherits only `hicolor`, and the Plasma Style declares no explicit fallback.

The Qt style is a native `QCommonStyle`/`QStylePlugin` implementation with the
public key `NoxForge`. It does not link against Breeze or Kvantum.

Offscreen SDDM test-mode startup passes. Live Wayland, scaling, interactive
SDDM and visual fallback checks remain recorded in `docs/MANUAL_TESTING.md`;
structural validation cannot mark them passed.

## Sources

- <https://develop.kde.org/docs/plasma/theme/theme-porting-to-plasma6/>
- <https://develop.kde.org/docs/plasma/>
- <https://doc.qt.io/QT-6/qstyleplugin.html>
- <https://doc.qt.io/qt-6/style-reference.html>
