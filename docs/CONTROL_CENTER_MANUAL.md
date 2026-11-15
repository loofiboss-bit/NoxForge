# NoxForge Control Center & Unified CLI Manual

`noxforge-ctl` and **NoxForge Control Center v5** provide a unified orchestration suite for switching palettes, customizing accent highlights, configuring Kinetic Iconography, tuning transparency, deploying ecosystem themes, managing diurnal schedules, and verifying system health across KDE Plasma 6.8+.

---

## 1. Overview

In **v20.0.0**, NoxForge provides a full-featured command-line utility (`noxforge-ctl`) and a 5-tab interactive PySide6 graphical interface (**Control Center v5** / `noxforge-ctl gui` / application launcher).

Key capabilities:
- **Profile Switching**: Instantly switch between the default deep slate **Graphite** palette and the pure **Obsidian OLED** true-black palette.
- **Accent Matrix & Union Harmony**: Select between Forge accents (`lime`, `cyan`, `violet`, `amber`, `system`, or WCAG AA custom hexes) synchronized across Plasma, Qt 6, `plasma-union`, and GTK 3/4.
- **Kinetic Icon Studio (`icons`)**: Configure custom icon accent tinting, optical sizing (`16`, `22`, or `auto`), and preview live 16-frame animated sprites and 10%/20%/25% multi-level status ladders.
- **Transparency & Opacity (`opacity`)**: Integrated tuning of panel, dialog, tooltip, and Aurorae window decoration opacity via presets (`solid`, `default`, `frost`, `glass`, `ultra`) or fine-grained sliders.
- **Ecosystem v3 & Flatpak (`ecosystem`, `flatpak`)**: Non-destructively deploy or restore themes across 18 developer tools (including Yazi, Lazygit, Zellij, Tmux, Zed, Neovim, Helix, Ghostty, Kitty, Alacritty, Starship, btop, Obsidian, Rofi) with `.noxforge.bak` backups and Flatpak GTK/Qt/icon overrides.
- **Motion, Wallpapers & Presets (`motion`, `wallpaper`, `export`, `import`)**: Control kinetic animation curves/reduced motion, switch the 5-wallpaper suite, and export/import full system presets.
- **Diurnal Automation (`schedule`)**: Optional systemd user timer to automatically switch between Graphite during the day and Obsidian at night.
- **Diagnostics (`doctor`)**: Built-in integration with `noxforge-doctor` (Schema 13) to verify installation integrity, `iconLevelMatrix`, and palette synchronization.

---

## 2. Command-Line Interface (`noxforge-ctl`)

### Synopsis

```bash
noxforge-ctl {switch,apply,sync,accent,icons,union,kwin-csd,flatpak,ecosystem,motion,wallpaper,export,import,preset,status,opacity,doctor,schedule,completion,gui} [options]
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
Select the active Forge accent highlight:

```bash
noxforge-ctl accent lime
noxforge-ctl accent cyan
noxforge-ctl accent violet
noxforge-ctl accent amber
noxforge-ctl accent system
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

