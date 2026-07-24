# Install NoxForge on Fedora KDE

NoxForge v3 makes the RPM package the primary installation authority. Until a
public repository is approved and published, build and test the package from a
clean source archive:

```bash
python3 scripts/build.py
rpmbuild -ba \
  --define "_sourcedir $PWD/dist" \
  packaging/noxforge.spec
```

Install the resulting architecture-specific RPM only in a disposable Fedora
KDE test environment:

```bash
sudo dnf install ~/rpmbuild/RPMS/*/noxforge-*.rpm
```

Installation only places package-owned files. It does not select NoxForge,
change a panel, activate SDDM, clear caches, or restart Plasma.

Public DNF/COPR commands will be added only after the repository owner and
Fedora 44 project are confirmed and publication is explicitly approved.

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

## Upgrade

Upgrade from a local candidate with:

```bash
sudo dnf upgrade ./noxforge-3.0.0-1.fc44.x86_64.rpm
rpm -V noxforge
noxforge-doctor
```

## Roll back and remove

Before downgrading or removing NoxForge, select a known-good non-NoxForge
Global Theme and any components you selected separately. Restore a known-good
SDDM theme first if you explicitly activated NoxForge SDDM.

Downgrade to a retained package:

```bash
sudo dnf downgrade ./noxforge-2.0.0-1.fc44.x86_64.rpm
```

Or remove NoxForge:

```bash
sudo dnf remove noxforge
```

See [Troubleshooting](TROUBLESHOOTING.md) for mixed source/RPM installations
and safe diagnostic collection.
