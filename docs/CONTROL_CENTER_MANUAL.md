# NoxForge Control Center & Unified CLI Manual

`noxforge-ctl` and **NoxForge Control Center v6** provide a unified orchestration suite for switching palettes, customizing 6 signature Forge accents (plus WCAG-AA Wallpaper Accent Extraction), managing named presets, configuring Duotone & Kinetic Iconography, tuning transparency, deploying Ecosystem v4 (25 tools) and Fastfetch Kinetic Studio v2, managing diurnal schedules, and verifying system health across KDE Plasma 6.8+.

---

## 1. Overview

In **v21.0.0**, NoxForge provides a live hot-reload command-line utility (`noxforge-ctl`) and a 5-tab interactive PySide6 graphical interface (**Control Center v6** / `noxforge-ctl gui` / application launcher) using non-blocking `CommandWorker(QThread)` execution and native `NoxForge` QStyle dogfooding.

Key capabilities:
- **Profile Switching & Live Hot-Reload**: Instantly switch between deep slate **Graphite** and pure `#000000` **Obsidian OLED**, automatically hot-reloading Plasma (`KGlobalSettings`), KWin, GTK (`gsettings`), terminals (`SIGUSR1` to current-UID Kitty/Foot/Ghostty), `tmux`, and Neovim (opt out via `--no-reload` or `NOXFORGE_SKIP_LIVE_RELOAD=1`).
- **6-Accent Matrix & Wallpaper Accent Extractor**: Choose from 6 WCAG-verified accents (`lime`, `cyan`, `violet`, `amber`, `crimson`, `ice`, `system`, or custom WCAG AA hex), extract a safe accent directly from any wallpaper (`accent --from-wallpaper`), and optionally render an accent-tinted wallpaper (`--sync-wallpaper`) with user-local Aurorae rail sync.
- **Named Presets (`preset`)**: Save, list, apply, and delete named configuration snapshots (`profile`, `accent`, `opacity`, `wallpaper`, `reduced_motion`, `union_mode`) and bind them to Day/Night schedules (`--day-preset`/`--night-preset`).
- **Kinetic & Duotone Icon Studio (`icons`)**: Preview live 16-frame animated sprites and 10%/20%/25% multi-level status ladders alongside 482 scalable Duotone Surface icons.
- **Transparency & Opacity (`opacity`)**: Integrated tuning of panel, dialog, tooltip, and Aurorae v2 window decoration opacity via presets (`solid`, `default`, `frost`, `glass`, `ultra`) or fine-grained sliders.
- **Ecosystem v4 & Flatpak (`ecosystem`, `fastfetch`, `flatpak`)**: Non-destructively deploy or restore themes across 25 developer tools (adding `bat`, `delta`, `fzf`, `eza`, `wofi`, and Fastfetch Kinetic Studio v2 `main`/`cyber`/`minimal` presets) with `.noxforge.bak` backups and Flatpak theme, icon, and cursor overrides.
- **Diagnostics (`doctor`)**: Built-in integration with `noxforge-doctor` (Schema 14) to verify installation integrity, real version metadata, `qtStyleLoadable`, `kwinBlurStatus`, `gtkImportIntegrity`, `flatpakIconAccess`, `dayNightTimerStatus`, and `configDrift`.

---

## 2. Command-Line Interface (`noxforge-ctl`)

### Synopsis

```bash
noxforge-ctl {switch,apply,sync,accent,preset,fastfetch,icons,union,kwin-csd,flatpak,ecosystem,motion,wallpaper,export,import,status,opacity,doctor,schedule,completion,gui} [options]
```

### Subcommands

#### `icons` (v20.0.0 — Kinetic Iconography)
Customize icon accent tinting and optical icon density:

```bash
# Apply custom WCAG AA hex accent tint to Kinetic icons
noxforge-ctl icons --accent "#22D3EE"

# Set preferred optical stroke density (16, 22, or auto)
noxforge-ctl icons --optical 22

# Reset icon customizations
noxforge-ctl icons --reset
```

#### `flatpak`
Manage read-only Flatpak GTK, Qt, and icon filesystem overrides (`~/.local/share/flatpak/overrides/global`):

```bash
noxforge-ctl flatpak --enable
noxforge-ctl flatpak --disable
noxforge-ctl flatpak --status
```

#### `ecosystem` (v3 — 18 Apps)
Deploy or restore NoxForge themes for supported tools (`yazi`, `lazygit`, `zellij`, `tmux`, `zed`, `neovim`, `helix`, `vscode`, `ghostty`, `alacritty`, `kitty`, `foot`, `btop`, `starship`, `fastfetch`, `obsidian`, `rofi`, `discord`, `firefox`, `systemmonitor`):

```bash
noxforge-ctl ecosystem list
noxforge-ctl ecosystem apply all
noxforge-ctl ecosystem apply yazi lazygit zellij tmux
noxforge-ctl ecosystem restore all
```

#### `union` (KDE Plasma 6.8)
Manage KDE Plasma 6.8 Union Style Engine (`plasma-union`) integration:

```bash
# Inspect Union style status
noxforge-ctl union --status

# Enable full Union widgetStyle mode (widgetStyle=Union + unionStyle=noxforge)
noxforge-ctl union --enable

# Return to Hybrid mode (widgetStyle=NoxForge + unionStyle=noxforge)
noxforge-ctl union --disable
```

#### `kwin-csd` (v19.0.0 — KWin 6.8)
Synchronize KWin 6.8 client-side window titlebar color scheme rules (`~/.config/kwinrulesrc` with `.noxforge.bak` backup):

```bash
noxforge-ctl kwin-csd --enable
noxforge-ctl kwin-csd --disable
noxforge-ctl kwin-csd --status
```

#### `switch`
Switch between Graphite and Obsidian profiles across desktop surfaces (color scheme, Plasma style, window decorations, TabBox task switcher, splash screen, and GTK theme).

```bash
# Switch to Obsidian OLED
noxforge-ctl switch obsidian

# Switch to standard Graphite
noxforge-ctl switch graphite

# Test without applying changes
noxforge-ctl switch obsidian --dry-run

# Output JSON for scripts and status widgets
noxforge-ctl switch obsidian --json
```

#### `sync`
Synchronize the full NoxForge suite across all desktop layers (Look-and-Feel, color scheme, Plasma desktop style, widget style, window decorations, icons, cursors, sounds, and GTK 3/4 themes) and apply live to running Plasma session:

```bash
# Synchronize active profile across all desktop components
noxforge-ctl sync

# Synchronize explicitly to Obsidian OLED
noxforge-ctl sync --profile obsidian

# Dry-run preview
noxforge-ctl sync --dry-run --json
```

#### `accent`
Select any of the 6 signature Forge accents, extract a WCAG-AA safe accent from a wallpaper, or apply a custom hex:

```bash
noxforge-ctl accent lime
noxforge-ctl accent cyan
noxforge-ctl accent violet
noxforge-ctl accent amber
noxforge-ctl accent crimson
noxforge-ctl accent ice
noxforge-ctl accent --from-wallpaper --sync-wallpaper
noxforge-ctl accent system
```

#### `preset` (v21.0.0 — Named Presets)
Manage saved named configuration snapshots in `~/.config/noxforge/presets.json`:

```bash
noxforge-ctl preset list
noxforge-ctl preset save coding-night
noxforge-ctl preset apply coding-night
noxforge-ctl preset delete coding-night
```

#### `fastfetch` (v21.0.0 — Fastfetch Kinetic Studio v2)
Deploy one of the three curated Fastfetch telemetry presets (`main`, `cyber`, `minimal`) with matching ANSI logos:

```bash
noxforge-ctl fastfetch --preset main
noxforge-ctl fastfetch --preset cyber
noxforge-ctl fastfetch --preset minimal
noxforge-ctl fastfetch --status
```

#### `status`
Inspect the currently active profile, accent color, color scheme, Plasma style, Aurorae decoration, and TabBox switcher:

```bash
noxforge-ctl status
```

#### `opacity`
Forward commands to the transparency engine (`noxforge-opacity`):

```bash
# Apply recommended frost glass preset
noxforge-ctl opacity --preset frost

# Set custom level
noxforge-ctl opacity --level 80
```

#### `schedule`
Configure automatic Day/Night profile transitions:

```bash
# Enable automatic day/night switching
noxforge-ctl schedule --enable

# Disable schedule
noxforge-ctl schedule --disable

# Check schedule status
noxforge-ctl schedule --status
```

#### `doctor`
Run diagnostic health checks to ensure all theme assets and plugins are aligned:

```bash
noxforge-ctl doctor
```

#### `gui`
Launch the interactive graphical interface:

```bash
noxforge-ctl gui
```

---

## 3. Graphical Interface (NoxForge Control Center v5)

Launch from the KDE Application Launcher under **Settings > NoxForge Control Center**, or run `noxforge-ctl gui` in the terminal.

The interface is organized into five dedicated tabs plus the integrated **Kinetic Icon Studio**:

1. **Profile & Accent**:
   - Visual toggle between **Graphite** (`#0D1419`) and **Obsidian OLED** (`#000000`) profiles.
   - Live Forge Accent Matrix swatches (`Lime`, `Cyan`, `Violet`, `Amber`, `System`, or custom hex with live WCAG AA contrast badges).
   - **Kinetic Icon Studio**: Live animated `process-working` spinner preview, interactive Battery/Wi-Fi/Volume level slider, and `16px`/`22px`/`scalable` optical toggle.
   - Configurable Day/Night diurnal scheduling controls.

2. **Transparency & Depth**:
   - Quick presets: **Solid** (98%), **Original** (94%), **Frost** (78%, recommended with KWin Blur), **Glass** (60%), and **Ultra** (40%).
   - Granular adjustment sliders for Panels, Dialogs, Widgets, and Aurorae Titlebars with a real-time blur preview.

3. **Accessibility & Motion**:
   - System-wide Reduced Motion toggles (`AnimationDurationFactor` & GTK `enable-animations`).
   - High-contrast focus ring and Plasma 6.8 `plasma-union` / KWin CSD controls.

4. **System Health & Doctor**:
   - Integrated `noxforge-doctor` (Schema 13) diagnostic view covering `iconLevelMatrix`, `animations`, `unionStyleStatus`, `waylandCompositor`, and `gtkChainStatus`.
   - One-click non-destructive configuration alignment (`--apply-sync`) and diagnostic report export.

5. **Ecosystem & Apps**:
   - Detect, deploy, preview, or restore NoxForge Graphite/Obsidian themes across 18 supported CLI, editor, and desktop applications (including Yazi, Lazygit, Zellij, Tmux, Zed, Neovim, Helix, Ghostty, Kitty, Alacritty, Foot, btop, Starship, Obsidian, Rofi) and toggle Flatpak sandbox overrides.

---

## 4. Architectural Safety & Standards

- **Non-Destructive**: All modifications are performed within `$XDG_CONFIG_HOME` and `$XDG_DATA_HOME`. System packages and root filesystems are never altered.
- **Graceful CLI Operation**: On minimal or headless systems without PySide6 (`python3-pyside6`) installed, manage profiles, accents, Kinetic icons, opacity, Flatpak overrides, and diagnostics directly using `noxforge-ctl` from the command line.
- **Wayland-Native**: Full support for Plasma 6.8+ on Wayland with dynamic scaling awareness and zero tearing.

