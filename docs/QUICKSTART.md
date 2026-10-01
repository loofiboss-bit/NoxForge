# Quick start and rollback

NoxForge 14.0.0 targets Fedora 44 KDE and Arch Plasma/KWin 6.7+ with Qt 6.11 on
Wayland. Graphite and Obsidian variants cover the Plasma Style, Global Theme,
Lock Screen, Aurorae decoration, KWin switcher, native Qt style, wallpapers,
and editor/terminal themes. It includes the unified `noxforge-ctl` CLI and
Control Center GUI alongside the `noxforge-opacity` transparency configurator.
Choose the edition that matches your installation boundary.

## Fedora complete-system edition

Use the Fedora 44 COPR repository `loofitheboss/noxforge`. Verify the installed
version with `rpm -q noxforge`; repository metadata may need refreshing after
an upgrade is published.

```bash
sudo dnf copr enable loofitheboss/noxforge
sudo dnf install --refresh noxforge
rpm -V noxforge
noxforge-doctor --json
```

The RPM installs the native Qt style, orchestration suite (`noxforge-ctl`,
Control Center GUI), and system doctor but never automatically applies a
theme, changes a panel, edits KDE configuration, or switches a display manager.
Fedora 44 uses Plasma Login Manager by default: select **NoxForge Quiet** as its
wallpaper through System Settings if desired. NoxForge does not supply a custom
PLM greeter. Select
Global Theme, application style, decorations, icons, cursors, sounds and one
of the five wallpapers explicitly in System Settings, or orchestrate via
`noxforge-ctl` / Control Center.

## Portable user-local edition

```bash
tar -xJf noxforge-14.0.0-portable.tar.xz
cd noxforge
./scripts/install.sh --user --dry-run
./scripts/install.sh --user
"${XDG_DATA_HOME:-$HOME/.local/share}/noxforge/bin/noxforge-doctor" --json
```

Portable installs all user-local components, including both palette variants
of the GTK, syntax, editor, and terminal assets. It uses Breeze application
controls and writes no active KDE settings. Store components can likewise be
installed individually; the Global Theme package is not a complete transaction.

## Build locally

```bash
python3 scripts/release-check.py --skip-rpm
python3 scripts/build.py --mode all --skip-tests
```

## Roll back

Select another theme and login surface first. For portable, use the matching
bundle's uninstaller:

```bash
./scripts/uninstall.sh --user --dry-run
./scripts/uninstall.sh --user
```

For Fedora, remove only the package-owned files:

```bash
sudo dnf remove --no-autoremove noxforge
```

Neither path changes active settings or prunes unrelated KDE dependencies.
