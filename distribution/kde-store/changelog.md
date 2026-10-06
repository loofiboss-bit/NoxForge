# NoxForge 15.0.0 — Kinetic Signal & Adaptive Motion Suite

- added native FreeDesktop / KDE `<style id="current-color-scheme">` support across all 201 scalable SVGs and 288 optical variants;
- implemented multi-stage geometric Wi-Fi and signal family (connected-00, 25, 50, 75, 100, acquiring, disconnected, locked, hotspot);
- upgraded Plasma busy widget (`busywidget.svg`) across Graphite and Obsidian themes to dual concentric orbital radar arcs;
- integrated 220ms damped horizontal error-shake on authentication failure in Lock Screen and SDDM;
- added live network and battery status badges to the lock screen;
- added Live Icon & Kinetic Motion Preview canvas to the Control Center GUI with dynamic accent previews;
- upgraded `noxforge-doctor` to Schema 8 with automated `iconAdaptation` audit;
- full v15 release contract coverage across all release gates.

# NoxForge 14.0.2 — Opacity Configurator Stability & Desktop Theme Crash Fix

- fixed KDE Plasma 6 System Settings crash (`SIGSEGV` in `KSvg::ImageSet`) caused by hollow user directories shadowing system themes;
- updated `noxforge-opacity` to require valid metadata (`metadata.json`/`metadata.desktop`) and Aurorae assets (`decoration.svg`/`themerc`) before classifying user-local directories;
- enhanced `ensure_user_copy` to safely clean up hollow shells and clone complete theme trees from system packages;
- protected `.noxforge-customization.json` receipt generation so receipts are never written to incomplete directories;
- added regression test coverage ensuring automatic recovery from hollow directory states.

# NoxForge 14.0.1 — Store Assets Refresh & Fluid TabBox Switcher

- fixed non-responsive cycling in Alt+Tab window switcher by implementing bidirectional index synchronization (`tabBox.currentIndex`);
- added smooth mouse wheel and touchpad scrolling support with wrap-around item cycling via `WheelHandler`;
- added robust keyboard navigation for arrow keys (Left/Right/Up/Down) and Tab/Backtab with RTL support;
- enhanced fluid motion with active card tactile scale (`scale: 1.03`), icon scale response (`scale: 1.08`), and kinetic expanding accent indicator bar;
- added interactive hover feedback on window cards and centered viewport range alignment;
- maintained complete parity across both Graphite and Obsidian TabBox variants;
- updated all KDE Store / OpenDesktop screenshots, hero banners, thumbnail, and marketing media.

# NoxForge 14.0.0 — Unified Control Suite & Full Ecosystem Parity

- added dedicated Obsidian lock screen to the look-and-feel package (`io.github.loofiboss.noxforge.obsidian.desktop`);
- added dedicated Obsidian TabBox KWin switcher (`io.github.loofiboss.noxforge.obsidian.desktop`);
- implemented real-time dynamic accent matrix with high-contrast electric lime notches across both palettes;
- fixed QMenu dynamic item sizing, margins, and font metrics to prevent text clipping across high-DPI scaling factors;
- added high-contrast dynamic toggle switches with clear visual states and smooth transitions;
- introduced `noxforge-ctl` CLI and PySide6 Control Center GUI (`noxforge-ctl gui` / desktop launcher) for effortless palette management;
- added systemd user timer for automated diurnal palette scheduling (Graphite by day, Obsidian at night);
- added official themes for Zed editor, btop, Starship prompt, Fastfetch, Firefox CSS, and Discord;
- upgraded `noxforge-doctor` to Schema 7 with automated configuration alignment (`--apply-sync [graphite|obsidian]`).

# NoxForge 13.0.2 — Opacity Configurator Stabilization & System Coherence

- eliminated deprecated `org.kde.PlasmaShell.refreshCurrentShell` D-Bus call preventing SIGSEGV crashes on theme reload in Plasma 6 / Qt 6;
- distinguished user opacity overrides from duplicate conflicts in `noxforge-doctor` (`[info: duplicate-customized]`), keeping edition status `ok`;
- added robust SVG attribute injection fallback and complete opacity token parsing (including percentages and scientific notation);
- added active desktop wallpaper sampling with `XDG_CONFIG_HOME` resolution and percent-encoded URL decoding;
- improved 60fps simulated frosted glass blur with center-cropped wallpaper geometry alignment and painter brush state cleanup;
- added High-DPI display scaling protection with `QScrollArea`, guaranteed slider heights, and cooperative thread termination safety.

# NoxForge 13.0.1 — Opacity & Transparency Configurator

- added `noxforge-opacity` CLI utility and Qt 6 GUI configurator for customizing panel, popup, and Aurorae window decoration transparency levels;
- added desktop entry `io.github.loofiboss.noxforge.opacity.desktop` for system application launcher integration;
- included presets (`solid`, `original`, `frost`, `glass`, `ultra`) and fine-grained percentage sliders with 60fps real-time desktop preview;
- integrated direct link to KDE Desktop Effects (Blur settings) for optimal contrast on transparent surfaces;
- packaged into Fedora RPM (COPR), portable bundle, and companion store packages.

# NoxForge 13.0.0 — True Obsidian OLED Parity & Dual-Stack Architecture

- added dedicated Obsidian Plasma Style and Global Theme (`io.github.loofiboss.noxforge.obsidian.desktop`);
- added Obsidian Aurorae window decoration with true-black titlebars, 6px border, and zero synthetic shadow;
- implemented dynamic runtime-adaptive Qt 6 C++ style plugin seamlessly switching between standard deep slate and OLED true black;
- added `NoxForge-Obsidian` (16:9 4K) and `NoxForge-Obsidian-Ultrawide` (21:9) wallpapers and SDDM Obsidian login theme;
- added official Neovim (Lua) and Helix (TOML) editor themes in standard and Obsidian palettes;
- upgraded Design Tokens to Schema 9 dual-palette authority and Doctor to Schema 6 with palette desynchronization diagnostics;
- updated CMake, RPM, Arch, portable, and companion KDE Store package contracts.

# NoxForge 12.0.1 — Aurorae Decoration Border Fix

- fixed Aurorae window decoration borders appearing as thick black rectangles on Fedora and KWin Wayland;
- disabled synthetic window shadow and zeroed padding contract to match the opaque 6px border design;
- updated qualification and release evidence across Store, portable, and complete packages.

# NoxForge 12.0.0 — Ecosystem & App Parity

- added deterministic GTK 3/4 themes in Graphite and Obsidian palettes;
- added KSyntaxHighlighting, VS Code/Cursor, and Big Four Wayland terminal themes;
- upgraded the read-only doctor to schema 5 with ecosystem and Flatpak override diagnostics;
- kept package installation non-applying and preserved the separate Store/portable/system boundaries.

# NoxForge 11.0.0 — Deep Focus & System Completeness

# NoxForge 10.1.0 — Lumina

- refined Forge, Quiet, and Ultrawide wallpapers with regenerated evidence;
- updated SDDM preview/background and splash surface;
- documented Aurorae window shadows with Plasma 6 padding;
- preserved user-local, non-applying installation and rollback boundaries.

# NoxForge 10.0.0 — Everyday Precision

- Doctor schema 3 with isolated roots, component precedence and edition-specific advice.
- Visible keyboard focus, composited disabled-text contrast and fractional-scale fixes.
- Improved TabBox text layout and correct removal of unterminated manifest entries.
- Neutral Wayland images and automatic media validation.
- Fedora/Arch automated qualification and configuration-preserving v9→v10→v9 tests.
- Physical hardware and full live-matrix qualification remain pending.
