# NoxForge 21.0.5

- Fix Unreadable Selected Items, Clipped SpinBoxes & Invisible Toggle Buttons (`libnoxforge6.so`): `PE_PanelItemViewItem` and `PE_PanelItemViewRow` now adapt to `QPalette::HighlightedText` WCAG luminance so KDE System Settings, Discover, Dolphin, and Kirigami/QQC2 selected rows always render at WCAG AA/AAA contrast (fixing dark text on `#223429`); expanded `CT_SpinBox`/`CT_ComboBox` widths and `SC_SpinBoxEditField` spacing so values like `100 %` never clip and inner frameless `QLineEdit`s no longer draw double borders; added distinct `State_On` checked toggle states (e.g. Display Orientation buttons) and quiet resting `Flat`/`AutoRaise` buttons; fixed `QSettings::IniFormat` `QStringList` `AccentColor` parsing, disabled control rendering, and indeterminate progress bar visibility.
- Harden Color Schemes, GTK 3/4, Plasma 6.8 Union CSS & Ecosystem Themes: upgraded `[Colors:Selection]` negative/neutral/visited foregrounds to WCAG AAA; removed broken `checkbutton:checked`/`radiobutton:checked` container fills in GTK 3/4 and completed GTK 3 popover/combobox/treeview/check/radio/progressbar/switch rules (0 `Gtk.CssProvider` parse errors); aligned Plasma 6.8 Union CSS selectors (`scrollbar > handle`, `checkbox > indicator`, `switch > indicator > handle`, `slider`, `spinbox`, `card`, `inlinemessage`, `monthgrid`); and fixed Obsidian/contrast issues in Kate, VS Code, Discord, Firefox, Obsidian.md, git-delta, and System Monitor.
- Polish Plasma SVGs, Aurorae v2, Icons, Cursors & Shared QML Surfaces: fixed Plasma SVG hint margins, `hint-compose-over-border`, blur masks, `tasks.svg` attention opacity, `scrollbar`/`slider`/`switch`/`radiobutton`/`checkmarks`; removed hard corner wedges from Aurorae `decoration.svg` and preserved red inactive hover/press on `close.svg`; fixed `network-wireless-connected-25.svg`, Wayland scalable cursor hollow rings and hotspots (`progress`, `color-picker`, `zoom-*`, `hand`); fixed `LockScreen.qml` `revealPassword` `TypeError`, real Caps Lock indicator, `OsdItem.qml` >100% overdrive, `TabBox` vertical layout & binding loop, `Logout`/`SystemDialog` keyboard handling, `SDDM` guards, and Obsidian TabBox default layout.
- Tooling, Doctor & Packaging Hardening: `noxforge-ctl` now places GTK `@import` before existing user rules, applies `plasma-apply-colorscheme` before writing `ColorScheme` (with `-a <hex>`), preserves Union full mode, refreshes outdated local Aurorae copies, and syncs both Aurorae variants on accent change; fixed `control_center.py` and `opacity_gui.py` (`--gui`, `"system"` accent state, border swatch readability, search filter retention, safe `QThread` shutdown); upgraded `noxforge-doctor` to detect stale shadowing `libnoxforge6.so` copies across `$QT_PLUGIN_PATH`, `~/.local/lib*`, and `/usr/local/lib*` plus `.svgz` Aurorae customizations; added `Requires: python3` to `packaging/noxforge.spec`.

# NoxForge 21.0.4

- Keep Fastfetch Strictly Opt-In (`tools/noxforge-ctl`): marked `fastfetch` as `opt_in: True` in `SUPPORTED_ECOSYSTEM_APPS` so bulk `noxforge-ctl ecosystem apply` / `ecosystem apply all` and Control Center's *Deploy All Detected Themes* never overwrite users' existing `~/.config/fastfetch/config.jsonc` or `logo.txt` automatically; fixed `fastfetch` installed-status detection to check `ecosystem-state.json` ownership instead of flagging any user config as synced; and fixed stale `ecosystem-state.json` writes when users explicitly opt into Fastfetch presets so `noxforge-ctl ecosystem restore fastfetch` reliably restores original configs.

# NoxForge 21.0.3

- Fix Plasma & KDE Text Selection Contrast (`[Colors:Selection]`): updated `color_scheme_for_palette()` in `scripts/generate_design_system.py` so `NoxForgeDark.colors`, `NoxForgeObsidian.colors`, and the embedded Plasma Desktop Theme `colors` files use high-contrast `accentPressed` (`#82D936`) selection fill with dark ink (`#0D1419` on Graphite, `#000000` on Obsidian) instead of dark `#223429`/`#192D1E` with light text — boosting Kickoff/KRunner/Plasma `TextField` selection contrast against sunken input backgrounds from `1.35:1` to `10.10:1` while delivering WCAG AAA (`10.54:1` / `11.93:1`) selected text legibility.
- Fix GTK 3 & GTK 4 CSS Parser Error (`::selection`): removed the invalid web pseudo-element `::selection` from generated `themes/NoxForge*/gtk-{3.0,4.0}/gtk.css`, retaining valid GTK CSS node selectors (`selection, entry selection, textview text selection, label selection`) so GTK 3 and GTK 4 parse all stylesheets with zero warnings or errors.

# NoxForge 21.0.2

- Fix Dolphin Dock Separator Green Dot & Splitter Metrics (`libnoxforge6.so`): fixed inverted `State_Horizontal` axis in `PE_IndicatorDockWidgetResizeHandle` (which clipped 3 dots down to a lone floating lime pixel on Dolphin's Places divider), replaced floating dots with a crisp 1px structural divider (`PM_DockWidgetSeparatorExtent = 1`, matching Breeze) with subtle `edgeHighlight` hover, and set `PM_SplitterWidth = 4` so `QSplitter` panes are cleanly draggable.
- Fix Aurorae v2 Floating Window Borders, Top-Edge Tiling & Corner Artifacts: added `hint-stretch-borders`, removed the partial accent segment inside `decoration-top` (which tiled every 28px into a dashed green top border), placed the crisp 1px Forge Notch accent cue strictly inside the fixed `decoration-topleft` corner, aligned all 36 9-patch cell bounding boxes to exact integer pixels (`0.00px` drift), replaced hard-edged stepped shadow blocks with seamless filter-free `<linearGradient>` / `<radialGradient>` ambient shadows, and slimmed floating side/bottom borders from `6px` to a sleek `2px` bezel with matching `2px` outer bottom corners.
- Fix Subpixel Corner Overflow in Plasma Desktop Theme SVGs: replaced `stroke-width="1"` top corner highlight arcs with exact 1px filled corner paths so `dialogs/background.svg`, `widgets/panel-background.svg`, and `widgets/tooltip.svg` measure exact `6.00×6.00` corner bounds with zero `-0.5px` bleed.
- Fix Live Aurorae `.svgz` Sync in `noxforge-ctl` & `noxforge-opacity`: both tools now write synchronized `decoration.svgz` alongside `decoration.svg` so KWin 6.8 immediately applies user-local Aurorae accent and opacity overrides.

# NoxForge 21.0.1

- Preserve Original Third-Party & App Icons: removed all 52 external app icon overrides from `icons/NoxForge/*/apps/` (retaining only NoxForge's own 4 Control Center & Opacity icons) so Firefox, VLC, Steam, Discord, Telegram, Bitwarden, GIMP, Dolphin, VS Code, Spotify, and all other apps keep their authentic original icons via `Inherits=breeze-dark,breeze,hicolor` (430 scalable + 896 optical system/places/mimetypes icons).
- Fix Maximized Aurorae v2 Titlebar Transparency & KF6Svg Custom CSS Stripping: split custom `.ColorScheme-Raised`, `.ColorScheme-Sunken`, `.ColorScheme-Hover`, `.ColorScheme-Pressed`, and `.NoxForge-*` classes into dedicated `<style id="noxforge-*-style">` blocks outside `<style id="current-color-scheme">` across Aurorae decorations, window buttons, and all Plasma Desktop Theme SVGs so `KF6Svg` preserves Graphite/Obsidian surfaces and edge highlights at runtime, and added dedicated `decoration-maximized-inactive` frames.
- Automatic KF6Svg & Icon Cache Purge: `noxforge-ctl` live reload and `noxforge-opacity` now clear `~/.cache/ksvg-elements`, `~/.cache/icon-cache.kcache`, and orphaned user `icon-theme.cache` files and emit `KGlobalSettings` `IconChanged` (`notifyChange 4 0`) alongside `PaletteChanged` so upgrades render immediately without stale cached frames or icons.

# NoxForge 21.0.0

- Duotone Visual Craft: 482 scalable SVGs (`56` apps, `30` distinct mimetypes, `28` duotone & 6-accent places) and 1,052 optical variants (`16x16`/`22x22` crisp monoline + `32x32`/`48x48`/`64x64` Duotone Surface).
- True PNG24 Wallpapers & Plasma 6 Dynamic Wallpaper: zero `PNG8` banding, new `16:10` (`2560x1600`, `3840x2400`) and `32:9` (`5120x1440`) aspect ratios, Plasma 6 `images_dark/` dynamic wallpaper, enriched Obsidian depth, and accent-adaptive rendering.
- Aurorae v2 & Plasma Shell Surfaces: `Shadow=true` with filter-free stepped ambient shadows, flush maximized frames, Plasma 6 `metadata.json`, user-local live accent rail sync, overhauled `notes`/`clock`/`calendar`/`glowbar` SVGs, and Look-and-Feel `osd/` + `systemdialog/` QML.
- Wayland Scalable Cursors & Tactile Forge Audio v2: 4× AA Xcursors with `1 px` contrast halo across `[24..64]px` + Plasma 6 `cursors_scalable/`, and 27 distinct DSP audio sources across 32 Freedesktop events.
- Complete Native Qt 6 Style, Modular Union CSS & Deep GTK4/Libadwaita: added `CC_Dial`, `CC_TitleBar`, `CC_MdiControls`, slider ticks, spinbox states, reactive config caching, 6-accent matrix (`+Crimson`, `+Ice`), 10 modular Union CSS sheets per variant, and deep GTK4/Libadwaita styling.
- Control Center v6, Live Hot-Reload CLI, Ecosystem v4 (25 Tools) & Doctor Schema 14: async `CommandWorker`, Wallpaper Accent Extractor, Named Presets Manager, live reload across Plasma/GTK/terminals/tmux/Neovim, Fastfetch Kinetic Studio v2, `bat`/`delta`/`fzf`/`eza`/`wofi`, and Schema 14 diagnostics.

# NoxForge 20.0.0

- Kinetic Iconography & Multi-Level Status Engine: deterministic 10%/20%/25% SVG ladders for battery (charging/discharging), Wi-Fi, signal, brightness, microphone, and volume (including mute & overdrive) bound to KDE Plasma `ColorScheme` CSS classes.
- Optical Size Differentiation & 16-Frame Sprites: 684 dedicated `16x16` and `22x22` optical SVGs paired with 404 scalable icons, synchronized `index.theme`, 16-frame animated sprites (`process-working.svg`, `process-syncing.svg`), and 8 Plasma Desktop Theme icon sheets per palette (Graphite & Obsidian).
- Control Center v5 Studio & Flatpak Isolation Support: live Kinetic Icon Studio preview (animated spinner, Battery/Wi-Fi/Volume slider, optical toggle), `noxforge-ctl icons` dynamic accent tinting, and `noxforge-ctl flatpak` sandbox override synchronization.
- Plasma 6.8 Union Style Engine & Lock Screen Forge Status Pill: expanded `union/styles/noxforge` & `noxforge-obsidian` with multi-state SVG masks and focus rings, plus a token-bound Lock Screen Status Pill with `reducedMotion` compliance.
- Developer Ecosystem v3: added reactive Graphite/Obsidian themes with `.noxforge.bak` rollback for Yazi, Lazygit, Zellij, and Tmux (18 supported ecosystem apps).
- Diagnostics Schema 13: extended `noxforge-doctor --json` with `iconLevelMatrix` and animated/optical verification.
- Updated `noxforge-ctl`, `noxforge-doctor`, and `noxforge-opacity` Control Center & manual documentation along with refreshed v20.0.0 Store screenshots.

# NoxForge 19.0.0 — KDE Plasma 6.8 Union Style Engine, KWin CSD & Wayland Precision

- introduced KDE Plasma 6.8 Union Style Engine (`plasma-union`) with deterministic generation of `union/styles/noxforge` (Graphite) and `union/styles/noxforge-obsidian` (Obsidian) via `design/tokens.json` (Schema 15) and dynamic `custom-color("kcolorscheme", ...)` CSS variable bindings;
- added hybrid Union orchestration in `noxforge-ctl union [--enable|--disable|--status|--profile]` and automated `unionStyle` synchronization in `kdeglobals`;
- added reversible KWin 6.8 client-side decoration window rules (`noxforge-ctl kwin-csd [--enable|--disable|--status]`) and Plasma 6.8 System Monitor telemetry preset (`apps/systemmonitor/noxforge-telemetry.page`);
- upgraded Control Center v4 (`tools/control_center.py`) with wallpaper live thumbnail preview, real-time WCAG AAA/AA palette and contrast swatch bar, and scrollable responsive layout;
- expanded supported ecosystem apps with native themes for Obsidian.md (`apps/obsidian/`) and Rofi/Wofi (`apps/rofi/`) plus shell tab completion (`noxforge-ctl completion`);
- upgraded `tools/noxforge-doctor` to Schema 12 (`unionStyleStatus`, `waylandCompositor`) and eliminated all `metadata-unknown` warnings on real installations;
- expanded verified Linux distribution compatibility to include Fedora 44 and Fedora 45 alongside Arch Linux.

# NoxForge 18.0.0 — Libadwaita Parity, Reversible Ecosystem Engine v2 & Dynamic Control Core

- upgraded GTK 3.0 and 4.0 themes with dynamic `@accent_color` CSS variable bindings and managed `~/.config/gtk-{3,4}.0/gtk.css` `@import` chaining for full Libadwaita surface and accent parity;
- added opt-in Flatpak theme override orchestration (`noxforge-ctl flatpak --enable|--disable|--status`) and Control Center toggle card;
- upgraded Ecosystem Engine to v2 with automatic `.noxforge.bak` backups, `noxforge-ctl ecosystem restore`, stateful tracking (`ecosystem-state.json`), and live profile/accent propagation across deployed developer tools and Konsole;
- extracted shared `tools/noxforge_core.py` library and upgraded Control Center v3 (`tools/control_center.py` and `tools/opacity_gui.py`) with real-time self-theming reflecting active Graphite/Obsidian surfaces and accent colors;
- upgraded `design/tokens.json` to Schema 14 and `tools/noxforge-doctor` to Schema 11 (`noxforgeCoreStatus`, `gtkChainStatus`, `ecosystemState`).

# NoxForge 17.0.1 — Authentic Dolphin Grid & Quick Onboarding

- aligned Dolphin store screenshot showcase with authentic KDE Plasma 6 icon grid view and standard navigation;
- enabled floating panel mode (`panel.floating = true`) in desktop layout script for modern elevated dock aesthetics;
- introduced `noxforge-ctl apply [profile] [--layout]` for automated 1-click end-to-end desktop profile setup;
- added quick onboarding "Apply NoxForge Setup" button in Control Center GUI overview tab.

# NoxForge 17.0.0 — Total Single-Source Authority, Dynamic Accent Ecosystem & Portable Integrity

- upgraded single-source QML architecture to Schema 2, unifying Lock Screen, SDDM greeters, KWin TabBox switchers, Splash screen, and Logout greeter with byte-parity generation across Graphite and Obsidian surfaces;
- implemented dynamic accent harmonization across native Qt 6 C++ style plugin, CLI, and Control Center for all accent modes (Electric Lime, Forge Cyan, Cyber Violet, Molten Amber, and WCAG AA validated custom accents);
- hardened authentication surfaces with password reveal security policies (`allowEmptyPassword=false` default) and visual indicators;
- introduced `noxforge-ctl ecosystem` CLI commands (`status`, `apply`, `sync`, `list`) and configurable diurnal schedule transition times (`--day-time` and `--night-time`);
- added 5th tab to Control Center GUI ("Ecosystem & Apps") for seamless management of Terminal themes, Neovim/Helix/Zed editors, Fastfetch, Starship, Firefox, and Discord;
- upgraded `noxforge-doctor` to Schema 10 with ecosystem alignment and comprehensive single-source validation.

# NoxForge 16.0.0 — Single Source, Kinetic Accessibility & Verified Truth

- single-source QML architecture for Lock Screen, SDDM greeters, and KWin TabBox switchers with deterministic byte-parity generation;
- full WCAG 2.2.2 / 2.3.3 motion accessibility compliance with static 220ms edge-flash error indicators replacing kinetic spring shakes under reduced motion;
- guarded LoofiFaceID integration for biometric facial unlock in Plasma lock screens and SDDM with zero-friction password fallback;
- unified Control Center GUI (`tools/control_center.py`) consolidating Profile, Opacity, Accessibility, and System Health diagnostics;
- real-time WCAG AA 4.5:1 contrast calculator for custom accent colors;
- updated Plasma busy indicator widget to smooth continuous single-arc rotation;
- upgraded `noxforge-doctor` to Schema 9 with automated checks for QML drift, motion policies, accent contrast, and version coherence.

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
