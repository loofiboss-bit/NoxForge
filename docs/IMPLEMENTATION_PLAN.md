# NoxForge KDE — v2.0.0 Visual Rebuild Plan

<!-- Canonical scope and release-gate authority. -->

**Target:** Fedora KDE 44, Plasma 6.7+, Qt 6.11, Wayland
**Theme ID:** `io.github.loofiboss.noxforge.desktop`
**Milestone:** `v2.0.0`
**Compatibility:** Plasma 6 and Qt 6 only

## Goal

Rebuild the v2.0.0 candidate into a visually coherent, complete NoxForge Global
Theme. Preserve the Industrial Precision identity and package IDs while
replacing placeholder coverage, semantically incorrect graphics and weak visual
evidence with release-quality implementation and verification.

`DESIGN.md` is the visual authority. This plan is the implementation and gate
authority. Structural validation never substitutes for live visual evidence.

## Phase 1 — Authority and baseline

- Record the v2 visual audit and invalidate stale release evidence.
- Make the canonical plan, README and design authority agree on current status.
- Preserve the existing clean v1.0.0 tag and rebuild v2.0.0 in place.

**Gate:** repository validation, Python tests and CTest establish a reproducible
baseline; known visual and QML issues are recorded rather than hidden.

## Phase 2 — Design tokens and generated consumers

- Upgrade the token schema and lock component, state, typography and icon rules.
- Generate the C++ palette, KDE colors, Plasma color definitions and physical
  QML token copies from `design/tokens.json`.
- Separate Plasma semantic contracts from original glyph geometry.

**Gate:** generated consumers match the token source byte-for-byte and contrast,
identity, version and no-symlink checks pass.

## Phase 3 — Complete Plasma Style

- Cover all Plasma 6.7 widget families and weather artwork used by core flows.
- Add edge-specific states, complete hints and opaque/solid/translucent variants.
- Apply the restrained selection, focus and Forge Notch hierarchy.

**Gate:** the semantic contract, SVG/XML validation and raster matrix at 100,
125, 140 and 200 percent pass. Live fallback checks remain Pending.

## Phase 4 — Native Qt application style

- Centralize state and geometry handling in the QCommonStyle implementation.
- Cover control sub-rects, LTR/RTL, focus, selection and scrollbar geometry.
- Expand the widget gallery to exercise dense native application workflows.

**Gate:** CMake, build and CTest pass for LTR/RTL at 100, 125, 140 and 200
percent; every capture is non-empty, correctly sized and distinct.

## Phase 5 — Identity artwork

- Replace incorrect icon and cursor aliases with semantic glyphs.
- Add optical small-icon variants and animated wait/progress cursors.
- Refine Aurorae, the canonical N/F mark and responsive wallpaper outputs.

**Gate:** alias allowlists, source/binary parity, render contact sheets, artwork
provenance and multi-size validations pass. Live cursor checks remain Pending.

## Phase 6 — Shell and login experiences

- Use generated tokens and brand artwork in splash, logout, Alt+Tab and SDDM.
- Complete keyboard, focus, RTL, error, empty and destructive-action states.
- Replace placeholder previews with reproducible renders or Pending live captures.

**Gate:** QML lint, offscreen smoke tests and SDDM test mode pass. Interactive
KWin, Plasma and SDDM checks remain Pending until run in their real sessions.

## Phase 7 — Integration and local release gate

- Run repeated isolated user and system install/uninstall checks without applying
  the theme or changing live settings.
- Run the full Fedora KDE 44 Wayland manual matrix and capture honest evidence.
- Build the local archive twice and require identical checksums.

**Gate:** all automated checks pass, every available live check has evidence,
unavailable graphical checks remain Pending and local release notes are current.

## Required verification

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests
cmake -S . -B build/cmake -G Ninja
cmake --build build/cmake
ctest --test-dir build/cmake --output-on-failure
/usr/lib64/qt6/bin/qmllint <changed-qml-files>
python3 scripts/build.py
./scripts/install.sh --user --dry-run
./scripts/uninstall.sh --user --dry-run
./scripts/install-system.sh --system --dry-run
./scripts/uninstall-system.sh --system --dry-run
```

## Manual release gate

The following remain Pending until run in a real Fedora KDE 44 Wayland session:

- Plasma and Qt application checks at 100 and 140 percent scaling;
- blur enabled and disabled, light and dark wallpapers;
- keyboard focus, RTL, multi-monitor and every panel edge;
- splash, logout, Alt+Tab, lock screen, cursors, sounds and interactive SDDM;
- direct confirmation that core workflows load no fallback theme artwork.

GitHub publication of v2.0.0 was explicitly authorized on 2026-07-18 after the
local release gate. RPM, COPR, KDE Store and automatic theme application remain
outside this plan.
