# Install the complete edition on Arch

The verified target is Arch Linux with Plasma/KWin 6.7+ and Qt 6.11. The
repository contains a candidate `packaging/arch/PKGBUILD`; it is not published
to the AUR.

For a local candidate, preload the exact source archive into a temporary
`SRCDEST` and verify it before building:

```bash
export SRCDEST="$(mktemp -d)"
cp noxforge-8.0.0-source.tar.xz "$SRCDEST/"
makepkg --verifysource --cleanbuild
makepkg --cleanbuild
```

Install the resulting package with an isolated pacman root for qualification,
then run `noxforge-doctor --json`. Pacman owns rollback and removal; no
scriptlet applies the theme or changes KDE configuration.
