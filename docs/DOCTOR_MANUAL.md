# NoxForge doctor

`noxforge-doctor` is read-only. The portable invocation is
`$XDG_DATA_HOME/noxforge/bin/noxforge-doctor`; the complete-system invocation
is `/usr/bin/noxforge-doctor`.

Use `--json` for automation and `--root /absolute/staged/root` for an isolated
package tree. JSON schema 2 adds a stable top-level `loginSurface` object and
retains the `edition` object. `loginSurface` contains:

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
