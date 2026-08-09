# NoxForge 8 compatibility

The qualified compatibility target is Fedora 44 KDE and the verified Arch
Plasma/KWin 6.7+ and Qt 6.11 family on Wayland. The project makes no X11,
Plasma 6.0, Debian, Ubuntu, openSUSE, Nix, Flatpak, or AppImage claim.

## System package roots

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
| Wallpapers | `/usr/share/wallpapers/NoxForge{,-Quiet,-Ultrawide}/` |
| Qt style plugin | `/usr/lib64/qt6/plugins/styles/libnoxforge6.so` |
| SDDM (optional) | `/usr/share/sddm/themes/NoxForge/` |
| Doctor | `/usr/bin/noxforge-doctor` |

Store and portable packages use Breeze application controls and install
components separately. The complete-system edition adds the native Qt style;
the doctor reports a portable installation as `ok` without Qt or SDDM.

KPackage metadata is at the Global Theme and Plasma Style archive roots, and
all packages reject symlinks. Installation, upgrade, and removal do not apply
NoxForge or edit KDE/SDDM configuration.
