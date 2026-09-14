# NoxForge 11.0.0 — Deep Focus & System Completeness

This plan is the active implementation authority for the NoxForge version 11
cycle. It follows the immutable 10.0.0 and 10.1.0 releases and must not
relabel or rewrite historical release evidence.

## Product contract

NoxForge 11 retains the authentic graphite surfaces, electric-lime precision
accent, Forge Notch (4 px) identity, system typography, KDE package roots,
three-edition architecture, and non-applying installation boundary.

Version 11 expands the scope to achieve full system completeness:
1. **Qt 6 C++ Style Completeness:** Complete primitive coverage for complex
   desktop applications (Dolphin, Kate, KDevelop, Qt Creator), adding
   `PE_IndicatorBranch` (tree view chevrons), `PE_FrameTabWidget` (clean tab
   panes), `PE_IndicatorSplitter` (tactile divider bars), `PE_FrameDockWidget`
   (dock frames), and `PE_PanelStatusBar` / `PE_FrameStatusBarItem` (status bars).
2. **Developer & Terminal Integration:** Official Konsole color schemes
   (`konsole/NoxForge.colorscheme` and `konsole/NoxForgeObsidian.colorscheme`)
   matching the Forge tokens for unified desktop-to-CLI cohesion.
3. **NoxForge Obsidian Variant:** An official OLED/True-Black companion color
   scheme (`color-schemes/NoxForgeObsidian.colors`) providing `#000000` canvas
   depth while strictly preserving graphite hierarchy, electric-lime focus,
   and WCAG contrast limits.
4. **Doctor Schema 4:** Diagnostic elevation to inspect terminal schemes,
   Wayland fractional scaling factors, and non-destructive remediation advice
   (`--remediation-plan`).
5. **Packaging and CI Automation:** Synchronized CMake, RPM spec, Arch PKGBUILD,
   and automated contract tests.

## Sequential phases

1. **Tokens and Authority:** Establish `NOXFORGE_V11_PLAN.md`, update
   `IMPLEMENTATION_PLAN.md`, and define terminal ANSI tokens and Obsidian
   palette definitions in `design/tokens.json`.
2. **Native Qt 6 Style Completeness:** Implement `PE_IndicatorBranch`,
   `PE_FrameTabWidget`, `PE_IndicatorSplitter`, `PE_FrameDockWidget`, and
   `PE_FrameStatusBar` in `src/style/noxforgestyle.cpp`.
3. **Terminal and Color Scheme Assets:** Deliver `konsole/NoxForge.colorscheme`,
   `konsole/NoxForgeObsidian.colorscheme`, and `color-schemes/NoxForgeObsidian.colors`.
4. **Doctor Schema 4:** Upgrade `tools/noxforge-doctor` to schema 4 with Konsole
   color scheme discovery, Obsidian support, and `--remediation-plan`.
5. **Build and Packaging Integration:** Update `CMakeLists.txt`, `noxforge.spec`,
   and `packaging/arch/PKGBUILD` to stage and install the new assets.
6. **Testing and Qualification:** Deliver `tests/test_v11_contracts.py` and run the
   comprehensive Python test suite and validation scripts.

## Acceptance criteria

- All newly implemented Qt 6 primitives render cleanly without falling back to
  raw beveled `QCommonStyle` defaults.
- Konsole color schemes and `NoxForgeObsidian.colors` pass contrast validation
  (>= 7:1 for primary text, >= 4.5:1 for ANSI/secondary text).
- `noxforge-doctor` schema 4 executes in read-only mode and discovers all
  v11 components.
- The Python test suite and `scripts/validate.py` pass with zero errors.
- Package specs accurately reflect all installed v11 paths.
