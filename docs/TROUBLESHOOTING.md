# Troubleshooting NoxForge

This guide covers the NoxForge v6 Kinetic Precision release line.

## Collect a read-only report

Run:

```bash
noxforge-doctor
```

The command reports package and component discovery, versions, safely readable
active theme names, and a concise session summary. It does not write files,
change KDE settings, apply a theme, clear caches, restart services, or request
privileges. Attach its output to a bug report; it omits usernames, hostnames,
personal paths, and display contents.

## Motion does not follow the expected speed

NoxForge uses KDE and Qt's configured animation duration; it does not maintain
a separate animation-speed setting. Verify the global animation speed in
System Settings, then close and reopen the affected application or session
surface. At zero duration, focus, selection, busy, success, and error states
remain visible but settle immediately.

Do not edit QML files or clear caches to force reduced motion. If a surface
still animates at zero duration, collect `noxforge-doctor` output and report
the exact application or surface. Live animation-speed qualification remains
explicitly blocked until it can run in an isolated input-capable Wayland
session.

## A component is missing or versions are mixed

Remove older user-local source copies before reinstalling the RPM:

```bash
./scripts/uninstall.sh --user --dry-run
./scripts/uninstall.sh --user
sudo dnf reinstall noxforge
noxforge-doctor
```

Run the source uninstaller only from the matching source checkout and inspect
its dry-run output first. It removes only NoxForge user-data paths.

## System Settings does not refresh

First close and reopen System Settings. If discovery remains stale, log out and
back in. Cache removal is not performed by the package or doctor. Any manual
cache operation must be scoped to a confirmed KDE cache issue and should not be
used as a routine installation step.

## Roll back safely

Before removing NoxForge, select a known-good Global Theme, color scheme, icons,
cursors, application style, window decoration, task switcher, splash screen,
and sound theme in System Settings. If you explicitly activated the NoxForge
SDDM theme, restore a known-good SDDM theme before removal and verify its test
mode in a recoverable environment.

Then remove the package:

```bash
sudo dnf remove --no-autoremove noxforge
```

Removal deletes only RPM-owned files. It does not rewrite active KDE or SDDM
settings, which is why explicit rollback comes first. Dependency cleanup stays
disabled so DNF cannot remove KDE packages that were installed independently
or first encountered as NoxForge dependencies.
