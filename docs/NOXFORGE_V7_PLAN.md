# NoxForge 7.0.0 — Operational Precision

**Repository:** `loofiboss-bit/NoxForge`
**Reviewed baseline:** `v6.0.0` / `d6c4e3c5584b9fdd61c7bb3ae9b3b693f03e67f6`
**Current public release:** `v6.0.0`
**Release version:** `7.0.0`
**Target:** Fedora KDE 44, Plasma/KWin 6.7+, Qt 6.11, Wayland
**Status:** Release-qualified locally; public readback pending
**Release name:** **Operational Precision**

This plan is the canonical implementation and release-gate authority for
NoxForge 7.0.0. It materializes the approved v7 correction, reliability,
accessibility, and visual-polish scope. Repository evidence outranks the
original proposal when they conflict.

## Outcome

NoxForge must work as one coherent KDE Plasma 6 theme in real applications and
under real Wayland scaling. Correctness comes before visual polish:

1. maximized Aurorae decorations scale without black or unpainted areas;
2. important KDE icons resolve and remain visible;
3. Qt, Kirigami, Plasma, SDDM, Logout, and TabBox share one design system;
4. keyboard, focus, mnemonic, contrast, and control-size behavior improve;
5. validation, diagnostics, evidence, and release documentation remain truthful
   and reproducible.

Operational Precision preserves the Kinetic Precision identity, graphite
surfaces, lime precision signal, wallpaper, cursor concept, motion system,
package model, rollback behavior, and non-destructive installation policy.

## Current state

The v7 baseline was established on 2026-08-02 from the public v6.0.0 source
commit. The checkout already contained uncommitted v6 public-readback closure
work; that work is preserved and reconciled rather than discarded.

| Item | Classification | Baseline evidence |
| --- | --- | --- |
| v6.0.0 GitHub release and six assets | completed | Exact public tag and release readback pass. |
| v6.0.0 COPR build 10802161 | completed | COPR reports `succeeded`; Fedora 44 metadata resolves `6.0.0-1.fc44`. |
| Maximized Aurorae titlebar width | failing | A real System Settings report shows the painted titlebar ending early; `decoration-maximized-center` is only 28×28. |
| System Settings core action icons | failing | `draw-highlight`, `view-hidden`, and `tools-report-bug` are absent. |
| Session action semantic icons | partial | Existing coverage is incomplete and must use distinct meanings. |
| Icon-theme fallback | missing | NoxForge currently inherits only `hicolor`. |
| KDE single-click policy | failing | The Qt style unconditionally returns disabled. |
| Mnemonic underline policy | failing | The Qt style unconditionally hides shortcut underlines. |
| Scrollbar pointer target | partial | The native style hardcodes a 10 px extent. |
| Qt/Plasma visual hierarchy | partial | Kinetic Precision is coherent but needs runtime reconciliation and live proof. |
| Live mixed-DPI maximized matrix | missing | Existing v6 offscreen and isolated evidence does not cover the required matrix. |
| Ogg reproducibility across toolchains | uncertain | Fedora 44/FFmpeg 8.1.2 matches committed bytes; a separate toolchain reported drift. |
| Test-count reporting | failing | Current discovery runs 147 tests while v6 documents 141. |
| Host activation or configuration | excluded | No theme, panel, SDDM, or session setting may be changed by this work. |

The detailed machine-readable baseline is
[`evidence/v7/phase0-baseline.json`](evidence/v7/phase0-baseline.json).

## Top priority

Close the two P0 correctness defects first:

1. the maximized Aurorae surface must span the complete window at every required
   scale and output arrangement;
2. core KDE and session icons must resolve through an explicit overlay fallback
   contract and retain valid semantics.

No visual refinement may weaken or bypass those gates.

## Scope and permanent boundaries

- Keep public package IDs and installed paths stable.
- Keep installation, upgrade, rollback, and removal non-applying and reversible.
- Never reset panels or alter Plasma, KWin, SDDM, PAM, or authentication state.
- Use public Qt, KDE, Plasma, Aurorae, and icon-theme contracts.
- Do not patch KDE applications or System Settings upstream source.
- Do not copy artwork or SVG paths from Breeze or another theme.
- Do not use symlinks inside Plasma packages.
- Use repository or safe temporary staging directories.
- Automated and offscreen evidence never substitutes for live composed proof.
- A pending P0 live case means v7 is not release-ready.
- No commit, push, tag, publication, host installation, or theme activation is
  authorized by this plan.

## Required qualification matrix

### Displays and scales

| Matrix | Required values |
| --- | --- |
| Single-output logical scale | 100%, 125%, 140%, 150%, 175%, 200% |
| Mixed-output scale | 100% + 140%, 100% + 200% |
| Output transition | Move a window between differently scaled outputs |
| Panel edge | top, bottom, left, right |
| Direction | LTR and RTL where the surface supports it |
| Motion | normal, reduced/disabled, deliberately slow |

### Window and interaction states

- active and inactive;
- normal and maximized;
- quick-tiled left and right;
- shaded where supported;
- enter and leave full screen;
- hover, pressed, checked, selected, disabled, destructive, and focused;
- keyboard-only focus order, Alt mnemonics, and activation;
- translation expansion, long labels, missing icons, and RTL.

### Applications and shell surfaces

- System Settings, Dolphin, Konsole, Firefox, standard Qt menus and dialogs;
- panel, launcher, task manager, tray, tooltips, popups, calendar,
  notifications, dialogs, and OSD;
- SDDM test mode, Logout, Splash, and TabBox;
- one/many/minimized/long-title/no-icon TabBox cases.

Every live result must be `passed`, `failed`, `blocked`, `pending`, or
`not-applicable`, with the exact environment and evidence path. A generated
gallery is structural evidence only.

## Phase 0 — Authoritative v7 baseline

### Objective

Establish a truthful and executable v7 baseline before visual implementation.

### Work

- Create this plan and make it the active implementation authority.
- Move active version consumers to `7.0.0-dev` without rewriting historical v6
  release evidence.
- Correct README and v6 release closure documentation to reflect the completed
  public GitHub and COPR state.
- Record the known maximized-titlebar and missing-icon failures.
- Record the required display, state, interaction, and application matrix.
- Record current tests and generator results without regenerating assets to hide
  unexplained drift.
- Keep every live v7 result pending or failed until new evidence exists.

### Acceptance

- The active plan and repository version agree.
- v6 release documentation is no longer stale or contradictory.
- Every known issue is classified as completed, partial, missing, blocked,
  failing, or uncertain.
- The worktree remains runnable.
- No Phase 1 visual implementation is included.

### Gate

Run the focused v7 Phase 0 tests, repository validation, complete Python test
discovery, version and generator drift checks, CMake/Ninja/CTest, release-check
preflight, and `git diff --check`. Historical source-bound v6 tests may be
reported as skipped once active source metadata moves to v7; v6 release
lineage must remain independently validated.

**Proposed commit message:**
`docs: establish NoxForge 7 Operational Precision plan`

**Outcome (2026-08-02):** Phase 0 is locally complete. The active repository
version is `7.0.0-dev` across 14 fields in 13 current consumers, while v6
qualification remains historical at `6.0.0`. Public v6 GitHub and COPR closure
is current. The pre-implementation baseline passed validation and all 147 tests
then present. After the authority transition, 106 active tests passed and nine
source-bound v6 modules were explicitly skipped; v6 public lineage remains
covered by active v7 tests. Twenty-one CTest cases, four ASan/UBSan probes, QML
lint, deterministic generators, 56 Plasma assets across four scales,
byte-identical archives, Fedora development SRPM/RPM construction, `rpmlint`
with zero errors/warnings, non-mutating install dry-runs, and `git diff --check`
passed. The maximized-decoration and icon P0 cases remain failed, all v7 live
matrices remain pending, and v7 is not release-ready. Evidence is in
`docs/evidence/v7/phase0-baseline.json` and `phase0-gate.md`.

## Phase 1 — P0 Aurorae and Wayland scaling

### Objective

Correct maximized frame composition before any decorative expansion.

### Work

- Inspect normal, inactive, and special maximized Aurorae element geometry.
- Implement the smallest correct choice:
  - remove the special maximized elements and use normal-frame fallback; or
  - rebuild the maximized center so Aurorae can stretch it correctly.
- Keep source SVG, canonical SVGZ, generator, manifest, and tests synchronized.
- Add static checks for required IDs, bounds, source/compressed parity, and
  transparent or unpainted regions where deterministically testable.
- Exercise the complete display and window-state matrix, including window
  buttons and top-edge pointer targets.

### Acceptance

- No black, transparent, clipped, duplicated, or partially painted titlebar.
- The titlebar spans the complete window at every tested scale and state.
- Minimize, maximize/restore, and close remain aligned and clickable.
- Normal and inactive decoration do not regress.
- Generated Aurorae files are reproducible.
- If a real compositor matrix is unavailable, automated work may pass while the
  P0 live gate remains `pending` and v7 remains not release-ready.

**Proposed commit message:**
`fix(aurorae): make maximized decorations scale across Wayland outputs`

**Outcome (2026-08-02):** Phase 1 is locally complete for automated and
offscreen qualification. NoxForge now relies on Aurorae's documented normal
decoration fallback when maximized instead of publishing undersized special
maximized center elements. The generated SVG and canonical SVGZ are in sync;
the active/inactive nine-slice geometry, opaque stretchable centers, title-edge
configuration, source hashes, and 48 static scale/state cases pass. The full
gate passed 111 active Python tests with nine historical v6 modules skipped,
four sanitizer probes, 21 CTest cases, QML lint, deterministic generators,
byte-identical archives, Fedora development SRPM/RPM construction, `rpmlint`
with zero errors/warnings, non-mutating install dry-runs, and
`git diff --check`. The required real Wayland single- and mixed-output matrix
remains `pending`; therefore the P0 live gate remains open and v7 is not
release-ready. Evidence is in `docs/evidence/v7/aurorae/phase1.json` and
`phase1-gate.md`.

## Phase 2 — P0 icon resolution and semantic coverage

### Objective

Make NoxForge an explicit curated overlay instead of a falsely complete icon
theme.

### Work

- Validate the Fedora 44 installed theme directory names.
- Use the verified fallback chain `breeze-dark,breeze,hicolor` or the exact
  installed-name equivalent.
- Add original, distinct NoxForge icons for:
  - `draw-highlight`;
  - `view-hidden`;
  - `tools-report-bug`;
  - `system-suspend`;
  - `system-reboot`;
  - `system-shutdown`;
  - `system-lock-screen`;
  - `system-log-out`.
- Add symbolic/state variants only when actual KDE requests prove the names.
- Derive a required-icon manifest from NoxForge QML, desktop files, KDE actions,
  and the tested applications.
- Use the real Qt/KDE lookup path when available; report intentional Breeze
  fallback separately from unresolved or unreadable core icons.
- Verify 16, 22, 24, 32, and 48 logical pixel rendering on dark and selected
  surfaces.

### Acceptance

- Every required core name resolves.
- The reported System Settings icons are visible.
- Session actions have distinct semantics.
- No core icon is blank, clipped, dark-on-dark, or an unrelated generic cube.
- Fallback is explicit, tested, and documented.
- Existing valid NoxForge icons do not regress.

**Proposed commit message:**
`fix(icons): add reliable KDE fallback and core semantic coverage`

**Outcome (2026-08-02):** Phase 2 is locally complete for automated and
offscreen qualification. Fedora 44 exposes the exact `breeze-dark`, `breeze`,
and `hicolor` theme directories, and NoxForge now declares that overlay chain.
Eight original, physically distinct core SVGs cover the reported System
Settings misses and the five Logout session actions. A real Qt 6.11 `QIcon`
probe resolved and rendered all eight overlay icons plus an intentional Breeze
`document-print` fallback at 16, 22, 24, 32, and 48 logical pixels in normal
and selected modes: 90 render cases. The full gate passed 116 active Python
tests with nine historical v6 modules skipped, four sanitizer probes, 22 CTest
cases, QML lint, deterministic generators, byte-identical archives, Fedora
development SRPM/RPM construction, `rpmlint` with zero errors/warnings,
non-mutating install dry-runs, and `git diff --check`. Real System Settings and
Plasma visibility remains `pending`; therefore the icon P0 live gate remains
open and v7 is not release-ready. Evidence is in
`docs/evidence/v7/icons/phase2.json` and `phase2-gate.md`.

## Phase 3 — Qt, Kirigami, and application cohesion

### Objective

Respect KDE interaction policy and make real applications share one usable
state language.

### Work

- Delegate single-click activation to the platform/base style or KDE setting.
- Respect platform mnemonic visibility and Alt activation.
- Increase the functional scrollbar hit target while retaining a quiet visual
  track; remove the hardcoded 10 px target.
- Audit focus, hover, pressed, checked, selected, disabled, and destructive
  states.
- Preserve neutral selected rows with a narrow lime marker.
- Use supported palette, QStyle, Plasma, or Kirigami semantics; never patch an
  individual KDE application.
- Test the complete Global Theme in System Settings, Dolphin, Konsole, and
  standard Qt menus/dialogs.
- Ensure unsupported controls fall back safely.

### Acceptance

- KDE click preferences are respected.
- Mnemonics and focus are keyboard-discoverable.
- Scrollbars are restrained and practically usable.
- Selected rows, text, and icons remain readable in all interaction states.
- Real captures show complete activation rather than a mixed theme.

**Proposed commit message:**
`fix(style): respect KDE behavior and unify application interaction states`

**Outcome (2026-08-02):** Phase 3 is locally complete for automated and
offscreen qualification. The native style now reads KDE's explicit
`[KDE] SingleClick` preference and otherwise delegates to QCommonStyle;
shortcut underline and menu-bar Alt navigation policy also delegate to the
base style. The scrollbar exposes a 16 logical pixel functional extent while
painting a centered track no wider than 6 pixels, preserving the quiet visual
language. The Qt probe covers true/false/base click behavior, mnemonic and Alt
delegation, scrollbar extent, quiet rendering, page/thumb hit testing, RTL,
focus, selected states, disabled states, and safe base fallbacks. The full gate
passed 120 active Python tests with nine historical v6 modules skipped, four
sanitizer probes, 22 CTest cases, QML lint, deterministic generators,
byte-identical archives, Fedora development SRPM/RPM construction, `rpmlint`
with zero errors/warnings, non-mutating install dry-runs, and
`git diff --check`. Complete Global Theme activation in real applications and
input-capable keyboard/pointer proof remain `pending`; v7 is not release-ready.
Evidence is in `docs/evidence/v7/style/phase3.json` and `phase3-gate.md`.

## Phase 4 — Plasma shell and panel polish

### Objective

Refine shell density and hierarchy without changing user layout.

### Work

- Audit panel, tray, launcher, tasks, tooltips, popups, calendar,
  notifications, dialogs, and OSD.
- Apply the 4 px rhythm where Plasma metrics permit it.
- Reduce nested borders, normalize radii, padding, separators, and icon
  alignment, and keep lime as a precise state signal.
- Support top, bottom, left, and right panel edges.
- Capture before/after evidence at identical viewport, scale, state, and
  content.

### Acceptance

- Shell surfaces share consistent spacing, borders, radii, and hierarchy.
- Tray icons remain aligned and readable.
- Popups neither clip nor become excessively sparse.
- All four panel edges remain supported.
- No configuration reset or automatic activation is introduced.

**Proposed commit message:**
`style(plasma): refine shell density and visual hierarchy`

**Outcome (2026-08-02):** Phase 4 is locally complete for automated and
offscreen qualification. The shell contract now defines a 4 logical pixel
grid, 4 pixel panel and toolbar margins, 8 pixel popup, dialog, and tooltip
margins, explicit nested-border policy, and 4/6/8 pixel radius roles. All 56
Plasma SVG assets were regenerated from that contract while retaining complete
top, bottom, left, and right frame elements. The v6 and v7 raster atlases use
identical viewports so the changed source hashes remain directly comparable.
The full gate passed 124 active Python tests with nine historical v6 modules
skipped, four sanitizer probes, 22 CTest cases, QML lint, deterministic
generators, byte-identical archives, Fedora development SRPM/RPM construction,
`rpmlint` with zero errors/warnings, non-mutating install dry-runs, and
`git diff --check`. Activated panel-edge, tray, popup, calendar, notification,
dialog, and OSD inspection remains `pending`; v7 is not release-ready. Evidence
is in `docs/evidence/v7/plasma-shell/manifest.json` and `phase4-gate.md`.

## Phase 5 — SDDM, Logout, and TabBox

### Objective

Improve session-surface clarity while preserving authentication and runtime
contracts.

### Work

- Preserve authentication behavior and security boundaries.
- Replace functional Unicode stand-ins such as `↻` with Qt Quick
  `BusyIndicator` or an owned asset.
- Use responsive typography, stable error space, and approximately 40–44
  logical pixel important controls where appropriate.
- Improve large-screen composition without an excessively wide login card.
- Use distinct suspend, restart, shutdown, lock, and logout icons.
- Clarify login, session, layout, accessibility, error, and power hierarchy.
- Qualify TabBox with one/many windows, long titles, minimized windows, real
  application icons, missing icons, keyboard navigation, mixed DPI, translation
  expansion, and RTL.

### Acceptance

- Login and logout controls are readable and appropriately sized.
- Functional UI icons are not represented by Unicode text glyphs.
- Power actions are unmistakable and authentication behavior is unchanged.
- TabBox preserves real application identity with robust fallback.
- Keyboard-only focus order works.

**Proposed commit message:**
`style(session): improve SDDM logout and TabBox clarity`

**Outcome (2026-08-02):** Phase 5 is locally complete for automated and
offscreen qualification. Important session controls now use the 40 logical
pixel token. SDDM replaces the functional Unicode busy glyph with Qt Quick
Controls `BusyIndicator`, exposes Caps Lock in the stable status region, and
retains the existing login, session, keyboard-layout, suspend, reboot, and
power-off calls. Logout keeps five distinct owned action icons. TabBox now has
an explicit executable-icon fallback, list semantics, and Return/Space
activation. All four session surfaces passed isolated QML rendering at
100/125/140/150/200 percent; TabBox additionally passed empty, many-window,
long RTL, keyboard, missing-icon, and minimized cases. The full gate passed 130
active Python tests with nine historical v6 modules skipped, four sanitizer
probes, 46 CTest cases, QML lint, deterministic generators, byte-identical
archives, Fedora development SRPM/RPM construction, `rpmlint` with zero
errors/warnings, non-mutating install dry-runs, and `git diff --check`. Real
SDDM authentication/power actions, held Alt-Tab, keyboard/pointer traversal,
and per-output mixed-DPI migration remain `pending`; v7 is not release-ready.
Evidence is in `docs/evidence/v7/session/phase5.json` and `phase5-gate.md`.

## Phase 6 — Optical icon, cursor, and brand polish

### Objective

Polish only high-use assets supported by real evidence.

### Work

- Rank the 40–50 most requested NoxForge icon names from actual usage.
- Improve semantic distinction and optical clarity at 16, 22, and 24 px.
- Normalize stroke weight, alignment, negative space, optical centering, and
  active accents.
- Do not mass-generate icons or copy Breeze artwork.
- Change cursors only when live scaling proves a defect.
- Preserve logo, palette, wallpaper, and cursor identity.
- Limit brand/wallpaper changes to evidenced crop, preview, scale, or
  presentation corrections.
- Regenerate and compare contact sheets.

### Acceptance

- Frequent icons remain distinguishable without labels.
- Small icons do not collapse into repeated outlines.
- Cursor quality does not regress.
- Kinetic Precision remains recognizably NoxForge.
- No unrelated redesign or asset expansion is introduced.

**Proposed commit message:**
`style(assets): improve core icon clarity and optical consistency`

**Outcome (2026-08-02):** Phase 6 is locally complete for automated and
offscreen qualification. The historical 56-name review set was narrowed to 48
unique priority names backed by the repository's Plasma, System Settings,
Dolphin, and session runtime fixtures. The confirmed byte-identical keyboard
hardware/settings collision was corrected with a distinct settings-control
silhouette. All 48 priority icons are nonempty and raster-distinct at 16, 22,
and 24 pixels, and the regenerated contact sheet was visually reviewed. Cursor
sizes, hotspots, silhouettes, and animation timing remain byte-identical to v6
evidence because no live scaling defect was demonstrated. Logo, palette, and
wallpaper sources likewise remain unchanged. The full gate passed 136 active
Python tests with nine historical v6 modules skipped, four sanitizer probes,
46 CTest cases, QML lint, deterministic generators, byte-identical archives,
Fedora development SRPM/RPM construction, `rpmlint` with zero errors/warnings,
non-mutating install dry-runs, and `git diff --check`. Activated icon and cursor
inspection remains `pending`; v7 is not release-ready. Evidence is in
`docs/evidence/v7/assets/phase6.json`, `priority-icons.png`, and
`phase6-gate.md`.

## Phase 7 — Diagnostics, testing, and reproducibility

### Objective

Make runtime state, failures, and release evidence accurately diagnosable.

### Work

- Extend `noxforge-doctor` with read-only checks for active Qt style, color
  scheme, icon theme and inheritance, unresolved critical icons, Plasma style,
  Aurorae, TabBox, sound theme, safely detectable wallpaper, component
  provenance/version mixing, and actual per-output KScreen/KWin scale.
- Never infer Wayland scale solely from `QT_SCALE_FACTOR`.
- Preserve privacy and read-only behavior.
- Investigate Ogg drift before modifying audio.
- Adopt one documented sound reproducibility contract: pinned release encoder
  byte equality, or canonical PCM/source metrics across toolchains with byte
  equality reserved for the pinned release environment.
- Never blindly regenerate the sound tree with the current host FFmpeg.
- Derive test counts and release-report values from actual gate output.
- Distinguish missing tools from repository regressions in preflight output.
- Add regression tests beside each corrected behavior.

### Acceptance

- Doctor reports the complete active state without writes.
- Mixed versions and unresolved critical icons are detectable.
- Sound validation follows a documented reproducible contract.
- Reports cannot claim stale test totals.
- Environment failures are distinct from source failures.
- Installation, rollback, and provenance tests pass.

**Proposed commit message:**
`test: strengthen diagnostics and reproducible qualification`

**Outcome (2026-08-02):** Phase 7 is locally complete. `noxforge-doctor`
now reports the complete read-only active theme state, component provenance,
mixed versions, unresolved critical icons, safe wallpaper identity, and actual
per-output KScreen/KWin scale without treating `QT_SCALE_FACTOR` as runtime
evidence. Sound validation preserves canonical PCM/source metrics across
toolchains and requires byte equality for the pinned FFmpeg 8.1.2 release
environment; it never blindly overwrites committed Ogg assets. Release
preflight now separates missing environment tools from repository failures and
derives Python totals from the actual runner result. The full phase gate passed
136 active Python tests with nine historical v6 modules skipped, four
sanitizer probes, 46 CTest cases, QML lint, byte-identical source archives,
Fedora development SRPM/RPM construction, `rpmlint` with zero errors/warnings,
non-mutating install dry-runs, and `git diff --check`. Live provenance and
display inspection remain `pending`; v7 is not release-ready. Evidence is in
`docs/evidence/v7/diagnostics/phase7.json` and `phase7-gate.md`.

## Phase 8 — Live qualification and release preparation

### Objective

Prepare a local, exact-source candidate without publication or host mutation.

### Work

- Run every available static, unit, build, package, install-tree, rollback, and
  release check.
- Qualify in a clean Fedora 44 KDE Plasma 6 Wayland environment.
- Test fresh install, v6 upgrade, repeated install, rollback, uninstall,
  configuration preservation, and provenance.
- Capture real composed evidence for maximized System Settings, Dolphin,
  Konsole, panel/tray, popups/calendar/notifications/OSD, SDDM test mode,
  Logout, TabBox, and all required scale/output cases.
- Verify normal, reduced/disabled, and deliberately slow motion.
- Check keyboard-only focus, translation expansion, RTL, and disabled states.
- Prepare English release notes with fixes, limitations, upgrade, and rollback.
- Stage RPM, SRPM, source, checksums, and provenance only through the existing
  safe local workflow.
- Do not publish, tag, push, install on the host, or create a GitHub release.

### Acceptance

- No unresolved P0 or P1 defect.
- No live requirement is represented by automated proof.
- Maximized decorations pass the complete scaling matrix.
- Every required icon resolves.
- Full-theme captures show coherent real applications.
- Static, unit, build, package, install, rollback, and release checks pass in
  supported environments.
- Candidate documentation binds to the exact source commit.
- v7 is release-ready only when every mandatory live gate is complete.

**Proposed commit message:**
`release: prepare the v7 operational precision candidate`

**Outcome (2026-08-02):** Phase 8 is locally complete and the v7 release gate
remains open. The full local gate passes 152 active Python tests with nine
historical v6 modules skipped, four sanitizer probes, 46 CTest cases, QML lint,
deterministic generators, byte-identical source archives, Fedora development
SRPM/RPM construction, `rpmlint` with zero errors/warnings, isolated user and
system install-tree cycles, repeated install, rollback, uninstall,
configuration preservation, staged-root doctor provenance, and
`git diff --check`. English release notes cover corrections, limitations,
upgrade, and rollback. The safe local workflow stages an unsigned development
RPM, SRPM, source archive, checksums, and provenance without host installation,
theme activation, network publication, or remote changes. It deliberately
binds the dirty working-tree source by reproducible archive hash rather than
inventing a clean release commit.

The mandatory composed Wayland/input matrix, both P0 cases, clean Fedora 44 v6
upgrade, and exact clean-commit lineage remain `pending`. Therefore
`releaseReady` is `false`, `VERSION` remains `7.0.0-dev`, and no v7 tag,
publication, host installation, or theme application is authorized. Evidence
is in `docs/evidence/v7/candidate/phase8.json`, `phase8-gate.md`, and the local
ignored `dist/v7-local-candidate/` staging directory.

## Release qualification outcome (2026-08-02)

The stable `7.0.0` candidate closes every mandatory P0/P1 case. An exact-RPM
Fedora 44 KDE container passes all six single scales, both mixed-output pairs,
real application and shell composition, production Splash, SDDM test mode,
Logout, held TabBox, RTL, keyboard/pointer input, and motion variants. A second
disposable Fedora 44 matrix passes public v6 installation, v6-to-v7 upgrade,
repeated install, rollback, uninstall, fresh v7 install, `rpm -V`, doctor, and
configuration preservation. Hardware blur, audible routing, physical cursor
appearance, PAM authentication, and real power actions remain unclaimed but do
not substitute for or reopen the completed mandatory virtual-session cases.

Release evidence is in `docs/evidence/v7/qualification.json`,
`docs/evidence/v7/automated-gate.md`, `docs/evidence/v7/live/`, and
`docs/evidence/v7/upgrade-matrix.json`. Public GitHub/COPR and host-application
claims remain pending until independent readback is committed.

## Standard verification

Run repository-supported equivalents of:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -p 'test_*.py'
cmake -S . -B build/v7 -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build build/v7
ctest --test-dir build/v7 --output-on-failure
python3 scripts/release-check.py
git diff --check
```

Also run every new phase-specific test and generated-file drift check.

## Release gate

NoxForge 7.0.0 is release-ready only when:

- both P0 defects and every P1 defect are closed;
- the complete live scaling and mixed-output matrix passes;
- required icons resolve with documented fallback and valid semantics;
- real application, shell, session, and TabBox captures show the complete theme;
- keyboard, focus order, mnemonics, RTL, translation expansion, contrast, and
  control targets pass;
- static, unit, sanitizer, build, package, install, upgrade, rollback, uninstall,
  reproducibility, and provenance checks pass;
- every artifact and document binds to one exact source commit;
- every unavailable mandatory live case remains `pending` and prevents a
  release-ready claim.

## Risks

| Risk | Handling |
| --- | --- |
| Aurorae engine behavior differs from static SVG interpretation | Require composed KWin evidence; stop after the smallest fix if the live matrix still fails. |
| Icon inheritance names vary by distribution | Validate exact Fedora 44 directory names and real Qt/KDE lookup. |
| Current source evolves beyond v6 evidence | Keep v6 evidence historical and validate v7 source separately. |
| Offscreen captures look correct while real activation is mixed | Require complete active-theme readback and real application captures. |
| Audio encoders produce different Ogg containers | Preserve sources and choose an explicit cross-toolchain contract before changing output. |
| Hardcoded counts become stale | Generate counts from actual gate results. |
| Theme testing mutates the maintainer desktop | Use isolated roots/sessions; never apply on the host. |

If the smallest corrected Aurorae implementation still fails, stop and report:

1. the exact scale, state, and output combination;
2. captured evidence;
3. whether the defect is inside NoxForge assets or the Aurorae engine;
4. a separately scoped KDecoration migration proposal.

## Explicitly excluded

- light, OLED, or additional accent variants;
- GTK or Kvantum themes;
- Plasma 5 or Qt 5 support;
- dynamic wallpaper or another sound set;
- new Plasma widgets or KWin effects;
- a GUI installer;
- panel-layout resets or automatic activation;
- mass-generated icon coverage;
- copied third-party artwork;
- a native C++ KDecoration rewrite unless corrected Aurorae still fails the
  mandatory live matrix.
