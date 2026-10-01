# Changelog

## 14.0.1 — Store Assets Refresh & Fluid TabBox Switcher

- KWin TabBox Window Switcher:
  - Fixed non-responsive cycling under Alt+Tab by implementing bidirectional index synchronization (`tabBox.currentIndex`) with `Connections` signal handling.
  - Added smooth mouse wheel and touchpad scrolling support with wrap-around item cycling via `WheelHandler`.
  - Added outer dialog and list keyboard navigation for arrow keys (Left/Right/Up/Down) and Tab/Backtab with full RTL support.
  - Enhanced fluid motion: active card tactile elevation (`scale: 1.03`), icon scale bounce (`scale: 1.08`), kinetic expanding accent indicator bar, and centered viewport range alignment (`preferredHighlightBegin`).
  - Added interactive mouse hover feedback (`tokens.surfaceHover` and `tokens.edgeHighlight`).
  - Maintained full parity across both Graphite and Obsidian TabBox variants (`io.github.loofiboss.noxforge.desktop` and `io.github.loofiboss.noxforge.obsidian.desktop`).
- Visual Assets & Store Presentation:
  - Fully regenerated high-resolution marketing and gallery screenshots across all 6 showcase slots for KDE Store / OpenDesktop and GitHub repository.
  - Added updated store hero banners (1280x640, 1920x1080), social preview banners, store icon (400x400), and store thumbnail (480x380).

## 14.0.0 — Unified Control Suite & Full Ecosystem Parity

- True Obsidian OLED Parity & Dual-Stack Architecture:
  - Add dedicated Obsidian lock screen in look-and-feel package (`io.github.loofiboss.noxforge.obsidian.desktop`).
  - Add dedicated Obsidian TabBox KWin switcher (`io.github.loofiboss.noxforge.obsidian.desktop`).
  - Real-time dynamic accent matrix with high-contrast electric lime notches across both palettes.
- Qt 6 C++ Style Engine:
  - Add dynamic QMenu item sizing, paddings, and font metrics preventing text clipping or truncation across high-DPI displays and scaling factors.
  - Implement high-contrast dynamic toggle switches with clear visual states and smooth transitions.
- Unified Control Suite:
  - Add `noxforge-ctl` CLI command supporting palette inspection, instant switching, automated scheduling, and doctor validation.
  - Add PySide6/Qt 6 NoxForge Control Center GUI (`noxforge-ctl gui` / desktop launcher) integrating palette switching, opacity/blur customization, and diagnostics.
  - Add systemd user timer for automatic diurnal palette transitions.
- Extended Ecosystem Parity:
  - Add themes and syntax definitions for Zed editor, btop, Starship prompt, Fastfetch, Firefox userChrome, and Discord.
- Tooling & Packaging:
  - Upgrade `noxforge-doctor` to Schema 7 with automated desktop configuration alignment (`--apply-sync [graphite|obsidian]`).
  - Re-qualify Fedora 44 RPM/SRPM, Arch Linux PKGBUILD, portable bundle, and 18 release artifacts.

## 13.0.2 — Opacity Configurator Stabilization & System Coherence

- Eliminate deprecated `org.kde.PlasmaShell.refreshCurrentShell` D-Bus call to prevent SIGSEGV crashes on theme reload in Plasma 6 / Qt 6.
- Distinguish user opacity overrides from duplicate conflicts in `noxforge-doctor` (`[info: duplicate-customized]`), keeping edition status `ok`.
- Robust SVG attribute injection fallback and complete opacity token parsing (including percentages and scientific notation).
- Active Plasma desktop wallpaper sampling with `XDG_CONFIG_HOME` resolution and percent-encoded URL decoding.
- 60fps simulated frosted glass blur with center-cropped wallpaper geometry alignment and painter brush state cleanup.
- High-DPI display scaling protection with `QScrollArea`, guaranteed slider heights, and cooperative thread termination safety.

## 13.0.1 — Opacity & Transparency Configurator

- Add `noxforge-opacity` CLI utility and Qt 6 GUI configurator for customizing panel, popup, and Aurorae window decoration transparency levels.
- Add desktop entry `io.github.loofiboss.noxforge.opacity.desktop` for system application launcher integration.
- Presets (`solid`, `original`, `frost`, `glass`, `ultra`) and fine-grained percentage sliders with 60fps real-time desktop preview.
- Direct integration with KDE Desktop Effects (Blur settings) for optimal contrast on transparent surfaces.
- Package integration into Fedora RPM (COPR), portable bundle, and companion store packages.

## 13.0.0 — True Obsidian OLED Parity & Dual-Stack Architecture

- Full Obsidian Plasma Style and dedicated Global Theme (`io.github.loofiboss.noxforge.obsidian.desktop`).
- Obsidian Aurorae window decoration with 6px border and electric-lime active notch.
- Dynamic runtime-adaptive Qt 6 C++ style (`noxforgestyle.so`) seamlessly switching between Graphite and OLED black.
- `NoxForge-Obsidian` (16:9 4K) and `NoxForge-Obsidian-Ultrawide` (21:9) vector wallpapers and SDDM Obsidian theme.
- Official Neovim (Lua) and Helix (TOML) syntax themes in both Standard and Obsidian palettes.
- Tokens Schema 9 dual-palette authority and Doctor Schema 6 with palette desynchronization diagnostics.
- Synchronized CMake, RPM, Arch, portable, and companion KDE Store packages.

## 12.0.1 — Aurorae Decoration Border Fix

- Fix Aurorae window decorations appearing as thick black borders on Fedora/KWin
  by disabling synthetic shadow and explicitly setting zero padding to match
  the solid 6px border design.
- Re-qualified Store packages, portable edition, RPM packaging, and runtime evidence.

## 12.0.0 — Ecosystem & App Parity

- GTK 3/4 themes, KSyntaxHighlighting themes, and VS Code/Cursor themes in
  standard and Obsidian palettes.
- Ghostty, Alacritty, Kitty, and Foot terminal configurations.
- Doctor schema 5 with ecosystem discovery and read-only Flatpak theme access
  guidance.
- Synchronized CMake, RPM, Arch, portable, and Store package contracts.

## 11.0.0 — Deep Focus & System Completeness

- Complete native Qt 6 style primitives, official Konsole themes, and the
  Obsidian true-black companion palette.

## 10.0.0 — Everyday Precision

- Fix system removal when CMake writes a final manifest entry without a newline.
- Doctor schema 3 with isolated version discovery and edition-specific guidance.
- Component precedence, duplicate/conflict findings, and actionable read-only reports.
- Refined focus visibility, surface distinction, and composited text contrast.
- Media validation for paths, PNG dimensions, and documented provenance.
- V10 isolated lifecycle and visual evidence; unavailable physical and live Arch
  session qualification remain pending rather than inheriting v9 results.

## 9.0.0

- Fedora 44 PLM wallpaper integration without unsupported custom-greeter claims.
- Doctor JSON schema 2 with stable, read-only login-surface diagnostics.
- System Coherence graphite hierarchy and refined 16/22 px optical icons.
- Manifest schema 2 login-manager compatibility model and packaging boundaries.
- V8 migration preservation for Plasma, panel, wallpaper, PLM, and SDDM settings.

## 8.0.0

- Forge Identity editions and manifest-driven artifact graph.
- Correct KDE package roots and deterministic Store validation.
- Portable install, uninstall, migration boundary, and edition doctor.
- Three selectable wallpaper packages and compact V8 media provenance.
- Fedora and Arch packaging documentation.

Historical release notes remain under `docs/releases/` and are not current
compatibility claims.
