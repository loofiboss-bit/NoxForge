# NoxForge Deep Focus & System Completeness

NoxForge is an original MIT-licensed Plasma visual system: quiet graphite
surfaces, exact electric-lime state markers, restrained detail, and a compact
Forge Notch. Version 11.0.0 targets Fedora 44 and Arch Plasma/KWin 6.7+ and
Qt 6.11 on Wayland, with complete native Qt 6 style coverage, official
Konsole themes, and an Obsidian true-black companion palette.
Physical qualification remains pending; see [the evidence record](docs/evidence/v11/qualification.json).

![NoxForge isolated desktop](media/v10/desktop.png)

Capture provenance and dimensions are recorded
in [media/manifest.json](media/manifest.json).

## Choose an installation

| Journey | What it includes | Boundary |
| --- | --- | --- |
| Store/component | Independently selectable KDE packages | User-local; no native Qt style, login-manager integration, or root |
| Portable | All user-local components, Breeze controls, installer, uninstaller, doctor | No login-manager integration, native plugin, or active-settings write |
| Complete system | Portable content plus native Qt style and system doctor | PLM wallpaper asset on Fedora; SDDM compatibility theme remains selectable |

Start with [Quick start](docs/QUICKSTART.md), or read the dedicated
[portable](docs/INSTALL_PORTABLE.md), [Fedora](docs/INSTALL_FEDORA.md), and
[Arch](docs/INSTALL_ARCH.md) guides. Package installation never applies a
theme, resets a panel, edits KDE configuration, or restarts Plasma.

## Gallery

![Dolphin and icon treatment](media/v10/dolphin.png)
![Launcher and panel](media/v10/launcher.png)
![System Settings](media/v10/system-settings.png)
![Aurorae and task switcher](media/v10/aurorae-tabbox.png)
![Recommended NoxForge Quiet login wallpaper](wallpapers/NoxForge-Quiet/contents/images/1920x1080.png)

Fedora 44 uses Plasma Login Manager (PLM) by default. NoxForge Quiet is the
recommended login wallpaper; NoxForge does not ship or claim a custom PLM QML
greeter and never writes the active PLM configuration. The SDDM theme remains
available for upgraded Fedora installations and the planned Arch journey.

These images carry explicit capture provenance in the media manifest. They are not a substitute for pending physical input,
cursor, audio, PAM/login, power, and live-session gates.

## Components

- Global Theme and Plasma Style with KDE-correct package roots;
- NoxForge Dark and Obsidian colors, matching Konsole themes, Aurorae decoration,
  KWin switcher, icons, cursors, and sounds;
- three selectable wallpapers: **NoxForge Forge** (`NoxForge`), **NoxForge Quiet**
  (`NoxForge-Quiet`), and **NoxForge Ultrawide** (`NoxForge-Ultrawide`);
- a native Qt 6 style, PLM wallpaper asset, and optional SDDM compatibility
  theme in the complete system edition;
- read-only edition-aware diagnostics and deterministic checksums.

Store descriptions state that components install separately and that the Global
Theme archive is not a complete one-click transaction. Store and portable
defaults use `widgetStyle=Breeze`; system packages use `widgetStyle=NoxForge`.

## Compatibility and rollback

See [compatibility](docs/COMPATIBILITY.md), [troubleshooting](docs/TROUBLESHOOTING.md),
and the [doctor manual](docs/DOCTOR_MANUAL.md). Always select a known-good
theme and login surface before rollback. Portable removal is file-precise and
RPM/Arch removal touches only package-owned paths.

## Development and evidence

The active scope is [NOXFORGE_V11_PLAN.md](docs/NOXFORGE_V11_PLAN.md), indexed by
[IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md). Run the phase gate with:

```bash
mkdir -p build/baseline-source
baseline_commit=$(python3 -c 'import json; from pathlib import Path; print(json.loads(Path("distribution/release-manifest.json").read_text())["release"]["baseline"]["commit"])')
git archive "$baseline_commit" | tar -x -C build/baseline-source
python3 scripts/release-check.py --baseline-source build/baseline-source --skip-rpm
python3 scripts/build.py --mode all --skip-tests
```

Full matrices remain temporary CI evidence; compact manifests and curated
representatives are tracked. See [CONTRIBUTING.md](docs/CONTRIBUTING.md) and
[MANUAL_TESTING.md](docs/MANUAL_TESTING.md) for boundaries.

## License

See [LICENSES.md](LICENSES.md). All NoxForge artwork and generated audio are
original project work.
