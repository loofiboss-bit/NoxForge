# Plasma 6 compatibility record

Verified structurally on 2026-07-18 against Fedora KDE 44: Plasma/KWin 6.7.3,
KDE Frameworks 6.28 and Qt 6.11.1. Plasma 5, Qt 5 and legacy metadata are not
supported.

## Package contracts

| Component | Installed path |
| --- | --- |
| Global Theme | `/usr/share/plasma/look-and-feel/io.github.loofiboss.noxforge.desktop/` |
| Plasma Style | `/usr/share/plasma/desktoptheme/io.github.loofiboss.noxforge.desktop/` |
| Color scheme | `/usr/share/color-schemes/NoxForgeDark.colors` |
| Aurorae | `/usr/share/aurorae/themes/io.github.loofiboss.noxforge.desktop/` |
| KWin switcher | `/usr/share/kwin/tabbox/io.github.loofiboss.noxforge.desktop/` |
| Icons | `/usr/share/icons/NoxForge/` |
| Cursors | `/usr/share/icons/NoxForge-Cursors/` |
| Sounds | `/usr/share/sounds/NoxForge/` |
| Wallpaper | `/usr/share/wallpapers/NoxForge/` |
| Qt style plugin | `/usr/lib64/qt6/plugins/styles/libnoxforge6.so` |
| SDDM | `/usr/share/sddm/themes/NoxForge/` |
| Doctor | `/usr/bin/noxforge-doctor` |

The Look-and-Feel package declares `Plasma/LookAndFeel`; the task switcher
declares `KWin/WindowSwitcher`. Packages contain no symlinks. The icon theme
inherits only `hicolor`, and the Plasma Style declares no explicit fallback.

The Qt style is a native `QCommonStyle`/`QStylePlugin` implementation with the
public key `NoxForge`. It does not link against Breeze or Kvantum.

Phase 6 isolated Wayland qualification passes theme application, panel
preservation, every panel edge, two virtual outputs, shell artwork, required
panel icons and real Qt composition at scale 1.0 and 1.4. Hardware blur,
input-driven keyboard/Aurorae/Alt+Tab/cursor cases, live RTL, isolated audio,
production splash integration and real SDDM authentication/power remain
`blocked` in `docs/evidence/v5/qualification.json`; structural evidence cannot
mark them passed. Completed v3 evidence remains under `docs/evidence/v3/` as
historical release evidence.

The Fedora RPM and CMake staging contract own system paths and contain no
installation scriptlets. Installation, upgrade and removal do not apply or
activate NoxForge and do not edit KDE or SDDM configuration. The legacy
user-local source installer remains a developer/migration fallback rather than
a competing production path.

The Aurorae generation contract is exercised with Python 3.12 and Fedora 44's
Python 3.14. Its `.svgz` files use a canonical gzip stream with a fixed
timestamp, empty filename, maximum compression and platform-neutral OS header,
so committed assets are byte-identical across these Python environments.

## Sources

- <https://develop.kde.org/docs/plasma/theme/theme-porting-to-plasma6/>
- <https://develop.kde.org/docs/plasma/>
- <https://doc.qt.io/QT-6/qstyleplugin.html>
- <https://doc.qt.io/qt-6/style-reference.html>
