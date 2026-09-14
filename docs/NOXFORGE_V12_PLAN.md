# NoxForge 12.0.0 — Ecosystem & App Parity

This plan is the active implementation authority for the NoxForge version 12
cycle. It builds upon the immutable 11.0.0 release and extends the NoxForge visual
and precision contract across the entire Linux desktop ecosystem.

## Product contract

NoxForge 12 preserves the authentic graphite surfaces, electric-lime precision
accent, Forge Notch (4 px) identity, system typography, KDE package roots,
three-edition architecture, and non-applying installation boundary.

Version 12 expands the scope to achieve complete desktop ecosystem parity:
1. **Tokens Schema 8 & Syntax Authority:** Formally introduces `syntax` color tokens
   and contrast pairs into `design/tokens.json` (schema 8) covering keywords,
   functions, strings, types, numbers, comments, operators, and variables with
   WCAG AA/AAA compliance against both Graphite and Obsidian OLED canvases.
2. **GTK 3 & GTK 4 Theme Parity:** Delivers deterministically generated GTK 3
   and GTK 4 themes (`themes/NoxForge` and `themes/NoxForgeObsidian`) bringing
   authentic graphite/obsidian surfaces, 4 px notch accents, and electric-lime focus
   rings to GTK applications.
3. **KSyntaxHighlighting Integration:** Official `.theme` definitions for Kate,
   KWrite, KDevelop, and Qt Creator (`syntax/kate/NoxForge.theme` and
   `syntax/kate/NoxForgeObsidian.theme`).
4. **VS Code & Cursor Themes:** Complete editor color theme extensions in
   `editors/vscode/` providing matching Dark and Obsidian OLED experiences.
5. **The Big Four Wayland Terminals:** Deterministic configuration generators for
   Ghostty, Alacritty, Kitty, and Foot in both Standard and Obsidian palettes.
6. **Doctor Schema 5:** Diagnostic elevation to inspect GTK themes, Flatpak override
   readiness (`xdg-data/themes:ro`), syntax highlighting, and terminal configs,
   with verified, copy-pasteable non-destructive remediation advice (`--remediation-plan`).
7. **Synchronized Packaging and CI Automation:** Updated CMake, RPM spec, Arch PKGBUILD,
   and automated v12 contract test suite (`tests/test_v12_contracts.py`).

## Sequential phases

1. **Tokens and Authority:** Establish `NOXFORGE_V12_PLAN.md`, update
   `IMPLEMENTATION_PLAN.md`, bump `VERSION` to 12.0.0, and specify syntax tokens
   in `design/tokens.json` under schema 8.
2. **GTK 3 & GTK 4 Themes:** Implement deterministic GTK CSS generation for
   `themes/NoxForge` and `themes/NoxForgeObsidian`.
3. **Editor and Syntax Assets:** Deliver Kate KSyntaxHighlighting themes and
   VS Code/Cursor editor themes.
4. **The Big Four Wayland Terminals:** Implement theme files for Ghostty, Alacritty,
   Kitty, and Foot.
5. **Doctor Schema 5:** Upgrade `tools/noxforge-doctor` to schema 5 with GTK, Flatpak,
   syntax, and terminal diagnostics.
6. **Build and Packaging Integration:** Update `CMakeLists.txt`, `packaging/noxforge.spec`,
   `packaging/arch/PKGBUILD`, `scripts/install.sh`, and `distribution/release-manifest.json`.
7. **Testing and Qualification:** Deliver `tests/test_v12_contracts.py`, update
   `scripts/validate.py` and run the full Python and CTest verification suite.

## Acceptance criteria

- All newly generated GTK 3/4 CSS files parse cleanly without syntax errors and reflect
  NoxForge design tokens.
- Syntax highlighting and terminal themes pass contrast validation (>= 7:1 for keywords/functions/strings,
  >= 4.5:1 for comments/secondary).
- `noxforge-doctor` schema 5 executes in read-only mode and discovers all v12 components.
- The Python test suite (`scripts/run_python_tests.py`) and `scripts/validate.py` pass with zero errors.
- Package specs (RPM spec, Arch PKGBUILD, CMake) stage and install all v12 paths accurately.
