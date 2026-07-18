# Quick start and rollback

NoxForge 2.0 targets Fedora KDE 44, Plasma 6.7+, Qt 6.11 and Wayland.

## Verify and build

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests
cmake -S . -B build/cmake -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build/cmake
ctest --test-dir build/cmake --output-on-failure
python3 scripts/build.py
```

## Install

Install data-only components for the current user:

```bash
./scripts/install.sh --user --dry-run
./scripts/install.sh --user
```

The native Qt style and SDDM must be discoverable system-wide. Preview the
exact targets, then run the separate installer through the administrator tool:

```bash
./scripts/install-system.sh --system --dry-run
sudo ./scripts/install-system.sh --system
```

Neither installer changes settings. Select **NoxForge** in System Settings →
Colors & Themes → Global Theme. The equivalent explicit command is:

```bash
plasma-apply-lookandfeel --apply io.github.loofiboss.noxforge.desktop
```

That command preserves the existing panel. Use `--resetLayout` only when the
optional NoxForge panel layout is deliberately wanted. Select the NoxForge
login screen separately in the SDDM settings page.

## Roll back

Select another Global Theme and login screen first, then remove only NoxForge
paths:

```bash
./scripts/uninstall.sh --user --dry-run
./scripts/uninstall.sh --user
./scripts/uninstall-system.sh --system --dry-run
sudo ./scripts/uninstall-system.sh --system
```

No script rewrites the active KDE or SDDM configuration.
