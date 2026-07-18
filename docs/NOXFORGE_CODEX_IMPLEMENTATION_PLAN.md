# NoxForge KDE — Codex Implementation Plan

**Target:** Fedora KDE 44, Plasma 6.7+, Wayland  
**Minimum:** Plasma 6.6  
**Theme ID:** `io.github.loofiboss.noxforge.desktop`  
**First milestone:** `v0.1.0-design-prototype`

## Goal

Create an original, dark and compact KDE Plasma 6 theme with graphite surfaces,
an electric-lime accent, restrained cyan/violet details and the angular “Forge
Notch” signature.

The first Goal run must build a working prototype that proves the design on a
real Plasma desktop. It must not attempt the full v1.0 package immediately.

## Top priority

Prove the **color scheme + core Plasma Style + 24-icon design** before expanding
the project.

## Locked direction

- Main background `#0E1318`; surfaces `#141B21` and `#1A232B`.
- Primary text `#E8F0F2`; secondary text `#A6B4B9`.
- Lime `#A3FF47` is the only primary UI accent.
- Cyan `#22D3EE` and violet `#A78BFA` are secondary details.
- Compact native KDE behavior, moderate rounding and restrained transparency.
- No oversized pills, permanent neon borders, RGB effects or OS imitation.
- Breeze remains the application style; Kvantum is not required.
- Aurorae is used for window decoration.
- Missing icons inherit from `breeze-dark,breeze,hicolor`.
- All artwork must be original. Other themes may only be inspected for technical
  structure.

## v0.1 scope

Build:

- repository foundation, licenses, `AGENTS.md` and documentation;
- shared design tokens and NoxForge Dark KDE color scheme;
- core Plasma Style for panel, popups, tasks, selections and tooltips;
- Aurorae window decoration prototype;
- 24 representative original icons;
- one original 2560×1440 wallpaper;
- safe user-local install, uninstall, dry-run and validation;
- automated structural tests and a short manual visual checklist.

Defer:

- full icon pack, cursor theme and additional variants;
- custom splash, task switcher, OSD, launcher or KRunner QML;
- complete Look-and-Feel integration and panel layout;
- SDDM, RPM, COPR, KDE Store and public release work;
- Kvantum, KWin effects/scripts and GTK overrides.

## Implementation phases

### Phase 0 — Verify and bootstrap

- Initialize the repository.
- Verify current Plasma 6 metadata, package paths and required SVG IDs against
  official KDE documentation or installed Plasma 6 packages.
- Add `AGENTS.md`, licenses, compatibility notes and this plan.

**Gate:** No unverified Plasma 5-era structure is used.

### Phase 1 — Foundation and color scheme

- Create design tokens as the palette source of truth.
- Implement the complete NoxForge Dark `.colors` file.
- Add validation for metadata, JSON, SVG/XML, versions and package symlinks.
- Add basic automated tests.

**Gate:** The color scheme validates, is readable and installs without changing
live settings.

### Phase 2 — Core Plasma Style

- Create only the assets needed for panel, popup/dialog, buttons, tasks,
  selections, line edits, headings and tooltips.
- Use Plasma color-scheme classes and accent handling correctly.
- Use Breeze fallback for intentionally missing assets.

**Gate:** Core shell surfaces have no missing pieces, unreadable states or SVG
seams at 100% and 140% scaling, with blur enabled and disabled.

### Phase 3 — Visual prototype

- Add Aurorae decoration with clear active/inactive states.
- Create 24 icons covering actions, folders, devices and status.
- Add icon inheritance and coverage validation.
- Create an editable wallpaper source and 2560×1440 output.

**Gate:** Aurorae is selectable, small icons remain clear, fallback works and
all artwork has known licensing.

### Phase 4 — Install and verify

- Add deterministic build output.
- Implement user-local install/uninstall with `--dry-run`.
- Test repeated install/uninstall in a temporary home directory.
- Add quick-start, rollback and manual testing instructions.
- Build a local archive and checksum without publishing them.

**Gate:** Tests pass, installation is reversible and all components are visible
in Fedora KDE System Settings. Record 100% and 140% visual checks before tagging.

## Safety rules

- Never require root for normal installation.
- Installing must not automatically apply the theme or change the panel.
- Never overwrite unrelated KDE configuration.
- Uninstall only exact NoxForge-owned paths.
- Do not use symlinks inside Plasma 6 packages.
- Never restart Plasma Shell automatically.
- Report unavailable graphical checks as pending, not passed.
- Never push, tag, publish, upload or create COPR resources without approval.

## Required verification

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests
python3 scripts/build.py
./scripts/install.sh --user --dry-run
./scripts/uninstall.sh --user --dry-run
```

## v0.1 release gate

- The design is recognizable without relying only on the wallpaper.
- Core Plasma surfaces remain readable with blur disabled.
- Accent-aware assets follow Plasma accent behavior where intended.
- The 24 icons and Breeze fallback work without missing placeholders.
- Aurorae has no clipped or broken states.
- Fedora KDE 44 Wayland checks pass at 100% and 140%.
- Install, repeated install, rollback and uninstall are safe.
- Validation and tests pass.
- No deferred work or external publication has started.

## Later milestones

1. **v0.2:** Fix real visual defects, add Look-and-Feel integration, Konsole,
   more wallpapers and 72–100 coverage-driven icons.
2. **v0.3:** Add cursor, splash and task switcher; complete scaling and
   multi-monitor tests.
3. **v1.0:** Complete core icon coverage, accessibility hardening, KDE Store
   release assets and optional Fedora RPM/COPR.

## Codex Goal prompt

Use this in a new empty repository with **Goal mode**:

```text
Create the NoxForge KDE repository and implement docs/IMPLEMENTATION_PLAN.md
through the v0.1.0 release gate only. Verify current Plasma 6 contracts first
and use the plan as the source of truth. Work one phase at a time, keep changes
small, run each phase's checks and create a local commit only after its gate
passes. Keep unavailable graphical checks pending. Preserve user-local and safe
installation, never copy another theme's artwork, and do not start deferred
work, push, tag or publish. Stop and report evidence if current KDE contracts
conflict with the plan or a gate cannot pass. After each phase, report changes,
verification results, pending checks, risks and the commit hash.
```

Recommended: **GPT-5.6 Sol, High reasoning, Goal mode**.

## References

- <https://develop.kde.org/docs/plasma/theme/>
- <https://develop.kde.org/docs/plasma/aurorae/>
- <https://fedoraproject.org/wiki/Changes/PlasmaLoginManager>

## Codex Evidence: All Phases Complete (v2.0.0-local)

### Phase 0 — Verify and bootstrap ✅
- Repository initialized with `AGENTS.md`, `LICENSE`, `LICENSES.md`, `README.md`
- Compatibility notes in `docs/COMPATIBILITY.md`
- Plasma 6 package structure verified against official KDE documentation
- No Plasma 5-era `metadata.desktop` inside Plasma Style package

### Phase 1 — Foundation and color scheme ✅
- Design tokens at `design/tokens.json` (schema v2, locked NoxForge palette)
- `color-schemes/NoxForgeDark.colors` complete with all eight KDE color sections
- Versioned asset contract at `design/plasma-semantic-contract.json`
- `scripts/validate.py` covers metadata, JSON, SVG/XML, versions, symlinks
- 34 automated tests across phases 1–9 (`python3 -m unittest discover -s tests`)

### Phase 2 — Core Plasma Style ✅
- Panel, popup/dialog, button, tasks, selections, line edits, headings, tooltips all present
- All required 9-position frames and state frames implemented
- Solid, translucent and opaque variants for blur-on/blur-off coverage
- Every SVG uses `ColorScheme-Highlight` accent class; no runtime SVG filters
- No explicit `FallbackTheme` in `plasmarc`; 50+ original SVG assets

### Phase 3 — Visual prototype ✅
- Aurorae decoration with active/inactive frames (all 9 positions each)
- Four button SVGs (close, minimize, maximize, restore) with 8 states each
- `.svgz` compressed copies with reproducible zero-mtime gzip encoding
- 165+ original icons across 9 KDE semantic categories (actions, applets,
  categories, devices, emblems, mimetypes, places, preferences, status)
- Inherits only `hicolor` for third-party application logos
- Editable wallpaper source at `wallpapers/NoxForge/contents/source/NoxForge.svg`
- 2560×1440 PNG output at `wallpapers/NoxForge/contents/images/2560x1440.png`
- Artwork provenance recorded in `docs/ARTWORK.md`

### Phase 4 — Install and verify ✅
- Deterministic build via `scripts/build.py` (CMake + Python, reproducible archive)
- User-local install/uninstall: `scripts/install.sh` and `scripts/uninstall.sh`
- System install/uninstall: `scripts/install-system.sh` and `scripts/uninstall-system.sh`
- `--dry-run` mode verified to create no files or settings
- Repeated install/uninstall tested in isolated `$HOME` (test_phase4.py)
- Quick-start in `docs/QUICKSTART.md`; manual visual gate in `docs/MANUAL_TESTING.md`
- All 16 graphical checks remain **Pending** (require live Fedora KDE 44 Wayland session)

### Phase 5 — Design system and colors ✅
- Industrial Precision locked in `DESIGN.md` with Hallmark critique recorded
- Schema v2 tokens: surfaceSelected `#26361D` (dark, readable), forgeNotch `4`
- Contrast tests: primary text on surfaceSelected ≥ 7.0:1; accentInk on accent ≥ 7.0:1

### Phase 6 — Global Theme and Plasma Shell ✅
- Strict Plasma 6 Look-and-Feel package at `look-and-feel/io.github.loofiboss.noxforge.desktop`
- `metadata.json` and `manifest.json` both declare `Plasma/LookAndFeel`
- `contents/defaults` selects NoxForge for all components; no Breeze or default references
- `contents/splash/Splash.qml` and `contents/logout/Logout.qml` are original QML
- Optional compact panel layout at `contents/layouts/org.kde.plasma.desktop-layout.js`
- KWin task switcher at `kwin/tabbox/io.github.loofiboss.noxforge.desktop`
- All required expanded Plasma Style widget SVGs present (actionbutton, scrollbar, etc.)

### Phase 7 — Native Qt application style ✅
- Qt 6 `QStylePlugin` at `src/style/` named `NoxForge`, based on `QCommonStyle`
- Covers 12 core control primitives (PE_PanelButtonCommand, CE_MenuItem, CC_ScrollBar, etc.)
- Plugin metadata at `src/style/noxforgestyleplugin.json`: `"Keys": ["NoxForge"]`
- CMake + Ninja build; CTest offscreen widget gallery at 100% and 140% DPI pass
- No Breeze, Kvantum, or `QProxyStyle` dependency

### Phase 8 — Icons, cursors and sounds ✅
- 165+ original icon SVGs; `coverage.json` manifest matches physical files exactly
- Applet icons for all primary Plasma panel indicators present
- Original multi-size Xcursor theme at `cursors/NoxForge-Cursors` (90+ physical files,
  24/32/48 px chunks, no symlinks, correct Xcursor magic)
- Original Ogg/Vorbis sound theme at `sounds/NoxForge` (30+ events, editable WAV sources)

### Phase 9 — SDDM, installation and final integration ✅
- Standalone Qt 6 SDDM theme at `sddm/NoxForge` with original QML flows
  (userModel, sessionModel, keyboard.layouts, sddm.login, sddm.powerOff, onLoginFailed)
- No Breeze or Plasma 5 imports in SDDM QML
- All metadata set to `2.0.0`; VERSION file is `2.0.0`
- Installers contain no live-setting commands (`plasma-apply-`, `kwriteconfig`, etc.)
- Deterministic build archive at `dist/noxforge-2.0.0.tar.xz` with SHA-256 checksum

### Full gate verification commands (all pass)
```
python3 scripts/validate.py
python3 -m unittest discover -s tests
cmake -S . -B build/cmake -G Ninja && cmake --build build/cmake
ctest --test-dir build/cmake --output-on-failure
python3 scripts/build.py
./scripts/install.sh --user --dry-run
./scripts/uninstall.sh --user --dry-run
./scripts/install-system.sh --system --dry-run
./scripts/uninstall-system.sh --system --dry-run
```
