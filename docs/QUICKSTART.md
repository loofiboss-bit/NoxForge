# Quick start and rollback

NoxForge v0.1.0 targets Fedora KDE 44, Plasma 6.7+, and Wayland. Plasma 6.6 is
the minimum supported version. Breeze remains the application style.

## Verify and install

From the repository or extracted local archive:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests
python3 scripts/build.py
./scripts/install.sh --user --dry-run
./scripts/install.sh --user
```

Installation copies only NoxForge-owned files below the current user's XDG data
directory. It does not apply a theme, edit KDE configuration, change the panel,
or restart Plasma Shell.

Select components separately in System Settings:

1. Colors: **NoxForge Dark**.
2. Plasma Style: **NoxForge**.
3. Window Decorations: **NoxForge**.
4. Icons: **NoxForge**.
5. Wallpaper: **NoxForge**.

This separation is intentional. A Look-and-Feel package and panel layout are
deferred beyond v0.1.0.

## Roll back

First select Breeze equivalents in System Settings so active settings no longer
reference NoxForge. Then preview and remove the installed files:

```bash
./scripts/uninstall.sh --user --dry-run
./scripts/uninstall.sh --user
```

Uninstall removes only the five exact NoxForge-owned component paths. It does
not rewrite active settings or restart Plasma Shell.
