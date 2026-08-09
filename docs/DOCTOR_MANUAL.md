# NoxForge doctor

`noxforge-doctor` is read-only. The portable invocation is
`$XDG_DATA_HOME/noxforge/bin/noxforge-doctor`; the complete-system invocation
is `/usr/bin/noxforge-doctor`.

Use `--json` for automation and `--root /absolute/staged/root` for an isolated
package tree. The stable JSON `edition` object contains:

- `kind`: `component`, `portable`, `complete-system`, `mixed`, or `absent`;
- `status`, capabilities, user/system shadowing, and wallpaper variants;
- `missingMandatory`, which excludes Qt and SDDM for component and portable
  editions.

An active `widgetStyle=NoxForge` without the native plugin is an action-required
`mixed` state. Missing SDDM is valid for portable and complete editions because
SDDM is separately selectable. The doctor never applies a theme, writes KDE
configuration, asks for privileges, or claims unavailable physical evidence.
