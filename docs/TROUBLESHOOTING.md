# Troubleshooting NoxForge 10

## Collect a read-only report

```bash
noxforge-doctor --json
# or for portable:
"${XDG_DATA_HOME:-$HOME/.local/share}/noxforge/bin/noxforge-doctor" --json
```

The report includes package/component discovery, the edition object, active
names that can be read safely, the stable `loginSurface` object, and a concise
session summary. It never writes
files, changes settings, applies a theme, clears caches, restarts services, or
requests privileges.

## Edition is mixed or incomplete

Read schema 3 `issues`, `edition.missingMandatory`, and each component's
`effectivePath` and `shadowedPaths`. Text output uses the same findings.

| Finding | Interpretation and next action |
| --- | --- |
| `missing-required` | Install the named Store dependency, rerun the matching portable installer, or repair the system package according to `edition.kind`. |
| `duplicate-identical` | Equivalent copies are present; review the shadowed path before removing an unwanted copy with its matching uninstaller or package manager. |
| `duplicate-conflict` | Payloads differ, even if versions match; retain the intended installation and remove only the identified conflicting copy. |
| `duplicate-unknown` | Contents could not be compared; inspect permissions and the listed paths before deciding what to remove. |
| `mixed-versions` | Reinstall the affected components from the same candidate or release. |
| `metadata-unknown` | Version metadata is unavailable; this informational finding alone does not make a component broken. |

A standalone component does not require the full suite. A Global Theme has
its declared component dependencies; portable and system editions require their
respective component sets. Native Qt and login assets are not portable
requirements. An active `widgetStyle=NoxForge` without the native plugin
requires selecting Breeze or installing the complete system package.

Do not infer the active Qt plugin from candidate file paths: its
`effectivePath` remains null. Doctor reports discovery, not runtime loader
proof. Never remove all user-local theme directories to resolve one finding.

## Inspect an isolated installation

```bash
noxforge-doctor --root /absolute/path/to/stage --json
```

`--root` reads version markers only inside that root. `expectedVersion: null`
means no valid marker was found; it never substitutes the source checkout's
version. Host session settings and runtime scale are not queried for a stage.

## System Settings does not refresh

Close and reopen System Settings, then log out and back in if discovery remains
stale. Cache removal is not part of installation or diagnosis. Verify the
selected components individually because KDE stores them in separate roots.

## Login surface is available but not selected

This is not an installation failure. For active PLM, `loginSurface` reports the
effective wallpaper after applying `/usr/lib` defaults, `/etc/plasmalogin.conf`,
and sorted `/etc/plasmalogin.conf.d` overrides. Select NoxForge Quiet manually
if desired. For active SDDM, the object reports the effective `Current` theme.
If PLM is active, an installed NoxForge SDDM theme remains only an available
compatibility asset.

## Roll back safely

Select a known-good Global Theme, application style, decoration, icons, cursors,
sounds, wallpaper, and login surface (if explicitly selected) before removal.
Portable rollback is file-precise:

```bash
./scripts/uninstall.sh --user --dry-run
./scripts/uninstall.sh --user
```

Fedora rollback is package-owned:

```bash
sudo dnf remove --no-autoremove noxforge
```
