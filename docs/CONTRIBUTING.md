# Contributing to NoxForge

NoxForge 10.1 targets Fedora KDE 44, Arch Plasma/KWin 6.7+, Qt 6.11 and Wayland.
Keep changes focused, preserve the Forge Identity design authority in `DESIGN.md`, and
do not copy artwork from another theme.

## Required development tools

On Fedora 44:

```bash
sudo dnf install cmake ffmpeg-free gcc-c++ git ImageMagick ninja-build \
  google-noto-sans-fonts libasan libubsan python3 qt6-qtbase-devel \
  qt6-qtdeclarative-devel \
  rpm-build rpmlint xz kf6-kpackage
```

## Release-integrity gate

Run the same gate used by CI:

```bash
mkdir -p build/baseline-source
baseline_commit=$(python3 -c 'import json; from pathlib import Path; print(json.loads(Path("distribution/release-manifest.json").read_text())["release"]["baseline"]["commit"])')
git archive "$baseline_commit" | tar -x -C build/baseline-source
python3 scripts/release-check.py --baseline-source build/baseline-source
python3 scripts/validate_media.py
```

The gate checks generated-file drift, repository metadata, Python tests, the
native Qt build and CTest suite, supported QML surfaces, non-mutating installer
dry runs, two independent source archives for byte identity, an SRPM/RPM build,
and `rpmlint`.

The release gate never applies NoxForge, changes KDE settings, restarts Plasma,
or publishes artifacts. Live desktop checks belong in an isolated Fedora KDE
test session and must follow `docs/MANUAL_TESTING.md`.

V10 Arch runtime qualification remains pending. Record exact Qt, Plasma, KWin,
OS and session versions with each test result; historical v9 evidence does not
qualify the v10 candidate.
