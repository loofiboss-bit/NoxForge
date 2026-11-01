# NoxForge 19.0.0 — Plasma 6.8 Union Engine, Wayland-Native KWin & Kinetic Studio Suite

This plan records the NoxForge version 19 release scope and implementation
sequence, targeted for publication as `v19.0.0`. It builds upon the `v18.0.0`
baseline and elevates NoxForge for the **KDE Plasma 6.8** era across Fedora 44+
and Arch Linux on Wayland: introducing first-class **KDE Union Style Engine**
(`plasma-union` 6.8) CSS themes, **Wayland-only KWin 6.8** compositor & CSD
window-rule orchestration, the **Fastfetch Kinetic Studio v2** telemetry & ANSI
logo suite, **Plasma Login Manager (`plasmalogin`)** multi-wallpaper parity,
**Plasma 6.8 System Monitor** telemetry page presets, **Control Center v4**,
**Tokens Schema 15**, and **Doctor Schema 12** with 100% component metadata
coverage (`0` `metadata-unknown`).

## Product contract

NoxForge 19 preserves the authentic graphite surfaces, true-black Obsidian OLED
variant, electric-lime precision accent, Forge Notch (`4 px`) identity, system
typography, KDE package roots, three-edition architecture, and non-applying
installation boundary.

Version 19 expands and hardens the system across six major pillars:

1. **Tokens Schema 15 & Plasma 6.8 Wayland-Native Baseline:**
   - Upgrades `design/tokens.json` to Schema 15, codifying the `union` style
     contract (`engineVersion: "6.8"`, `inputType: "css"`, `inputVersion: 1`,
     `styles: ["noxforge", "noxforge-obsidian"]`, `kcolorschemeBinding: true`),
     `kwin68` Wayland-only & CSD window-rule contract, and `fastfetch` Kinetic
     Studio preset contract (`presets: ["main", "cyber", "minimal"]`).
   - Elevates platform requirements and documentation (`README.md`,
     `docs/COMPATIBILITY.md`, `packaging/noxforge.spec`, `packaging/arch/PKGBUILD`,
     `distribution/release-manifest.json`) to **KDE Plasma/KWin 6.8+ & Qt 6.11+
     (Wayland-Native)** and adds `Recommends: plasma-union` (RPM) and
     `optdepends=('plasma-union: KDE Plasma 6.8 unified CSS style engine')` (Arch).

2. **KDE Plasma 6.8 Union Style Engine (`union/styles/noxforge*`):**
   - Extends `scripts/generate_design_system.py` to deterministically generate
     two complete KDE Union CSS styles from `design/tokens.json`:
     - `union/styles/noxforge/` (`Breeze/NoxForge Graphite Union`)
     - `union/styles/noxforge-obsidian/` (`NoxForge Obsidian OLED Union`)
   - Each Union style ships `metadata.json` (`input-type: "css"`,
     `input-version: 1`, `version: "19.0.0"`) and modular CSS rules in
     `contents/css/` (`style.css`, `variables.css`, `defaults.css`,
     `application.css`, `button.css`, `bars.css`, `tabs.css`, `delegate.css`,
     `text.css`, `check.css`, `popup.css`, `kirigami.css`, `tables.css`,
     `calendar.css`, `widgets.css`) binding to `custom-color("kcolorscheme", ...)`
     for dynamic accent parity while enforcing NoxForge's `4 px` Forge Notch
     geometry, crisp `1 px` surface borders, and tactile hover/focus states.
   - Hybrid orchestration in `noxforge-ctl`:
     - `noxforge-ctl switch`, `apply`, and `sync` automatically synchronize
       `unionStyle=noxforge` (or `noxforge-obsidian`) in `kdeglobals` (`[KDE]`)
       while keeping `libnoxforge6.so` (`NoxForge`) / `Breeze` as the default
       `widgetStyle`.
     - Adds `noxforge-ctl union [--enable|--disable|--status|--profile <graphite|obsidian>]`
       for users who want to toggle full Union mode (`widgetStyle=Union` +
       `unionStyle`) or inspect Union engine readiness via `union-styletool`.

3. **KWin 6.8 Wayland-Only Compositor, CSD Window Rules & System Monitor Telemetry:**
   - Adds reversible KWin 6.8 Client-Side Decoration (CSD) & third-party app
     border/corner/shadow rule synchronization (`noxforge-ctl kwin-csd
     [--enable|--disable|--status]`) in `~/.config/kwinrulesrc` (with
     `.noxforge.bak` backup), harmonizing Steam, Electron/CEF, and client-decorated
     windows with NoxForge's active surface and border geometry on KWin 6.8.
   - Generates a Plasma 6.8 System Monitor (`plasma-systemmonitor`) telemetry page
     preset (`apps/systemmonitor/noxforge-telemetry.page`, installed to
     `/usr/share/plasma-systemmonitor/noxforge-telemetry.page` and deployable via
     `noxforge-ctl ecosystem apply systemmonitor`) showcasing CPU, GPU/VRAM %
     (new in Plasma 6.8), RAM, Swap, and Network sensors tinted with NoxForge
     accent and detail colors.

4. **Fastfetch "Kinetic Studio" v2 & Dynamic ANSI Logo Suite:**
   - Formalizes and completes the Fastfetch Kinetic Studio v2 telemetry dashboard
     in `scripts/generate_design_system.py` (`tools/fastfetch/noxforge.jsonc`,
     `noxforge-cyber.jsonc`, `noxforge-minimal.jsonc`), organized into five
     visual sections (`✦ SYSTEM IDENTITY ✦`, `✦ WORKSPACE SUITE ✦`,
     `✦ HARDWARE ENGINE ✦`, `✦ TELEMETRY & RESOURCES ✦`,
     `✦ CONNECTIVITY & MEDIA ✦`) with progress bars and Nerd Font glyphs.
   - Generates and packages three official NoxForge ANSI art logos in
     `tools/fastfetch/` (`logo.txt`, `logo_cyber.txt`, `logo_minimal.txt`),
     installed to `/usr/share/noxforge/fastfetch/` and `~/.local/share/noxforge/fastfetch/`.
   - Extends `noxforge-ctl ecosystem apply fastfetch` and adds
     `noxforge-ctl fastfetch [--preset <main|cyber|minimal>] [--status]` to deploy
     both `config.jsonc` and active logo assets into `~/.config/fastfetch/` with
     automatic `.noxforge.bak` backup/restore and dynamic accent RGB re-coloring.

5. **Plasma Login Manager (`plasmalogin` 6.8) & Wallpaper Detection Fixes:**
   - Fixes the wallpaper detection regex in `tools/noxforge-doctor`
     (`detect_wallpaper()`) and `edition_report()` (`wallpaperVariants`) so all
     five wallpapers (`NoxForge`, `NoxForge-Quiet`, `NoxForge-Ultrawide`,
     `NoxForge-Obsidian`, `NoxForge-Obsidian-Ultrawide`) are recognized instead of
     reporting Obsidian wallpapers as `"other"`.
   - Upgrades `login_surface_report()` in `tools/noxforge-doctor` so Plasma 6.8's
     `plasmalogin` (`plasma-login-manager`) recognizes all five NoxForge wallpaper
     packages when configured in `/etc/plasmalogin.conf` or
     `/usr/lib/plasmalogin/defaults.conf`, reporting the exact active wallpaper
     variant.

6. **Control Center v4 & Doctor Schema 12 (Zero `metadata-unknown`):**
   - Upgrades `tools/control_center.py` to **Control Center v4**:
     - Adds a **Plasma 6.8 Union Style Engine** card (displaying `unionStyle`
       sync state, installed Union styles, and one-click Hybrid / Full Union mode
       controls).
     - Adds an interactive **Fastfetch Kinetic Studio Preset Selector** (`Main`,
       `Cyber Matrix`, `Minimal HUD`) and **KWin 6.8 CSD Rule Harmonizer** card in
       `Ecosystem & Apps`.
     - Adds **Union Engine** and **Wayland KWin 6.8** health badges in
       `System Health & Doctor`.
   - Upgrades `tools/noxforge-doctor` to **Schema 12**:
     - Embeds deterministic `@noxforge-version: 19.0.0` metadata headers/keys
       across all generated theme, syntax, terminal, editor, browser, QML, and
       icon/sound/cursor `index.theme` files, and teaches `metadata_version()` to
       extract versions across all 45+ components plus `libnoxforge6.so` —
       reducing `[info: metadata-unknown]` issues from 14+ to **0**.
     - Adds `unionStyleStatus` (auditing `/usr/share/union/styles/noxforge*` and
       `kdeglobals` `unionStyle`) and `waylandCompositor` (auditing Plasma 6.8
       Wayland-only session & KWin CSD rule status).

## Sequential phases

1. **Milestone 1 — Branch Setup, Tokens Schema 15 & Version 19.0.0 Sync:**
   Create feature branch `feat/v19-plasma-6.8-union`, bump `VERSION` to `19.0.0`
   via `scripts/sync_version.py`, upgrade `design/tokens.json` to Schema 15, and
   update `docs/IMPLEMENTATION_PLAN.md` and `distribution/release-manifest.json`
   (`baseline`: `18.0.0`).
2. **Milestone 2 — KDE Plasma 6.8 Union Style Generator & Orchestration:**
   Extend `scripts/generate_design_system.py` to generate `union/styles/noxforge/`
   and `union/styles/noxforge-obsidian/` (metadata + 15 modular CSS files each),
   wire `unionStyle` synchronization and the `union` subcommand into `noxforge-ctl`,
   and stage Union styles across CMake, RPM, Arch, and portable installers.
3. **Milestone 3 — Fastfetch Kinetic Studio v2, KWin 6.8 CSD & System Monitor:**
   Complete the Fastfetch Kinetic Studio generator (`noxforge.jsonc`,
   `noxforge-cyber.jsonc`, `noxforge-minimal.jsonc`, `logo.txt`, `logo_cyber.txt`,
   `logo_minimal.txt`), generate `apps/systemmonitor/noxforge-telemetry.page`, and
   add `noxforge-ctl fastfetch` and `noxforge-ctl kwin-csd` orchestration with
   reversible `.noxforge.bak` backups.
4. **Milestone 4 — Doctor Schema 12, PLM/Obsidian Wallpaper Fixes & Zero `metadata-unknown`:**
   Embed version headers across all generated component assets, upgrade
   `metadata_version()` in `tools/noxforge-doctor` to resolve all component
   versions (eliminating `metadata-unknown`), fix Obsidian wallpaper regexes in
   `detect_wallpaper()`, `edition_report()`, and `login_surface_report()`, and
   implement Schema 12 (`unionStyleStatus`, `waylandCompositor`).
5. **Milestone 5 — Control Center v4 GUI Upgrade:**
   Upgrade `tools/control_center.py` with the Plasma 6.8 Union Engine card,
   Fastfetch Kinetic Studio preset selector, KWin 6.8 CSD toggle, and Schema 12
   Doctor health badges, backed by headless `QT_QPA_PLATFORM=offscreen` unit tests.
6. **Milestone 6 — Packaging Parity, Release Contracts & Gate Qualification:**
   Update `CMakeLists.txt`, `packaging/noxforge.spec` (`kwin >= 6.8`,
   `plasma-workspace >= 6.8`, `Recommends: plasma-union`), `packaging/arch/PKGBUILD`,
   portable scripts, and `docs/COMPATIBILITY.md`; create `docs/evidence/v19` and
   `tests/test_v19_contracts.py`; and pass `scripts/validate.py`, `pytest`, `ctest`,
   and `scripts/release-check.py`.

## Acceptance criteria

- `design/tokens.json` complies with Schema 15.
- `scripts/generate_design_system.py` deterministically generates `union/styles/noxforge/`
  and `union/styles/noxforge-obsidian/` with zero drift, valid `metadata.json`
  (`input-type: "css"`, `input-version: 1`), and `custom-color("kcolorscheme", ...)`
  variable bindings.
- `noxforge-ctl switch`, `apply`, and `sync` update `unionStyle` in `kdeglobals`,
  and `noxforge-ctl union` manages hybrid/full Union mode cleanly.
- Fastfetch Kinetic Studio v2 (`noxforge.jsonc`, `noxforge-cyber.jsonc`,
  `noxforge-minimal.jsonc`) and all 3 ANSI logos (`logo.txt`, `logo_cyber.txt`,
  `logo_minimal.txt`) are generated, packaged, and dynamically accent-synced via
  `noxforge-ctl fastfetch` / `ecosystem apply fastfetch`.
- `noxforge-doctor` Schema 12 reports **0** `metadata-unknown` issues on a complete
  installation, accurately detects all 5 NoxForge wallpapers across both Desktop
  and `plasmalogin` (PLM), and reports `unionStyleStatus` and `waylandCompositor`.
- Control Center v4 renders and operates Union, Fastfetch preset, KWin CSD, and
  Schema 12 health controls under headless PySide6 testing (`QT_QPA_PLATFORM=offscreen`).
- All Python (`pytest`, `run_python_tests.py`), CTest, `scripts/validate.py`, and
  `scripts/release-check.py` gates pass with zero errors.
