# NoxForge 14.0.0 — Unified Control, Dynamic Accents & Complete Desktop Immersion

This plan records the NoxForge version 14 release scope and implementation
sequence, published as `v14.0.0`. It builds upon the 13.0.2 release and
elevates NoxForge from a collection of visual components to a fully unified,
immersive Linux desktop product for Fedora 44 and Arch Linux (KDE Plasma 6.7+,
Qt 6.11, Wayland).

## Product contract

NoxForge 14 preserves the authentic graphite surfaces, electric-lime precision
accent, Forge Notch (4 px) identity, system typography, KDE package roots,
three-edition architecture, and non-applying installation boundary.

Version 14 expands the scope across five major pillars:
1. **Tokens Schema 10 & Accent Matrix Authority:** Formally introduces Schema 10
   into `design/tokens.json`, defining the Forge Accent Matrix (`lime`, `cyan`,
   `violet`, `amber`) and dynamic system accent mapping while guaranteeing WCAG
   AA/AAA contrast compliance across both Graphite and OLED canvases.
2. **KWin Alt+Tab Obsidian Parity:** Delivers a dedicated OLED window switcher
   (`kwin/tabbox/io.github.loofiboss.noxforge.obsidian.desktop`) matching the
   pitch-black `#000000` aesthetic of the Obsidian Global Theme.
3. **Plasma 6 Lock Screen (Total Immersion):** Delivers custom, Wayland-native
   `LockScreen.qml` implementations for both Graphite and Obsidian Look-and-Feel
   packages featuring the Forge Notch, kinetic password focus, typography, and
   MPRIS media controls.
4. **Dynamic Qt 6 C++ Style Accent Engine:** Upgrades `noxforgestyle.so` to
   dynamically query `QPalette::Highlight` or `kdeglobals [General] AccentColor`
   and respect `NOXFORGE_ACCENT` overrides across all native Qt 6 widgets.
5. **Unified Control Suite (`noxforge-ctl` & NoxForge Control Center):**
   Introduces `tools/noxforge-ctl` for single-command profile switching
   (`switch`), accent selection (`accent`), opacity manipulation, and day/night
   scheduling. Upgrades the Qt 6 GUI (`tools/control_center.py`) into a 3-tab
   Control Center with system menu integration (`distribution/io.github.loofiboss.noxforge.controlcenter.desktop`).
6. **Ecosystem Horizon:** Delivers official themes for Firefox / LibreWolf
   (`userChrome.css`), Zed Editor, btop resource monitor, Starship prompt,
   Fastfetch, and Discord / Vesktop.
7. **Doctor Schema 7 & Debt Remediation:** Upgrades `noxforge-doctor` to Schema 7
   with automated `--apply-sync` alignment and audits for all v14 components.
   Synchronizes `tools/noxforge-opacity` versioning and stabilizes test suite paths.
8. **Synchronized Packaging and CI Automation:** Updated CMake, RPM spec, Arch PKGBUILD,
   release manifest, and automated v14 contract test suite (`tests/test_v14_contracts.py`).

## Sequential phases

1. **Tokens and Authority:** Establish `NOXFORGE_V14_PLAN.md`, update
   `IMPLEMENTATION_PLAN.md`, bump `VERSION` to 14.0.0, and specify `accents`
   in `design/tokens.json` under Schema 10.
2. **KWin TabBox Obsidian Parity:** Create `kwin/tabbox/io.github.loofiboss.noxforge.obsidian.desktop`
   and update `scripts/generate_design_system.py` to generate tokens and motion policies.
3. **Plasma 6 Lock Screen:** Implement `contents/lockscreen/LockScreen.qml` in
   both Graphite and Obsidian Look-and-Feel packages.
4. **Dynamic Qt 6 C++ Style Adaptation:** Upgrade `src/style/noxforgepalette.h`
   and `src/style/noxforgestyle.cpp` to support dynamic accents.
5. **Unified Control CLI (`noxforge-ctl`):** Implement `tools/noxforge-ctl`
   with `switch`, `accent`, `opacity`, `doctor`, and `schedule` actions.
6. **NoxForge Control Center GUI:** Implement `tools/control_center.py` and
   desktop entry `io.github.loofiboss.noxforge.controlcenter.desktop`.
7. **Ecosystem Horizon:** Deliver Firefox userChrome/manifest, Zed, btop,
   Starship, Fastfetch, and Discord theme configurations.
8. **Doctor Schema 7 & Technical Debt:** Upgrade `tools/noxforge-doctor` to
   Schema 7, fix opacity tool version desync, and resolve test suite path handling.
9. **Build, Packaging, and Qualification:** Update `CMakeLists.txt`, `packaging/noxforge.spec`,
   `packaging/arch/PKGBUILD`, `distribution/release-manifest.json`, deliver
   `tests/test_v14_contracts.py`, and run the complete validation and test suite.

## Acceptance criteria

- `design/tokens.json` complies with Schema 10, defining `colors`, `colorsObsidian`, and `accents`.
- `kwin/tabbox/io.github.loofiboss.noxforge.obsidian.desktop` installs cleanly and matches Obsidian tokens.
- `LockScreen.qml` in both Look-and-Feel packages parses cleanly with valid QML bindings.
- `noxforgestyle.so` dynamically adapts both palette surfaces (Graphite/Obsidian) and accent highlights.
- `noxforge-ctl` switches profiles cleanly, reports status, and invokes the Control Center GUI.
- Firefox, Zed, btop, Starship, Fastfetch, and Discord themes conform strictly to design tokens.
- `noxforge-doctor` Schema 7 executes in read-only mode and discovers all v14 components.
- All Python tests (`scripts/run_python_tests.py`), `pytest`, and repository validations (`scripts/validate.py`) pass with zero errors.
- Package specifications stage and install all v14 paths accurately.
