# Quick start and rollback

NoxForge 9 System Coherence targets Fedora 44 KDE and the verified Arch Plasma /
KWin 6.7+ and Qt 6.11 environment on Wayland. Choose the edition that matches
your boundary.

## Fedora complete-system edition

```bash
sudo dnf install noxforge
rpm -V noxforge
noxforge-doctor --json
```

The RPM installs the native Qt style and system doctor but never applies a
theme, changes a panel, edits KDE configuration, or switches a display manager.
Fedora 44 uses Plasma Login Manager by default: select **NoxForge Quiet** as its
wallpaper through System Settings if desired. NoxForge does not supply a custom
PLM greeter. Select
Global Theme, application style, decorations, icons, cursors, sounds and one
of the three wallpapers explicitly in System Settings.

## Portable user-local edition

```bash
tar -xJf noxforge-9.0.0-portable.tar.xz
cd noxforge
./scripts/install.sh --user --dry-run
./scripts/install.sh --user
"${XDG_DATA_HOME:-$HOME/.local/share}/noxforge/bin/noxforge-doctor" --json
```

Portable installs all user-local components, uses Breeze application controls,
and writes no active KDE settings. Store components can likewise be installed
individually; the Global Theme package is not a complete transaction.

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
