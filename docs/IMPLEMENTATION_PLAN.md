# NoxForge KDE — Codex Implementation Plan

<!-- Canonical scope and release-gate authority for the v0.1.0 prototype. -->

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
