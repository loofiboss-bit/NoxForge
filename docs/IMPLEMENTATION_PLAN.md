# NoxForge KDE — v2.0 Implementation Plan

<!-- Canonical scope and release-gate authority. -->

**Target:** Fedora KDE 44, Plasma 6.7+, Qt 6.11, Wayland
**Theme ID:** `io.github.loofiboss.noxforge.desktop`
**Milestone:** `v2.0.0-local`
**Compatibility:** Plasma 6 and Qt 6 only

## Goal

Deliver an original, complete NoxForge Global Theme for KDE Plasma. Every
theme-owned KDE/Qt visual component must use NoxForge artwork and styling.
Breeze artwork, style plugins, explicit fallbacks and icon inheritance are not
allowed. Third-party application logos remain available through `hicolor`.

`DESIGN.md` is the visual authority. This plan is the implementation and gate
authority.

## Phase 5 — Design system and colors

- Lock Industrial Precision in `DESIGN.md` and schema-v2 design tokens.
- Replace large lime selection fills with a dark selected surface and lime
  focus/active markers.
- Preserve compact geometry, readable contrast and restrained color.

**Gate:** token validation, color-scheme completeness and automated contrast
tests pass. Live visual comparison remains Pending until performed.

## Phase 6 — Global Theme and Plasma Shell

- Add a strict Plasma 6 Look-and-Feel package with defaults and previews.
- Add original splash, logout, optional panel layout and KWin task switcher.
- Cover core Plasma Style widgets and shell icons without an explicit fallback.

**Gate:** KPackage structure validates, NoxForge is listed as a Global Theme,
all required SVG state IDs exist and no package contains symlinks.

## Phase 7 — Native Qt application style

- Add a Qt 6 `QStylePlugin` named `NoxForge`, implemented from `QCommonStyle`.
- Cover standard primitives, controls, complex controls, metrics, palettes,
  focus, disabled states, RTL and high DPI.
- Add an offscreen widget gallery and plugin discovery tests.

**Gate:** CMake, build, CTest and offscreen render pass; the plugin reports
`NoxForge` without linking to a Breeze or Kvantum style library.

## Phase 8 — Icons, cursors and sounds

- Expand original icon families across KDE semantic categories.
- Inherit only `hicolor` for third-party application logos.
- Add an original multi-size Xcursor theme with physical aliases, no symlinks.
- Add an original, normalized system sound theme.

**Gate:** coverage manifests, XML/audio/cursor validation and pixel-size preview
checks pass. Live cursor and sound checks remain Pending until performed.

## Phase 9 — SDDM, installation and final integration

- Add a standalone Qt 6 SDDM theme.
- Keep data components user-local; install the Qt style and SDDM only through
  an explicit separate system installer.
- Never apply the theme, reset the panel, restart Plasma or change SDDM config.
- Produce deterministic local archives and checksums.

**Gate:** validation, Python tests, CMake/CTest, deterministic build, isolated
repeated user install/uninstall and system dry-runs pass. Set all metadata to
`2.0.0` only at this final gate.

## Required verification

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests
cmake -S . -B build/cmake -G Ninja
cmake --build build/cmake
ctest --test-dir build/cmake --output-on-failure
python3 scripts/build.py
./scripts/install.sh --user --dry-run
./scripts/uninstall.sh --user --dry-run
./scripts/install-system.sh --system --dry-run
./scripts/uninstall-system.sh --system --dry-run
```

## Manual release gate

The following remain Pending until run in a real Fedora KDE 44 Wayland session:

- Plasma and Qt application checks at 100% and 140% scaling;
- blur enabled and disabled, light and dark wallpapers;
- keyboard focus, RTL, multi-monitor and every panel edge;
- splash, logout, Alt+Tab, lock screen, cursors, sounds and interactive SDDM flows;
- direct confirmation that core workflows load no fallback theme artwork.

No commit, push, tag, publication, RPM, COPR or KDE Store work is authorized.
