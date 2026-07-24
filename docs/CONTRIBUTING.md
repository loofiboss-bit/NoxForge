# Contributing to NoxForge

NoxForge targets Fedora KDE 44, Plasma 6.7+, Qt 6.11 and Wayland. Keep changes
focused, preserve the Industrial Precision design authority in `DESIGN.md`, and
do not copy artwork from another theme.

## Required development tools

On Fedora 44:

```bash
sudo dnf install cmake ffmpeg-free gcc-c++ git ImageMagick ninja-build \
  python3 qt6-qtbase-devel qt6-qtdeclarative-devel rpm-build rpmlint xz
```

## Release-integrity gate

Run the same gate used by CI:

```bash
python3 scripts/release-check.py
```

The gate checks generated-file drift, repository metadata, Python tests, the
native Qt build and CTest suite, supported QML surfaces, non-mutating installer
dry runs, two independent source archives for byte identity, an SRPM/RPM build,
and `rpmlint`.

The release gate never applies NoxForge, changes KDE settings, restarts Plasma,
or publishes artifacts. Live desktop checks belong in an isolated Fedora KDE
test session and must follow `docs/MANUAL_TESTING.md`.
