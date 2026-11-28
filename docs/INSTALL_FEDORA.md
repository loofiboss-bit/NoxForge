# Install NoxForge on Fedora KDE

NoxForge 21.0.3 is a scriptlet-free Fedora 44 and Fedora 45 package for the complete-system
journey. It provides the event-driven native Qt 6 style (`QFileSystemWatcher`, 6 WCAG-AA accents,
custom `QPalette::Accent`), 10-module Plasma 6.8 Union CSS styles, the unified Control Center v6
suite (`noxforge-ctl` with live hot-reload, Wallpaper Accent Extractor & Named Presets + async
PySide6 GUI), Schema 14 system doctor, differentiated GTK 3/4 Libadwaita themes, Ecosystem v4
assets (25 apps including Fastfetch Kinetic Studio v2, Bat, Delta, Fzf, Eza, Wofi, Neovim, VS Code,
Zed, Yazi, Lazygit, Zellij, Tmux, btop, Starship, Firefox, and Discord), Duotone Surface icons
(482 scalable + 1,052 optical), 5-size 4× AA Xcursors + Plasma 6 scalable Wayland cursors, Tactile
Forge Audio v2, true PNG24 wallpapers (`16:10`, `32:9`, `images_dark/`), Aurorae v2 decorations,
canonical OSD & SystemDialog Look-and-Feel QML, Lock Screens, KWin switchers, `noxforge-opacity`,
and both SDDM theme variants.
Fedora 44 and 45 use Plasma Login Manager (PLM) by default. NoxForge Quiet is the
recommended standard PLM wallpaper; NoxForge does not ship a custom PLM greeter
or write PLM configuration.

Use the Fedora 44/45 COPR repository `loofitheboss/noxforge`. Verify the installed
version with `rpm -q noxforge`; repository metadata may need refreshing after
an upgrade is published.

```bash
sudo dnf copr enable loofitheboss/noxforge
sudo dnf install --refresh noxforge
rpm -V noxforge
noxforge-doctor --json
```

## Quick Start — Apply NoxForge

Package installation does not automatically apply NoxForge, change a panel, edit KDE
configuration, restart Plasma, install a display manager, or switch display
managers. To immediately apply the complete NoxForge experience:

```bash
# Apply Graphite (standard) or Obsidian (OLED) across theme, icons, cursors & wallpaper:
noxforge-ctl apply graphite
# Or with the optional floating panel desktop layout:
noxforge-ctl apply graphite --layout

# Or launch the graphical Control Center:
noxforge-ctl gui
```

### Dolphin & Desktop Clean Look

To get the clean, modern look featured in the showcase:
* **Dolphin:** Press `Ctrl+M` to hide the classic menubar (Dolphin will use the modern hamburger menu on the toolbar). In *Configure Dolphin → View Modes*, the vector icons scale cleanly in Icons mode.
* **Floating Panel:** In KDE Plasma 6, right-click the bottom panel → *Enter Edit Mode* → enable *Floating* (or use `noxforge-ctl apply --layout`).


## Build from the distributed source archive

```bash
tar -xJf noxforge-21.0.3-source.tar.xz
cd NoxForge-21.0.3
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build
DESTDIR="$PWD/stage" cmake --install build
```

The same source archive is the RPM Source0 input. Its archive root and checksum
are recorded in `SHA256SUMS`.

## Upgrade, rollback, and removal

```bash
sudo dnf upgrade --refresh noxforge
sudo dnf downgrade --refresh noxforge
sudo dnf remove --no-autoremove noxforge
```

Before rollback or removal, select a known-good Global Theme and restore a
known-good login wallpaper or SDDM theme if you explicitly activated one.
`rpm -V` and the doctor
are read-only checks; no scriptlet mutates user settings.
