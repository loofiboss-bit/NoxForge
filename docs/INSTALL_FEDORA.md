# Install NoxForge on Fedora KDE

NoxForge 13.0.2 is a scriptlet-free Fedora 44 package for the complete-system
journey. It provides the palette-adaptive native Qt style, system doctor, GTK
3/4 themes, syntax/editor/terminal assets, both Obsidian and Graphite Plasma
components, the `noxforge-opacity` configurator, and both SDDM theme variants. Fedora 44 uses Plasma Login Manager
(PLM) by default. NoxForge Quiet is the recommended standard PLM wallpaper;
NoxForge does not ship a custom PLM greeter or write PLM configuration.

Use the Fedora 44 COPR repository `loofitheboss/noxforge`. Verify the installed
version with `rpm -q noxforge`; repository metadata may need refreshing after
an upgrade is published.

```bash
sudo dnf copr enable loofitheboss/noxforge
sudo dnf install --refresh noxforge
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
tar -xJf noxforge-13.0.2-source.tar.xz
cd NoxForge-13.0.2
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
