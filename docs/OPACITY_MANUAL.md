# NoxForge Transparency & Opacity Configurator

`noxforge-opacity` is the official configuration tool for customizing transparency levels across NoxForge Plasma Desktop Themes and Aurorae window decorations on KDE Plasma 6.

## Overview

NoxForge is designed with an OLED-first aesthetic, featuring deep graphite and true obsidian surfaces with high default opacity (94%–98%). For users who prefer a softer look with visible wallpaper bleed-through and frosted glass effects with KWin Blur, `noxforge-opacity` allows dialing in transparency safely, reversibly, and without root privileges.

## Invocations

```bash
# In-tree / development:
tools/noxforge-opacity [options]

# System-installed:
noxforge-opacity [options]
```

## Presets

| Preset | Panel | Dialogs | Widgets | Tooltips | Titlebars (Active/Inactive) | Description |
| --- | --- | --- | --- | --- | --- | --- |
| `solid` | 98% | 99% | 98% | 100% | 100% / 90% | Pitch-black, OLED pure solid |
| `original` | 94% | 94% | 92% | 96% | 100% / 90% | Factory default NoxForge |
| `frost` *(rec.)* | 78% | 78% | 76% | 88% | 85% / 75% | **Recommended** balanced frosted glass with KWin Blur |
| `glass` | 60% | 62% | 60% | 80% | 75% / 65% | Deep translucent glass; distinct wallpaper bleed |
| `ultra` | 40% | 45% | 40% | 70% | 60% / 50% | High transparency aesthetic |

## Common Workflows

### 1. Apply Recommended Frost Transparency
```bash
noxforge-opacity --preset frost
```

### 2. Set Custom Opacity Percentage
```bash
# Set 75% opacity (25% transparency)
noxforge-opacity --level 75

# Or with decimal notation:
noxforge-opacity --opacity 0.75
```

### 3. Apply to Both Panels and Window Titlebars
```bash
noxforge-opacity --preset frost --aurorae
```

### 4. Interactive Graphical UI (Qt 6 with Live Preview)
Launch the advanced graphical configurator featuring real-time 60fps desktop preview, preset cards, granular precision sliders, and non-blocking background application:
```bash
noxforge-opacity --gui
# Or simply run without arguments in a desktop session:
noxforge-opacity
```
*(If running on headless environments without PySide6/Qt, it automatically falls back gracefully to `kdialog`, `zenity`, or CLI mode).*

### 5. Inspect Current Opacity
```bash
# Human-readable report:
noxforge-opacity --status

# Machine-readable JSON:
noxforge-opacity --status --json
```

### 6. Dry Run (Preview Changes)
```bash
noxforge-opacity --preset glass --dry-run
```

### 7. Reset to Factory Defaults
```bash
noxforge-opacity --reset
```

## Safety and System Package Protection

When NoxForge is installed via RPM, Arch packages, or system-wide in `/usr/share/plasma/desktoptheme/`:
- `noxforge-opacity` never attempts to write to `/usr/share` without permissions or break package manager checksums (`rpm -V`).
- It automatically creates a user-local override in `$XDG_DATA_HOME/plasma/desktoptheme/` (typically `~/.local/share/plasma/desktoptheme/`).
- KDE Plasma prioritizes user-local themes over `/usr/share/`.
- To completely revert, simply run `noxforge-opacity --reset` or delete the local override folder.

## Cache Invalidation and Refresh

When opacity settings change, `noxforge-opacity` automatically:
1. Clears rendered Plasma theme SVG caches in `~/.cache/plasma_theme_*.kcache` and `~/.cache/plasma-svgelements-*`.
2. Sends a refresh signal to Plasma Shell and KWin via `qdbus` if running.
3. If `--no-reload` is passed, cache invalidation and D-Bus signals are skipped.
