# NoxForge v4 Implementation Plan

**Repository:** `loofiboss-bit/NoxForge`  
**Reviewed baseline:** `main` / `v3.0.0` at `7e5d51b5d3204cb20c19a80b665e7b02207cd4a3`  
**Target:** Fedora KDE 44, Plasma 6.7+, Qt 6.11, Wayland  
**Plan status:** In Progress (Active Release Authority)

## Executive Summary

NoxForge v4 is the next evolution of the **Industrial Precision** design system for KDE Plasma 6 and Qt 6. Building on the distribution, packaging, and reliability foundation established in v3.0.0, v4 delivers targeted visual polish, Qt 6 native widget rendering enhancements, refined QML session surfaces (SDDM, Splash, Logout, Window Switcher), machine-readable `noxforge-doctor` diagnostic features (`--json`), and comprehensive test suite updates.

Execution follows a strict phase-gated workflow. Each phase must pass its phase gate before proceeding to subsequent work.

---

## Phases & Scope

### Phase 1: Foundation, Plan Authority & Version Bumping
- Establish `docs/NOXFORGE_V4_PLAN.md` as the canonical active release authority.
- Update `docs/IMPLEMENTATION_PLAN.md` referencing `NOXFORGE_V4_PLAN.md`.
- Bump version in `VERSION` to `4.0.0-dev`.
- Execute version synchronization and baseline validation tests.
- **Phase Gate**: `python3 scripts/sync_version.py --check` and `python3 scripts/validate.py` pass cleanly.

### Phase 2: Native Qt 6 Style Engine Polish (`src/`)
- Enhance native C++ `QStyle` implementation (`src/noxforge_style.cpp`, `src/noxforge_style.h`):
  - Refine `QStyle` primitive and control drawing for tab bars (`CE_TabBarTabShape`, `CE_TabBarTabLabel`) with active 4px Forge Notch accent and `#202C34` hover states.
  - Refine sliders (`CC_Slider`) and scrollbars (`CC_ScrollBar`) with Electric Lime accent focus rings and graphite contrast grooves.
  - Refine table/tree headers (`HeaderView`) with `#2B3942` borders and `#141B21` background tokens.
- Add and update C++ / Python unit tests for Qt style metrics and palette compliance in `tests/`.
- **Phase Gate**: `ctest --test-dir build` and `python3 -m unittest discover -s tests -v` pass cleanly.

### Phase 3: Plasma 6 Style, Session Surfaces & High-DPI Polish (`plasma/`, `look-and-feel/`, `sddm/`, `kwin/`)
- Polish generated Plasma widget SVGs in `plasma/desktoptheme/NoxForge/` using `scripts/generate_plasma_svgs.py`.
- Refine QML session surfaces:
  - `sddm/NoxForge/Main.qml`
  - `look-and-feel/io.github.loofiboss.noxforge.desktop/contents/splash/Splash.qml`
  - `look-and-feel/io.github.loofiboss.noxforge.desktop/contents/logout/Logout.qml`
  - `kwin/tabbox/io.github.loofiboss.noxforge.desktop/contents/ui/main.qml`
- Ensure 2px Electric Lime focus indicators for keyboard navigation and high-DPI crispness.
- **Phase Gate**: `qmllint` on all four QML files and `python3 scripts/generate_plasma_svgs.py --check` pass cleanly.

### Phase 4: Diagnostic Tooling Enhancements (`tools/noxforge-doctor`)
- Extend `tools/noxforge-doctor`:
  - Add `--json` command-line option for machine-readable diagnostic reporting.
  - Add system vs user-local installation mismatch detection and explicit version reporting.
- Update `tests/test_doctor.py` to cover JSON formatting and mismatch detection.
- **Phase Gate**: `python3 -m unittest tests/test_doctor.py` passes cleanly.

### Phase 5: Comprehensive v4 Release Gate & Qualification
- Update evidence manifest in `docs/evidence/v4/`.
- Run full release check: `python3 scripts/release-check.py`.
- Verify packaging RPM contracts and clean uninstallation scripts.
- **Phase Gate**: `python3 scripts/release-check.py` passes with zero errors.

---

## Safety & Governance Rules

1. **Non-applying**: Theme installation does not automatically apply theme, modify user panels, or restart Plasma shell.
2. **Reversibility**: Full dry-run and uninstall options remain available in user and system installers.
3. **No Symlinks**: No symlinks inside Plasma package structures.
4. **Original Artwork**: All artwork remains 100% original NoxForge content.
5. **English Standard**: Code, comments, documentation, filenames, and commit messages must be in English.
