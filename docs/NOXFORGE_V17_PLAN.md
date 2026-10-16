# NoxForge 17.0.0 — Total Single-Source Authority, Dynamic Accent Ecosystem & Portable Integrity

This plan records the NoxForge version 17 release scope and implementation
sequence, published as `v17.0.0`. It builds upon the 16.0.0 baseline and elevates
NoxForge into a complete, drift-proof, dynamically adaptive desktop system across
KDE Plasma 6.7+, Qt 6.11, SDDM, GTK 3/4, and third-party developer tools.

## Product contract

NoxForge 17 preserves the authentic graphite surfaces, electric-lime precision
accent, Forge Notch (4 px) identity, system typography, KDE package roots,
three-edition architecture, and non-applying installation boundary.

Version 17 expands and hardens the scope across five major pillars:

1. **Tokens Schema 13 & Full Ecosystem Generation:**
   - Upgrades `design/tokens.json` to Schema 13, defining per-accent `surfaceSelected`
     and `surfaceSelectedObsidian` tokens to eliminate green-tint clashes across
     Cyan, Violet, Amber, and custom accents.
   - Migrates remaining manual theme files (Zed, btop, Discord/Vesktop, Firefox
     userChrome, Starship, and Fastfetch) to deterministic single-source generation
     in `scripts/generate_design_system.py`.
2. **100% Single-Source QML Variants Architecture:**
   - Consolidates all 6 QML component pairs into `qml/shared/` (`LockScreen.qml`,
     SDDM `Main.qml`, TabBox `main.qml`, TabBox `Switcher.qml`, `Splash.qml`,
     and `Logout.qml`), generating all 12 theme variants with automated headers
     and zero drift under `design/qml-variants.json` Schema 2.
3. **Dynamic Accent Engine & GTK 3/4 Parity:**
   - Upgrades `src/style/noxforgestyle.cpp` to dynamically tint item selection
     backgrounds, accent-soft highlights, and pressed states from the active accent
     color in real-time.
   - Enhances `noxforge-ctl accent` to non-destructively synchronize user accent
     overrides into GTK 3 and GTK 4 (`~/.config/gtk-3.0/gtk.css` and `gtk-4.0/gtk.css`).
4. **SDDM & Lock Screen UX Refinements:**
   - Password visibility toggle (`Show/Hide Password`) with 5-second automatic hide
     and accessible button semantics.
   - Configurable `allowEmptyPassword` policy (defaulting to `false`) for passwordless
     or hardware-token/PAM sessions.
5. **Portable Packaging Parity, Ecosystem CLI & Control Center v2:**
   - Fixes portable bundle packaging in `scripts/build_store_packages.py` to ensure
     all components expected by `scripts/install.sh` (Zed, browsers, apps, fastfetch,
     `noxforge-ctl`, `control_center.py`) are bundled.
   - Adds 5th tab `Ecosystem & Apps` in `tools/control_center.py` and `noxforge-ctl ecosystem`
     command for user-driven opt-in theme deployment to developer tools.
   - Adds full man page `docs/man/noxforge-ctl.1`.
   - Upgrades `tools/noxforge-doctor` to Schema 10.

## Acceptance criteria

- `design/tokens.json` complies with Schema 13.
- All 12 QML variant files are deterministically generated from `qml/shared/`.
- Portable bundle `./scripts/install.sh --user --dry-run` succeeds when run from within the bundle.
- Qt 6 style dynamically harmonizes selection backgrounds with active accent.
- `noxforge-doctor` Schema 10 audits all v17 components with 0 regressions.
- All Python, CTest, and GUI tests pass cleanly.
