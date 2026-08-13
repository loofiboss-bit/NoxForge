# Install NoxForge on Fedora KDE

NoxForge 9 is a scriptlet-free Fedora 44 package for the complete-system
journey. It provides the native Qt style, system doctor, and all system theme
components. Fedora 44 uses Plasma Login Manager (PLM) by default. NoxForge
provides NoxForge Quiet as the recommended standard PLM wallpaper and retains
its SDDM theme only as an explicitly selectable compatibility component.

```bash
sudo dnf install noxforge
rpm -V noxforge
noxforge-doctor --json
```

Package installation does not apply NoxForge, change a panel, edit KDE
configuration, restart Plasma, install a display manager, or switch display
managers. PLM does not support arbitrary third-party greeter QML, so NoxForge
does not ship a replacement PLM greeter or write PLM configuration. Select components explicitly
in System Settings and keep panel-layout replacement disabled unless you have
deliberately chosen it.

## Build from the distributed source archive

```bash
tar -xJf noxforge-9.0.0-source.tar.xz
cd NoxForge-9.0.0
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build
DESTDIR="$PWD/stage" cmake --install build
```

The same source archive is the RPM Source0 input. Its archive root and checksum
are recorded in `SHA256SUMS`.

## Upgrade, rollback, and removal

```bash
sudo dnf upgrade --refresh noxforge
sudo dnf downgrade --refresh noxforge
sudo dnf remove --no-autoremove noxforge
```

Before rollback or removal, select a known-good Global Theme and restore a
known-good login wallpaper or SDDM theme if you explicitly activated one.
`rpm -V` and the doctor
are read-only checks; no scriptlet mutates user settings.
