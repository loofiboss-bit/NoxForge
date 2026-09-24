# Install the complete edition on Arch

Download the exact 13.0.2 archive and `SHA256SUMS` from the
[GitHub release](https://github.com/loofiboss-bit/NoxForge/releases/tag/v13.0.2).
Verify its checksum before installation.

The intended target is Arch Linux with Plasma/KWin 6.7+ and Qt 6.11. The
repository contains `packaging/arch/PKGBUILD`; it is not published
to the AUR.

For a local candidate, preload the exact source archive into a temporary
`SRCDEST` and verify it before building:

```bash
export SRCDEST="$(mktemp -d)"
cp noxforge-13.0.2-source.tar.xz "$SRCDEST/"
makepkg --verifysource --cleanbuild
makepkg --cleanbuild
```

Install the resulting package with an isolated pacman root for qualification,
then run `noxforge-doctor --json`. Pacman owns rollback and removal; no
scriptlet applies the theme or changes KDE configuration. The SDDM theme is an
optional compatibility component; package installation does not install,
enable, or configure SDDM. V13 Arch build, live-login, and pacman lifecycle
qualification remain pending.
