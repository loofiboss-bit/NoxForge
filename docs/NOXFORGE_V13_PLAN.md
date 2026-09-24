# NoxForge 13.0.0 — True Obsidian OLED Parity & Dual-Stack Architecture

This plan records the NoxForge version 13 release scope and implementation
sequence, published as `v13.0.0`. It builds upon the immutable 12.0.1 release
and extends the NoxForge visual
and precision contract across the entire Linux desktop ecosystem by elevating the
Obsidian palette into a fully synchronized, first-class twin to standard Graphite.

## Product contract

NoxForge 13 preserves the authentic graphite surfaces, electric-lime precision
accent, Forge Notch (4 px) identity, system typography, KDE package roots,
three-edition architecture, and non-applying installation boundary.

Version 13 expands the scope to achieve complete dual-palette system parity:
1. **Tokens Schema 9 & Dual-Palette Authority:** Introduces full `colorsObsidian`
   palette tokens and verified contrast pairs into `design/tokens.json` under
   Schema 9, guaranteeing WCAG AA/AAA compliance against pitch-black OLED surfaces.
2. **KDE Plasma Style (Obsidian):** Delivers a deterministically generated
   `io.github.loofiboss.noxforge.obsidian.desktop` desktop theme with pitch-black
   `#000000` panel, widget, dialog, and tray backgrounds.
3. **KDE Global Theme (Obsidian):** Delivers a complete Look-and-Feel package
   (`io.github.loofiboss.noxforge.obsidian.desktop`) enabling single-click activation
   of the complete Obsidian experience in KDE System Settings.
4. **Aurorae Window Decoration (Obsidian):** Delivers matching Obsidian window
   decorations (`aurorae/io.github.loofiboss.noxforge.obsidian.desktop`) with solid
   borders, zero padding, and electric-lime active notch markers.
5. **Dynamic Qt 6 C++ Style Runtime Adaptation:** Upgrades `noxforgestyle.so`
   to dynamically detect whether `NoxForgeDark` or `NoxForgeObsidian` is active
   (via `kdeglobals` and `QPalette` luminance), rendering deep OLED surfaces in
   real time without requiring separate style plugins.
6. **Obsidian Wallpapers & SDDM Integration:** Provides `NoxForge-Obsidian` (16:9 up to 4K)
   and `NoxForge-Obsidian-Ultrawide` (21:9 3440x1440) multi-resolution vector-rendered
   wallpapers, plus `sddm/NoxForgeObsidian` and PLM integration.
7. **Developer Tooling (Neovim & Helix):** Provides official syntax highlighting
   themes for Neovim (Lua) and Helix (TOML) in both Standard and Obsidian palettes.
8. **Doctor Schema 6:** Upgrades `noxforge-doctor` to Schema 6 with palette
   desynchronization detection and copy-pasteable non-destructive `--remediation-plan`
   commands to synchronize KDE, GTK, Aurorae, and terminal profiles.
9. **Synchronized Packaging and CI Automation:** Updated CMake, RPM spec, Arch PKGBUILD,
   Store packaging scripts, and automated v13 contract test suite (`tests/test_v13_contracts.py`).

## Sequential phases

1. **Tokens and Authority:** Establish `NOXFORGE_V13_PLAN.md`, update
   `IMPLEMENTATION_PLAN.md`, bump `VERSION` to 13.0.0, and specify `colorsObsidian`
   in `design/tokens.json` under Schema 9.
2. **Obsidian Plasma Style and Global Theme:** Generate `plasma/desktoptheme/io.github.loofiboss.noxforge.obsidian.desktop`
   and construct `look-and-feel/io.github.loofiboss.noxforge.obsidian.desktop`.
3. **Obsidian Aurorae Window Decoration:** Implement and build
   `aurorae/io.github.loofiboss.noxforge.obsidian.desktop`.
4. **Dynamic Qt 6 C++ Style Adaptation:** Upgrade `src/style/noxforgepalette.h`,
   `noxforgestyle.h`, and `noxforgestyle.cpp` to dynamically switch surfaces.
5. **Obsidian Wallpapers and Login Surfaces:** Generate vector SVG sources,
   render PNGs, and stage `wallpapers/NoxForge-Obsidian*` and `sddm/NoxForgeObsidian`.
6. **Developer Tooling:** Implement official Neovim and Helix theme generators
   and output files in `editors/neovim/` and `editors/helix/`.
7. **Doctor Schema 6:** Upgrade `tools/noxforge-doctor` to Schema 6 with
   desynchronization diagnostics and remediation commands.
8. **Build and Packaging Integration:** Update `CMakeLists.txt`, `packaging/noxforge.spec`,
   `packaging/arch/PKGBUILD`, `distribution/release-manifest.json`, and packaging scripts.
9. **Testing and Qualification:** Deliver `tests/test_v13_contracts.py`, update
   `scripts/validate.py`, and run the complete validation and test suite.

## Acceptance criteria

- `design/tokens.json` complies with Schema 9, containing both `colors` and `colorsObsidian`.
- Obsidian Plasma Style and Aurorae SVG assets parse cleanly without errors and conform to design tokens.
- `noxforgestyle.so` dynamically adapts between Graphite and Obsidian surfaces based on active palette.
- Neovim Lua themes and Helix TOML themes pass contrast and syntax tests.
- `noxforge-doctor` Schema 6 executes in read-only mode, checks all v13 components, and detects palette synchronization.
- All Python tests (`scripts/run_python_tests.py`) and repository validations (`scripts/validate.py`) pass with zero errors.
- Package specifications (RPM, PKGBUILD, CMake, Store archives) stage and install all v13 paths accurately.
