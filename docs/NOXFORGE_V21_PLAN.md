# NoxForge 21.0.0 — Duotone Visual Craft, Aurorae v2, Live Control Core & Ecosystem v4

This plan records the NoxForge version 21 release scope and implementation sequence,
targeted for publication as `v21.0.0`. Building upon the `v20.0.0` baseline, V21
breaks through the procedural wireframe ceiling and strengthens runtime reactivity
across four major pillars:

## Product contract

NoxForge 21 preserves the two signature dark surfaces (**Graphite** `#0D1419` and
**Obsidian OLED** `#000000`), Forge Notch (`4 px`) architectural identity, Plasma
6.8 Wayland-native Union & KWin integration, three-edition packaging, symlink-free
packages, and the non-applying installation boundary.

1. **Tokens Schema 17 & 6-Accent Forge Matrix (`design/tokens.json`):**
   - Upgrades `design/tokens.json` to Schema 17, expanding `accents` from 4 to 6
     WCAG-verified presets: `lime`, `cyan`, `violet`, `amber`, **Forge Crimson**
     (`crimson`: `#FF8FA3`), and **Titanium Ice** (`ice`: `#93C5FD`), plus Custom Hex.
   - Codifies `duotoneIconography`, `auroraeV2`, `wallpaperV2`, and `ecosystemV4`.

2. **Duotone Surface Iconography, Wayland Cursors, PNG24 Wallpapers & Audio v2:**
   - Expands `icons/NoxForge` with physical `32x32`, `48x48`, and `64x64` optical
     tiers and ~52 curated `apps/` icons using Duotone Surface plates (`surfaceRaised`
     fills, `1 px` top bevels, semantic `places/` + folder colors, distinct `mimetypes/`),
     while preserving crisp `16x16` and `22x22` monoline symbols and kinetic `status/`
     ladders.
   - Upgrades `cursors/NoxForge-Cursors` with `4x4` subpixel anti-aliasing + `1 px`
     contrast halo across `[24, 32, 36, 48, 64]` Xcursors plus Plasma 6 Wayland
     `cursors_scalable/` SVG directories.
   - Upgrades `scripts/render_wallpaper.py` from `PNG8` (`256`-color) to true
     anti-banded `PNG24`, enriches `NoxForge-Obsidian` architectural depth (`>85%`
     `#000000`), adds `16:10` (`2560x1600`, `3840x2400`) & `32:9` (`5120x1440`),
     KDE Dynamic Wallpaper (`images_dark/`), and accent-adaptive rendering.
   - Upgrades `scripts/generate_sound_theme.py` to **Tactile Forge Audio v2**
     (24 distinct DSP-synthesized waveforms across 32 Freedesktop events).

3. **Aurorae v2, Plasma 6.8 DesktopTheme Craft & Look-and-Feel QML:**
   - Fixes the `frame()` Forge Notch `45°` chamfered `edge_highlight` geometry bug in
     `scripts/generate_plasma_svgs.py`, adds `opaque/widgets/background.svg`, and
     overhauls `notes.svg`, `clock.svg`, `calendar.svg`, `timer.svg`, `glowbar.svg`,
     and `checkmarks.svg`.
   - Upgrades Aurorae to **Aurorae v2** (`Shadow=true`, filter-free stepped ambient
     shadows, flush `decoration-maximized-*` frames, `metadata.json`, and user-local
     live accent-rail sync).
   - Adds token-bound Plasma 6 **Forge OSD** (`contents/osd/Osd.qml`, `OsdItem.qml`)
     and **SystemDialog** (`contents/systemdialog/SystemDialog.qml`).

4. **Complete C++ Qt 6 Style, Modular Union CSS, Deep GTK4, Control Center v6, Ecosystem v4 & Doctor Schema 14:**
   - Completes missing `QStyle` elements (`CC_Dial`, `CC_MdiControls`, `CC_TitleBar`,
     `CE_DockWidgetTitle`, `CE_RubberBand`, `CE_HeaderEmptyArea`, `QSlider` ticks,
     `QSpinBox` subcontrols), replaces `1000 ms` paint-loop polling with
     `QFileSystemWatcher` + `QPalette::Accent`, and extends `NoxForgeMotion` to
     `QLineEdit`, `QAbstractItemView`, and per-tab `QTabBar`.
   - Expands modular `union/styles/` CSS and differentiates GTK3 vs GTK4/Libadwaita.
   - Upgrades `noxforge-ctl` with live hot-reload (`KGlobalSettings`, `KWin`,
     `gsettings`, `SIGUSR1`, `tmux`, `nvim`), `preset`, `accent --from-wallpaper`,
     and `fastfetch` commands + Flatpak `xdg-data/icons:ro`.
   - Rebuilds Control Center to **v6** with async `CommandWorker(QThread)`, pure
     Obsidian QSS, 6-accent matrix, Named Presets, Wallpaper Accent Extractor,
     Live Surface Preview, and Ecosystem filter.
   - Completes Fastfetch Kinetic Studio v2, deepens Neovim/VS Code/Firefox+Zen/Discord+Vesktop,
     adds `bat`, `delta`, `fzf`, `eza`, `wofi` (25 Ecosystem v4 tools), and hardens
     `noxforge-doctor` to **Schema 14** (`0` unmasked `metadata-unknown`, `configDrift`,
     `qtStyleLoadable`, `kwinBlurStatus`, `gtkImportIntegrity`).

## Acceptance criteria

- `design/tokens.json` complies with Schema 17 (`6` accents + `duotoneIconography`, `auroraeV2`, `wallpaperV2`, `ecosystemV4`).
- All deterministic generator `--check` gates, `scripts/validate.py`, `ctest`, `pytest`, `qmllint`, `ruff`, and `scripts/release-check.py` pass cleanly against `v20.0.0`.
