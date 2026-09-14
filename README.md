# NoxForge Ecosystem & App Parity

NoxForge is an original MIT-licensed Plasma visual system: quiet graphite
surfaces, exact electric-lime state markers, restrained detail, and a compact
Forge Notch. Version 12.0.0 targets Fedora 44 and Arch Plasma/KWin 6.7+ and
Qt 6.11 on Wayland, extending the system with GTK 3/4 themes, KDE syntax
themes, VS Code/Cursor themes, and matching Ghostty, Alacritty, Kitty, and
Foot terminal configurations. Doctor schema 5 reports the complete ecosystem
in read-only mode. Physical qualification remains pending; see [the evidence
record](docs/evidence/v12/qualification.json).

![NoxForge Hero Showcase](media/store/01_hero_desktop_showcase_2560x1440.png)

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

![NoxForge Hero Desktop Showcase](media/store/01_hero_desktop_showcase_2560x1440.png)
![Dual Palettes: Graphite and Obsidian OLED](media/store/02_dual_palettes_obsidian_2560x1440.png)
![Aurorae Window Craft and Forge Notch](media/store/03_window_craft_aurorae_2560x1440.png)
![Native Qt 6 Control Completeness](media/store/04_system_completeness_qt6_2560x1440.png)
![Application Launcher and Floating Plasma Shell](media/store/05_launcher_and_plasma_shell_2560x1440.png)
![Original Vector Iconography and File Hierarchy](media/store/06_original_iconography_2560x1440.png)
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
- GTK 3 and GTK 4 themes, Kate/KWrite syntax themes, and VS Code/Cursor editor
  themes in standard and Obsidian palettes;
- Ghostty, Alacritty, Kitty, and Foot configurations for both terminal palettes;
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

The active scope is [NOXFORGE_V12_PLAN.md](docs/NOXFORGE_V12_PLAN.md), indexed by
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
