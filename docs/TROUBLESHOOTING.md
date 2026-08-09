# Troubleshooting NoxForge 8

## Collect a read-only report

```bash
noxforge-doctor --json
# or for portable:
"${XDG_DATA_HOME:-$HOME/.local/share}/noxforge/bin/noxforge-doctor" --json
```

The report includes package/component discovery, the edition object, active
names that can be read safely, and a concise session summary. It never writes
files, changes settings, applies a theme, clears caches, restarts services, or
requests privileges.

## Edition is mixed or incomplete

Read `edition.missingMandatory` and `edition.shadowed`. Remove only an old
NoxForge user-local copy with the matching portable/source uninstaller, then
reinstall the selected component. An active `widgetStyle=NoxForge` without the
native plugin requires selecting Breeze or installing the complete system
package; it is not a portable failure.

## System Settings does not refresh

Close and reopen System Settings, then log out and back in if discovery remains
stale. Cache removal is not part of installation or diagnosis. Verify the
selected components individually because KDE stores them in separate roots.

## Roll back safely

Select a known-good Global Theme, application style, decoration, icons, cursors,
sounds, wallpaper, and SDDM theme (if explicitly selected) before removal.
Portable rollback is file-precise:

```bash
./scripts/uninstall.sh --user --dry-run
./scripts/uninstall.sh --user
```

Fedora rollback is package-owned:

```bash
sudo dnf remove --no-autoremove noxforge
```
