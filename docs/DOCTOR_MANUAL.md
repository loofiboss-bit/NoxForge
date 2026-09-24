# NoxForge doctor

`noxforge-doctor` is read-only. The portable invocation is
`$XDG_DATA_HOME/noxforge/bin/noxforge-doctor`; the complete-system invocation
is `/usr/bin/noxforge-doctor`.

Use `--json` for automation and `--root /absolute/staged/root` for an isolated
package tree or a portable data root. JSON schema 6 includes the top-level
`loginSurface`, `edition`, and `paletteSynchronization` objects.
`loginSurface` contains:

- `manager`: `plasmalogin`, `sddm`, `other`, or `not-detected`;
- `serviceState`: `active`, `inactive`, `unknown`, or `not-applicable`;
- `integration`: `wallpaper`, `custom-theme`, or `none`;
- `asset`, `available`, `selected`, and `status`.

The `edition` object contains:

- `kind`: `component`, `portable`, `complete-system`, `mixed`, or `absent`;
- `status`, capabilities, user/system shadowing, and wallpaper variants;
- `missingMandatory`, which excludes Qt and login-manager assets for component
  and portable editions.

An active `widgetStyle=NoxForge` without the native plugin is an action-required
`mixed` state. An unselected login wallpaper or SDDM theme is valid and does
not make an installation incomplete. With active PLM, an installed SDDM theme
is reported only as a compatibility capability. PLM settings are read with
`/usr/lib` defaults first and `/etc` overrides last.

The doctor never applies a theme, writes KDE or login-manager configuration,
asks for privileges, or claims unavailable physical evidence. System-service
queries time out and degrade to `unknown` instead of blocking the report.

## Schema 6 diagnostics

Schema 6 discovers the standard and Obsidian Konsole schemes, GTK 3/4 themes,
Kate/KWrite syntax themes, packaged terminal/editor assets, and the v13
Obsidian Plasma Style, Aurorae, wallpapers, SDDM theme, Neovim, and Helix
themes. The
`ecosystem.flatpakThemesOverride` field reports whether Flatpak applications
have a read-only `xdg-data/themes` override. The doctor also reports
fractional scaling factors when the inspected root provides them. The
`--remediation-plan` option emits non-destructive shell guidance and preserves
the report's status-derived exit code; it never claims that a suggested action
was executed.

`paletteSynchronization.status` is `synchronized`, `desynchronized`, or
`not-active`. Its `targets` object reports detected variants for active color
scheme, Plasma Style, Aurorae, splash, and wallpaper surfaces. A
`palette-desynchronization` issue is a warning to review those selections.
The remediation plan can print suggested commands for either palette, but it
does not change settings. The native Qt plugin is discovered as an installed
component; filesystem discovery does not prove which plugin Qt loaded.

Each component exposes ordered `paths`, `effectivePath`, `shadowedPaths`,
`copyVersions`, `metadataStatus`, and `duplicateStatus`. Data components use
user data followed by ordered absolute `$XDG_DATA_DIRS` entries (default
`/usr/local/share:/usr/share`) precedence. User paths are
shown relative to `$XDG_DATA_HOME` to avoid exposing account names. Native Qt
plugin paths are discovered candidates; `effectivePath` is null because the
loader's choice is not inferred from filesystem presence.

`duplicateStatus` is `none`, `identical`, `conflict`, `customized`, or `unknown` for data
components and `not-applicable` for native plugin candidates. Identical payload
copies are warnings; differing payloads fail even when version strings match unless
the difference is a valid user customization (e.g. customized SVG opacity with matching
component version metadata), in which case `duplicateStatus` is `customized`.
An unreadable comparison remains unknown. Review the listed shadowed copies
manually; doctor never removes them. `metadataStatus: unknown` is informational,
including component formats without version metadata.

`issues` contains `code`, `component`, `severity`, and `message`. Codes are
`duplicate-identical`, `duplicate-conflict`, `duplicate-customized`, `duplicate-unknown`,
`metadata-unknown`, `mixed-versions`, `missing-required`, and
`palette-desynchronization`. Text output renders the same issues and paths.
Error issues yield exit status 1; warnings and informational issues alone do
not fail an otherwise valid installation.

A standalone component is valid without the rest of the suite. The global theme
requires the portable component set, matching its Store dependency declaration.
A portable manifest or installer ownership marker requires that set. A native
plugin or installed `noxforge/release-manifest.json` identifies a system edition
and requires that set plus the native plugin. Optional login assets do not fail those editions.
The next action names Store components, the portable installer, or the system
package manager according to the detected edition.

`--root` never reads the source repository's VERSION or host session settings.
Only VERSION markers inside the inspected root are used; missing or invalid
markers produce `expectedVersion: null`. Staged session fields are
`not-applicable`; runtime scales and active configuration are not queried.
