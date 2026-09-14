# Install the complete edition on Arch

Download the exact 11.0.0 archive and `SHA256SUMS` from the
[GitHub release](https://github.com/loofiboss-bit/NoxForge/releases/tag/v11.0.0).
Verify its checksum before installation.

The intended target is Arch Linux with Plasma/KWin 6.7+ and Qt 6.11. The
repository contains `packaging/arch/PKGBUILD`; it is not published
to the AUR.

For a local candidate, preload the exact source archive into a temporary
`SRCDEST` and verify it before building:

```bash
export SRCDEST="$(mktemp -d)"
cp noxforge-11.0.0-source.tar.xz "$SRCDEST/"
makepkg --verifysource --cleanbuild
makepkg --cleanbuild
```

Install the resulting package with an isolated pacman root for qualification,
then run `noxforge-doctor --json`. Pacman owns rollback and removal; no
scriptlet applies the theme or changes KDE configuration. SDDM is the planned
login-manager journey on Arch and remains an optional dependency; package
installation does not install, enable, or configure it.
