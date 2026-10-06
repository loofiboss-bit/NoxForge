# NoxForge 15.0.0 — Kinetic Motion, Adaptive Vector Iconography & Visual Precision

This plan records the NoxForge version 15 release scope and implementation
sequence, published as `v15.0.0`. It builds upon the 14.0.2 release and
elevates NoxForge into a living, kinesthetically responsive desktop experience
featuring dynamic vector iconography, multi-tier Wi-Fi signal rendering,
FreeDesktop color scheme integration, and machined micro-animations across
KDE Plasma 6, SDDM, and Qt 6.

## Product contract

NoxForge 15 preserves the authentic graphite surfaces, electric-lime precision
accent, Forge Notch (4 px) identity, system typography, KDE package roots,
three-edition architecture, and non-applying installation boundary.

Version 15 expands the scope across five major pillars:
1. **Tokens Schema 11 & Kinetic Authority:** Formally introduces Schema 11
   into `design/tokens.json`, defining signal tier specifications (`signalTiers`:
   0, 25, 50, 75, 100), inactive attenuation opacities, and kinetic interaction
   parameters (`errorShake`, `cardScale`, `progressPulseMs`).
2. **Next-Generation Vector Iconography Suite & Wi-Fi Multi-Stage System:**
   Overhauls vector iconography generation with native FreeDesktop/KDE Plasma
   `<style id="current-color-scheme">` support (`ColorScheme-Text`,
   `ColorScheme-Highlight`, `ColorScheme-NeutralText`, `ColorScheme-NegativeText`).
   Delivers a full multi-stage Wi-Fi signal suite (`network-wireless-connected-00`,
   `25`, `50`, `75`, `100`, `acquiring`, `disconnected`, `locked`, `hotspot`) with
   mathematically centered arcs, attenuated inactive segments, and 45° Forge
   Notch disconnection slashes.
3. **Kinetic Motion Polish Across Plasma 6 Surfaces:**
   - **Lock Screen (`LockScreen.qml`):** Wayland-native damped horizontal error-shake
     animation upon authentication failure, smooth Forge Notch focus expansion,
     and interactive button hover transitions.
   - **SDDM Login Theme (`Main.qml`):** Password rejection shake feedback and
     smooth session dropdown transitions.
   - **Alt+Tab Switcher (`Switcher.qml`):** Seamless bezier selection glide and
     card scaling.
   - **Plasma Shell Busy Widget (`busywidget.svg`):** Modern orbital radar spinner
     geometry with accented rotational lead.
4. **Control Center GUI Live Visual Hub:**
   Enhances `tools/control_center.py` with an interactive vector icon preview
   panel reflecting real-time accent shifts (Lime, Cyan, Violet, Amber) and
   Graphite/Obsidian palette switches, alongside motion duration controls.
5. **Doctor Schema 8 & Release Qualification:**
   Upgrades `tools/noxforge-doctor` to Schema 8, auditing new v15 icon files,
   dynamic ColorScheme headers, and validating the complete automated contract suite
   in `tests/test_v15_contracts.py`.

## Sequential phases

1. **Tokens and Authority:** Establish `NOXFORGE_V15_PLAN.md`, update
   `IMPLEMENTATION_PLAN.md`, bump `VERSION` to 15.0.0, and specify `signal`
   and `interactions` in `design/tokens.json` under Schema 11.
2. **Vector Icon Generation & Wi-Fi Suite:** Upgrade `scripts/generate_visual_assets.py`
   to inject `current-color-scheme` CSS blocks and generate complete multi-tier Wi-Fi,
   battery, and volume suites across scalable, 22x22, and 16x16 contexts.
3. **Plasma 6 & SDDM Kinetic Motion:** Implement error-shake animation and focus
   transitions in `LockScreen.qml` (Graphite and Obsidian), SDDM `Main.qml`, and
   upgrade `busywidget.svg`.
4. **Control Center Live Preview Hub:** Upgrade `tools/control_center.py` with
   real-time icon and accent preview canvas.
5. **Doctor Schema 8 & Diagnostics:** Update `tools/noxforge-doctor` to Schema 8.
6. **Build, Packaging, and Qualification:** Update `CMakeLists.txt`, `packaging/noxforge.spec`,
   `packaging/arch/PKGBUILD`, `distribution/release-manifest.json`, deliver
   `tests/test_v15_contracts.py`, and run repository validation and full test matrix.

## Acceptance criteria

- `design/tokens.json` complies with Schema 11, defining `signal` and `interactions`.
- Generated icon SVGs embed valid `<style id="current-color-scheme">` definitions.
- Wi-Fi signal suite (`network-wireless-connected-*`, `acquiring`, `disconnected`, etc.)
  installs cleanly and renders crisp geometric arcs without pseudo-hash fallbacks.
- `LockScreen.qml` and SDDM `Main.qml` include functional error shake animations.
- `busywidget.svg` includes multi-ring orbital geometry.
- `tools/control_center.py` displays live icon preview reflecting dynamic accents.
- `noxforge-doctor` Schema 8 audits all v15 components without regressions.
- All Python tests (`pytest` and `scripts/validate.py`) pass cleanly.
