# NoxForge 11 compatibility

The intended compatibility target is Fedora 44 KDE and the target Arch
Plasma/KWin 6.7+ and Qt 6.11 family on Wayland. The project makes no X11,
Plasma 6.0, Debian, Ubuntu, openSUSE, Nix, Flatpak, or AppImage claim.

## System package roots

| Component | Installed path |
| --- | --- |
| Global Theme | `/usr/share/plasma/look-and-feel/io.github.loofiboss.noxforge.desktop/` |
| Plasma Style | `/usr/share/plasma/desktoptheme/io.github.loofiboss.noxforge.desktop/` |
| Color scheme | `/usr/share/color-schemes/NoxForgeDark.colors` |
| Obsidian color scheme | `/usr/share/color-schemes/NoxForgeObsidian.colors` |
| Konsole themes | `/usr/share/konsole/NoxForge{,Obsidian}.colorscheme` |
| Aurorae | `/usr/share/aurorae/themes/io.github.loofiboss.noxforge.desktop/` |
| KWin switcher | `/usr/share/kwin/tabbox/io.github.loofiboss.noxforge.desktop/` |
| Icons | `/usr/share/icons/NoxForge/` |
| Cursors | `/usr/share/icons/NoxForge-Cursors/` |
| Sounds | `/usr/share/sounds/NoxForge/` |
| Wallpapers | `/usr/share/wallpapers/NoxForge{,-Quiet,-Ultrawide}/` |
| Qt style plugin | `/usr/lib64/qt6/plugins/styles/libnoxforge6.so` |
| PLM wallpaper asset | `/usr/share/wallpapers/NoxForge-Quiet/` |
| SDDM compatibility theme | `/usr/share/sddm/themes/NoxForge/` |
| Doctor | `/usr/bin/noxforge-doctor` |

Store and portable packages use Breeze application controls and install
components separately. The complete-system edition adds the native Qt style;
the doctor reports a portable installation as `ok` without Qt or login-manager
integration.

## Login managers

Fedora 44 defaults to Plasma Login Manager. NoxForge supports PLM only through
its standard wallpaper surface; arbitrary PLM QML themes are not supported.
NoxForge Quiet is the recommended asset, but it is never selected automatically.
The packaged SDDM theme supports upgraded Fedora systems that still use SDDM.
The Arch qualification journey uses optional SDDM. An installed SDDM theme does not imply that SDDM
is active.

KPackage metadata is at the Global Theme and Plasma Style archive roots, and
all packages reject symlinks. Installation, upgrade, and removal do not apply
NoxForge, edit KDE/PLM/SDDM configuration, or switch display managers.

The v11 local gate passes all 72 offscreen CTest cases on Fedora 44 with
Qt 6.11.2 and Plasma/KWin 6.7.4, plus the generated Store/portable and RPM
contracts. Arch build/live login and hardware qualification remain pending;
offscreen results do not establish those behaviors. See the active
[qualification record](evidence/v11/qualification.json).
