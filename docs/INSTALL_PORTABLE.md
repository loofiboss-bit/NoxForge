# Install the portable edition

The portable edition is user-local and reversible. It installs below
`$XDG_DATA_HOME/noxforge/` for its doctor and keeps component files in KDE's
normal user data roots. It uses Breeze application controls, has no native Qt
plugin or SDDM, and never writes active KDE settings.

```bash
tar -xJf noxforge-8.0.0-portable.tar.xz
cd noxforge
./scripts/install.sh --user --dry-run
./scripts/install.sh --user
"${XDG_DATA_HOME:-$HOME/.local/share}/noxforge/bin/noxforge-doctor" --json
```

Re-running the installer is safe and preserves unrelated sentinel files. A
known legacy root can be inspected with `--migrate`; migration is allowlisted
and never deletes the old data automatically.

```bash
./scripts/uninstall.sh --user --dry-run
./scripts/uninstall.sh --user
```

The uninstaller removes only paths recorded in the portable ownership manifest.
