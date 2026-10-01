# NoxForge Control Center & Unified CLI Manual

`noxforge-ctl` and the **NoxForge Control Center** provide a unified orchestration suite for switching palettes, customizing accent highlights, tuning transparency, managing diurnal schedules, and verifying system health across KDE Plasma 6.

---

## 1. Overview

Starting with **v14.0.0**, NoxForge includes both a full-featured command-line utility (`noxforge-ctl`) and an interactive graphical interface (`noxforge-ctl gui` / application launcher).

Key capabilities:
- **Profile Switching**: Instantly switch between the default deep slate **Graphite** palette and the pure **Obsidian OLED** true-black palette.
- **Accent Matrix**: Select between Forge accents (`lime`, `cyan`, `violet`, `amber`, or `system`).
- **Transparency & Opacity**: Integrated tuning of panel, dialog, tooltip, and Aurorae window decoration opacity via presets (`frost`, `glass`, `solid`, etc.) or fine-grained sliders.
- **Diurnal Automation**: Optional systemd user timer to automatically switch between Graphite during the day and Obsidian at night.
- **Diagnostics**: Built-in integration with `noxforge-doctor` to ensure installation integrity and palette synchronization.

---

## 2. Command-Line Interface (`noxforge-ctl`)

### Synopsis

```bash
noxforge-ctl {switch,accent,status,opacity,doctor,schedule,gui} [options]
```

### Subcommands

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

## 3. Graphical Interface (NoxForge Control Center)

Launch from the KDE Application Launcher under **Settings > NoxForge Control Center**, or run `noxforge-ctl gui` in the terminal.

The interface is organized into three dedicated tabs:

1. **Profiles & Accents**:
   - Visual toggle between **Graphite** and **Obsidian** profiles.
   - Live color badges for accent selection (`Lime`, `Cyan`, `Violet`, `Amber`, `System`).
   - One-click instant application without restarting Plasma.

2. **Opacity & Glass**:
   - Quick presets: **Solid** (98%), **Original** (94%), **Frost** (78%, recommended with KWin Blur), **Glass** (60%), and **Ultra** (40%).
   - Granular adjustment sliders for Panels, Dialogs, Widgets, and Aurorae Titlebars.
   - Interactive preview window simulating frosted glass wallpaper blur.

3. **Diagnostics & Automation**:
   - Integrated status indicator showing palette synchronization and component versions.
   - One-click "Align Configuration" to repair desynchronized surfaces.
   - Simple toggle for Day/Night scheduled transitions.

---

## 4. Architectural Safety & Standards

- **Non-Destructive**: All modifications are performed within `$XDG_CONFIG_HOME` and `$XDG_DATA_HOME`. System packages and root filesystems are never altered.
- **Graceful CLI Operation**: On minimal or headless systems without PySide6 (`python3-pyside6`) installed, manage profiles, accents, opacity, and diagnostics directly using `noxforge-ctl` from the command line.
- **Wayland-Native**: Full support for Plasma 6.7+ on Wayland with dynamic scaling awareness and zero tearing.

