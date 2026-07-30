# Install NoxForge on Fedora KDE

NoxForge v6 uses the RPM package as the primary installation authority. Enable
the Fedora 44 COPR and install the package:

```bash
sudo dnf copr enable loofitheboss/noxforge
sudo dnf install noxforge
```

To build the exact package locally from a clean source archive instead:

```bash
python3 scripts/build.py
rpmbuild -ba \
  --define "_sourcedir $PWD/dist" \
  packaging/noxforge.spec
```

The NoxForge RPM owns only its theme, plugin, diagnostic, and documentation
files and has no installation scriptlets. On the supported Fedora KDE target,
DNF reuses the installed Plasma, KWin, Qt, and SDDM packages. NoxForge does not
select a theme, change a panel, activate SDDM, clear caches, or restart Plasma.

## Select the theme

Open **System Settings → Colors & Themes → Global Theme**, select NoxForge and
review the components before applying. Keep panel-layout replacement disabled
unless you explicitly want the optional compact NoxForge layout.

Select the NoxForge application style, window decoration, icons, cursors,
colors, task switcher, splash screen and sounds individually if your Global
Theme selection does not include a component. SDDM is intentionally separate;
test it in a recoverable VM before selecting it as the login-screen theme.

## Verify

```bash
rpm -V noxforge
noxforge-doctor
```

The doctor is read-only and exits non-zero when components are absent or mixed.

NoxForge motion follows KDE's configured animation duration. A zero duration
settles every native Qt and supported QML state immediately while preserving
focus, selection, busy, success, and error indicators.

## Upgrade

Upgrade from COPR with:

```bash
sudo dnf upgrade --refresh noxforge
rpm -V noxforge
noxforge-doctor
```

## Roll back and remove

Before downgrading or removing NoxForge, select a known-good non-NoxForge
Global Theme and any components you selected separately. Restore a known-good
SDDM theme first if you explicitly activated NoxForge SDDM.

For a later NoxForge update, downgrade to an older build retained in the
enabled repository:

```bash
sudo dnf downgrade --refresh noxforge
```

NoxForge v2 did not have an RPM channel. For all package-managed releases,
explicitly select another theme before removal. Disable dependency cleanup so
a minimal or manually assembled KDE installation cannot lose desktop packages
that DNF first encountered as NoxForge dependencies:

```bash
sudo dnf remove --no-autoremove noxforge
```

See [Troubleshooting](TROUBLESHOOTING.md) for mixed source/RPM installations
and safe diagnostic collection.
