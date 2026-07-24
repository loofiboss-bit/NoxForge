# Quick start and rollback

NoxForge 3.0 targets Fedora KDE 44, Plasma 6.7+, Qt 6.11 and Wayland. The RPM
is the primary installation authority.

## Install

```bash
sudo dnf copr enable loofitheboss/noxforge
sudo dnf install noxforge
rpm -V noxforge
noxforge-doctor
```

Package installation changes no settings. Select **NoxForge** explicitly in
System Settings → Colors & Themes → Global Theme. Keep panel-layout replacement
disabled unless the optional compact layout is deliberately wanted. Select and
test NoxForge SDDM separately in a recoverable VM.

## Build locally

```bash
python3 scripts/release-check.py
python3 scripts/build.py
rpmbuild -ba --define "_sourcedir $PWD/dist" packaging/noxforge.spec
```

## Roll back

Select another Global Theme and login screen first, then remove the package:

```bash
sudo dnf remove noxforge
```

Removal deletes only RPM-owned paths and does not rewrite active KDE or SDDM
configuration. See `docs/INSTALL_FEDORA.md` for upgrade and downgrade commands,
and `docs/TROUBLESHOOTING.md` for old user-local source copies.
