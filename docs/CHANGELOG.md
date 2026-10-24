# Changelog

## 18.0.0 — Libadwaita Parity, Reversible Ecosystem Engine v2 & Dynamic Control Core

- GTK 3/4, Libadwaita & Flatpak Parity:
  - Bound interactive and focus selectors in generated GTK 3.0 and 4.0 CSS (`themes/NoxForge` and `themes/NoxForgeObsidian`) to `@accent_color`, `@accent_bg_color`, `@accent_fg_color`, and `@theme_selected_bg_color`.
  - Replaced partial GTK accent snippets with a managed `@import` + `@define-color` block in `~/.config/gtk-3.0/gtk.css` and `~/.config/gtk-4.0/gtk.css` for full Libadwaita surface and accent parity.
  - Added opt-in `noxforge-ctl flatpak --enable|--disable|--status` orchestration.
- Reversible & Reactive Ecosystem Engine v2:
  - Added automatic `.noxforge.bak` backups before deploying over user configs (`starship.toml`, `fastfetch/config.jsonc`, Firefox `userChrome.css`, etc.) and `noxforge-ctl ecosystem restore [apps...|all]`.
  - Added stateful tracking in `~/.config/noxforge/ecosystem-state.json` and automatic propagation of profile switches (`graphite`/`obsidian`) and custom/matrix accents across deployed ecosystem tools and Konsole profiles.
- Shared Python Core & Control Center v3:
  - Extracted `tools/noxforge_core.py` to unify version resolution, XDG paths, KConfig access, WCAG 2.1 contrast calculation, and dynamic Qt stylesheet generation.
  - Upgraded `tools/control_center.py` and `tools/opacity_gui.py` with live self-theming (`build_qt_stylesheet()`), per-app `Restore Backup` controls, and a Flatpak Theme Override card.
- Tokens Schema 14 & Doctor Schema 11:
  - Upgraded `design/tokens.json` to Schema 14 (`gtk` and `ecosystem` contracts) and `tools/noxforge-doctor` to Schema 11 (`noxforgeCoreStatus`, `gtkChainStatus`, `ecosystemState`).

## 17.0.1 — Authentic Dolphin Grid & Quick Onboarding

- Aligned Dolphin store showcase with authentic Plasma 6 icon grid view and added 1-click `noxforge-ctl apply` onboarding.

## 17.0.0 — Total Single-Source Authority, Dynamic Accent Ecosystem & Portable Integrity

- Upgraded single-source QML generation to Schema 2 across all 6 component pairs (12 variants), Tokens Schema 13, dynamic C++ style selection tinting, Control Center Tab 5 (`Ecosystem & Apps`), and Doctor Schema 10.

## 16.0.0 — Single Source, Kinetic Accessibility & Verified Truth

- Single-Source QML Architecture & Drift-Proof Generator:
  - Established canonical single-source QML templates in `qml/shared/` for Lock Screen (`LockScreen.qml`), SDDM (`Main.qml`), and KWin TabBox Window Switcher (`main.qml`).
  - Added deterministic variant generation pipeline (`scripts/generate_design_system.py`) and schema configuration (`design/qml-variants.json`) generating all 6 variant files across Graphite and Obsidian surfaces with automated `// GENERATED from ...` headers.
  - Added drift prevention step to `scripts/validate.py` and byte-level parity unit tests in `tests/test_qml_variants.py`.
- Kinetic Motion & Accessibility:
  - Respect system animation speed (`Kirigami.Units.longDuration <= 0`, `AnimationDurationFactor <= 0`, or `NOXFORGE_REDUCED_MOTION=1`) across all shared and generated QML surfaces.
  - Implemented 220ms static edge-flash error indicator (`ColorScheme-NegativeText`) replacing horizontal spring shakes under reduced motion in Lock Screen and SDDM.
  - Added accessible roles and descriptions (`Accessible.role`, `Accessible.name`, `Accessible.description`) across authentication password inputs, action buttons, and error banners for screen readers.
  - Added strict WCAG AA 4.5:1 contrast enforcement in `noxforge-ctl accent custom '#RRGGBB'` and Control Center against both Graphite (`#141E25`) and Obsidian (`#000000`) surfaces.
- Guarded Experimental LoofiFaceID Authentication:
  - Implemented non-invasive, guarded face-authentication hooks in single-source SDDM (`Main.qml`) and Lock Screen (`LockScreen.qml`) templates.
  - Safe zero-side-effect fallback to standard password authentication when biometrics or PAM APIs are absent.
  - Strict preservation of the non-applying desktop installation boundary: NoxForge installs no daemons, PAM configs, or system policies.
  - Documented API contract, qualification limits, and troubleshooting in `docs/EXPERIMENTAL_FACE_AUTH.md`.
- Unified Control Center GUI:
  - Unified desktop theme customization into a multi-tab interface (`tools/control_center.py`):
    - Profile & Palette tab (Graphite and Obsidian presets, system notification).
    - Opacity tab (blur, transparency, and background adjustments with preset levels).
    - Accessibility & Motion tab (kinetic reduced-motion simulation and live WCAG AA custom accent contrast calculator).
    - System Health & Diagnostics tab (integrated Doctor audit with one-click refresh).
  - CLI routing support via `--tab <profile|opacity|a11y|health>`.
  - Maintained backward compatibility via `tools/opacity_gui.py` thin launcher shim delegating to `control_center.py --tab opacity`.
  - Added comprehensive headless PySide6 GUI test suite in `tests/test_control_center_gui.py` (`QT_QPA_PLATFORM=offscreen`).
- Diagnostics, Validation & Rolling Contracts:
  - Upgraded `noxforge-doctor` to Schema 9 with automated audits for `qmlVariantDrift`, `reducedMotion` policy, `customAccentContrast`, `faceAuthApi`, and `versionCoherence`.
  - Archived 25 obsolete per-version test suites into `tests/archive/`, reducing pytest run times by >65%.
  - Introduced rolling release contract tests in `tests/test_release_contract.py`.
  - Accelerated `scripts/validate.py` with step progress output, `--only <step>`, and `--list` flags.
  - Added fast CI preflight workflow in `.github/workflows/ci.yml` (<3 min runtime) with zero-ruff hygiene.

## 15.0.0 — Kinetic Signal & Adaptive Motion Suite

- Adaptive FreeDesktop / KDE Current-Color-Scheme Iconography:
  - Embed `<style id="current-color-scheme">` across all 201 scalable SVGs and 288 optical variants (16x16 and 22x22).
  - Native response to active Plasma color schemes using `ColorScheme-Text`, `ColorScheme-Highlight`, `ColorScheme-NeutralText`, and `ColorScheme-NegativeText`.
- Multi-Stage Geometric Wi-Fi & Signal Family:
  - High-precision geometric curves for signal levels: `network-wireless-connected-00`, `25`, `50`, `75`, `100`.
  - Specialized states: `acquiring`, `locked`, `hotspot`, and `disconnected` with 45° Forge Notch negative slash.
  - Complete battery indicator suite: `battery-000` through `battery-100` and charging glyphs.
- Dual-Ring Orbital Radar Busy Widget:
  - Overhaul `busywidget.svg` across Graphite and Obsidian themes to dual concentric orbital radar arcs.
- Kinetic Motion Polish Across Plasma Surfaces:
  - Integrated 220ms damped horizontal error-shake (`errorShakeAnim`, +/-8px -> +/-4px -> 0px) on authentication failure in Lock Screen (`LockScreen.qml`) and SDDM (`Main.qml`).
  - Added live network and battery status badges to lock screen.
  - Fluid bezier curves and tactile elevation in KWin window switcher.
- Control Center GUI Live Visual Hub:
  - Interactive Live Icon & Kinetic Motion Preview canvas previewing Wi-Fi, battery, and audio indicators reflecting dynamic accents.
  - Interactive test trigger for 220ms kinetic error-shake spring animation.
- Diagnostics & Automated Contracts:
  - Upgraded `noxforge-doctor` to Schema 8 with automated `iconAdaptation` audit.
  - Added `tests/test_v15_contracts.py` ensuring contract adherence across all release gates.
  - Updated dedicated application icons for Control Center and Opacity Configurator in hicolor icon theme.

## 14.0.2 — Opacity Configurator Stability & Desktop Theme Crash Fix

- Fix KDE Plasma 6 System Settings crash (`SIGSEGV` in `KSvg::ImageSet`):
  - Prevent `noxforge-opacity` from classifying hollow/empty user directories as valid local themes.
  - Require valid metadata (`metadata.json` or `metadata.desktop`) and Aurorae assets (`decoration.svg` or `themerc`) before treating a directory as `user-local`.
  - Fix `ensure_user_copy` to safely clean up hollow directory shells and clone complete theme assets from `/usr/share/plasma/desktoptheme` and `/usr/share/aurorae/themes`.
  - Prevent writing customization receipt (`.noxforge-customization.json`) to incomplete directories lacking metadata.
  - Add regression unit tests in `tests/test_opacity.py` verifying fallback and self-healing behavior.

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
