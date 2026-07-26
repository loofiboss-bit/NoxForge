# NoxForge v5 Implementation Plan

<!-- Hallmark · pre-emit critique: P5 H5 E5 S5 R5 V4 -->

**Repository:** `loofiboss-bit/NoxForge`  
**Reviewed baseline:** `main` / `v4.0.0` at `e3faefd481026cffafb9b48e11aa79987781fa78`  
**Target:** Fedora KDE 44, Plasma/KWin 6.7+, Qt 6.11, Wayland  
**Plan status:** Phase 7 release candidate qualified; publication pending

## Product direction

NoxForge v5 is a single dark-theme evolution of Industrial Precision for broad
daily KDE use. The graphite/lime palette, Forge Notch, N/F mark, public package
identifiers and non-applying installation contract remain stable. Visual
quality must be demonstrated across Qt, Plasma, session surfaces, icons,
cursors, wallpaper and sound rather than inferred from file counts.

Implementation proceeds one phase at a time. A phase gate must pass before a
local commit, and a later phase requires a new explicit user request. Pushes,
tags, publication, COPR operations, installation and desktop-setting changes
remain separately gated.

## Phase 0 — Authority and truthful baseline

- Close v4 as a tagged source release with no attached public assets, v4 COPR
  claim or fresh v4 live qualification.
- Make this file the active authority and move the repository to `5.0.0-dev`.
- Reconcile README, release records, COPR guidance, RPM history and version
  consumers.
- Give development versions explicit SemVer, CMake and RPM mappings.
- Generalize the exact-tag release workflow to select notes and evidence from
  the requested version, require six verified assets and reject stale metadata.
- Introduce a versioned v5 qualification manifest without relabeling v3 results.

**Gate:** version synchronization, source validation, release-workflow contract
tests, the Python suite, CMake/CTest, QML lint, deterministic archives, RPM
build/rpmlint and `git diff --check` all pass.

**Outcome (2026-07-26):** The automated Phase 0 gate passed. The v5 live
qualification matrix remains explicitly blocked because Phase 6 has not been
authorized or run; no offscreen result is promoted to live evidence.

## Phase 1 — Design system schema v4

- Preserve the locked anchor palette and 4 px grid.
- Tokenize semantic roles, opacity, elevation, overlay, shadow and reduced
  motion for every generated consumer.
- Define one complete hierarchy for default, hover, focus, pressed, checked,
  selected, disabled, busy, error and success.
- Require Hallmark scores of at least 4/5 on philosophy, hierarchy, execution,
  specificity, restraint and variety.

**Gate:** zero generator drift, full token parity and contrast coverage for all
documented foreground/background pairs.

**Outcome (2026-07-26):** Schema v4 preserves the locked palette and four-pixel
grid while adding semantic roles, opacity, elevation, overlay, shadow,
reduced-motion and the complete ten-state hierarchy. Generated C++ and QML
consumers have exact canonical token parity, every semantic foreground and
background pair is covered by a passing contrast contract, and all six
Hallmark scores are at least 4/5. The focused Phase 1 gate and the broader local
release check without archive/RPM packaging passed.

## Phase 2 — Complete native Qt 6 style

- Complete common control rendering and state coverage while preserving safe
  `QCommonStyle` fallbacks.
- Correct labels, sort/close indicators, tri-state and busy states, hit testing,
  subcontrol geometry, RTL and high-DPI rendering.
- Defer animation policy to Qt/system reduced-motion settings.
- Expand the authentic widget gallery to control, data, menu, state and stress
  surfaces.

**Gate:** CTest, geometry/state probes and approved LTR/RTL 100/125/140/200
percent reference renders pass.

**Outcome (2026-07-26):** The native Qt style now covers common labels,
header sort and tab-close indicators, tri-state checks, static busy progress,
mirrored subcontrol geometry and hit testing while retaining `QCommonStyle`
fallbacks. Animation policy falls through to Qt/system settings. The authentic
gallery covers control, data, menu, state and stress surfaces; all 12 reviewed
LTR/RTL scale and page renders have unique image data. The focused CTest,
geometry/state probe, visual-evidence tests and broader local validation passed.

## Phase 3 — Plasma Style and shell surfaces

- Refine all 43 Plasma 6.7 widget families from semantic recipes.
- Qualify opaque, solid and translucent backgrounds, all panel edges and task
  states, popups, tooltips, calendar, notifications and scrollable surfaces.
- Prevent dark seams, stacked focus indicators and visible fallback artwork.

**Gate:** deterministic generation and a complete state/orientation/scale raster
atlas pass.

**Outcome (2026-07-26):** All 43 Plasma 6.7 widget families now resolve through
the versioned semantic recipe contract. Opaque, solid and translucent shell
variants use consistent nine-slice paints; focused controls retain one
indicator, and task focus/progress markers follow all four panel edges. The
committed deterministic atlas covers 56 widget, weather, dialog and background
assets at 100/125/140/200 percent, including every declared state sheet and
oriented task state. Generator drift, focused Phase 3 tests, the Python suite,
CMake/CTest, QML lint and the broader local release check without archive/RPM
packaging passed. Live Plasma fallback and compositor qualification remain
blocked for Phase 6.

## Phase 4 — Original artwork system

- Optically refine the N/F mark and author separate deterministic 16:9 and
  ultrawide v5 wallpaper compositions.
- Expand icons from a fixed KDE/Plasma/System Settings runtime fixture and add
  optical variants only where required.
- Validate cursor hotspots, physical sizes and animation timing, and normalize
  sound loudness without losing semantic distinction.

**Gate:** byte-identical outputs, semantic duplicate checks and reviewed contact
sheets pass. No copied artwork or package symlinks are allowed.

**Outcome (2026-07-26):** The N/F mark was optically balanced while preserving
its physical cross-surface identity. Independent 16:9 and ultrawide vector
compositions now produce byte-identical wallpaper outputs. A versioned Fedora
KDE 44, Plasma 6.7 and System Settings 6.7 runtime fixture expands coverage to
185 scalable icons with 196 explicitly scoped 16/22 px optical variants.
Cursor manifests bind every canonical hotspot, all 24/32/48 px images and both
12-frame 80 ms animations. Original sound masters are RMS-normalized with a
measured peak ceiling while retaining distinct duration and pitch signatures.
All generators, semantic duplicate checks, three reviewed contact sheets, the
focused Phase 4 suite and the broader local release check without archive/RPM
packaging passed. No package symlink or copied artwork was introduced.

## Phase 5 — Session and window surfaces

- Refine SDDM, Splash, Logout, KWin TabBox and Aurorae without changing their
  supported login/session/language/power contracts.
- Cover long and empty text, localization, keyboard-only use, RTL, reduced
  motion and stable error/status regions.
- Qualify 1280x720, 1920x1080, 2560x1440 and 3440x1440 compositions.

**Gate:** available QML lint, authentic QML renders and structural Aurorae state
validation pass. No private lock-screen implementation is introduced.

**Outcome (2026-07-26):** SDDM, Splash, Logout and KWin TabBox retain their
public login, session, language, power and cancellation contracts while adding
bounded long/empty text, explicit keyboard traversal, mirrored RTL layouts,
system-duration reduced motion and a stable two-line login status region.
Aurorae preserves its active/inactive frame and eight button states with
canonical compressed assets. Sixteen reviewed authentic QML renders cover all
four surfaces at 1280x720, 1920x1080, 2560x1440 and 3440x1440 across long RTL,
keyboard focus, standard and empty reduced-motion scenarios. QML lint, focused
Phase 5 tests, deterministic evidence regeneration, CMake/CTest and the broader
local release check without archive/RPM packaging passed. No private lock
screen was introduced. These offscreen renders are structural evidence, not
live session qualification; the live matrix remains blocked until Phase 6 is
explicitly authorized and run.

## Phase 6 — Accessibility, performance and live qualification

- Run the full release gate plus sanitizers, contrast/font checks,
  keyboard-only, RTL, scale, reduced-motion and color-vision reviews.
- Hold gallery startup, control rendering and QML first-frame medians within
  ten percent of the Phase 0 baseline unless a regression is justified.
- Run the isolated Wayland matrix for panel preservation, edges, multi-output,
  blur, Aurorae, Alt+Tab, cursors and SDDM test mode.

**Gate:** no failed case; every unavailable case remains `blocked` with a
specific blocker. Offscreen evidence never substitutes for live evidence.

**Outcome (2026-07-26):** The complete source/archive/RPM gate and the separate
AddressSanitizer/UndefinedBehaviorSanitizer CTest build passed. Source-bound
accessibility evidence covers all contrast pairs, the KDE system-font policy,
keyboard and RTL structure, scale compositions, reduced motion and non-color
state indicators. Eleven-sample medians stayed within the ten-percent Phase 0
budget: gallery startup 0.8761x, control rendering 0.9996x and QML first frame
1.0064x. Isolated KWin/Plasma Wayland runs passed theme application, exact
panel preservation, all four panel edges, two virtual outputs, shell artwork,
required icon clarity and real Qt composition at 100/140 percent. Hardware
blur, injected keyboard and pointer transitions, live RTL, a held visible
Alt+Tab cycle, isolated audio routing, complete splash integration and real
SDDM authentication/power actions remain explicitly `blocked` with specific
environmental limitations. No offscreen capture was promoted to live evidence,
and the active desktop and SDDM settings were unchanged.

## Phase 7 — Public v5 release and readback

- Promote the repository to stable `5.0.0` and qualify the exact annotated tag.
- Publish exactly six GitHub assets: source archive, SRPM, Fedora 44 RPM,
  qualification manifest, automated-gate report and `SHA256SUMS`.
- Require a terminal successful COPR build and actual package availability.
- Independently download, verify, install, inspect and remove the package
  without changing active KDE or SDDM settings.

**Gate:** GitHub, COPR, checksums, tag lineage, package installation,
`rpm -V`, `noxforge-doctor` and non-applying removal all read back successfully.

## Permanent constraints

- Plasma 5, Qt 5, Light and OLED variants are out of scope.
- `NoxForge`, existing `KPlugin.Id` values, package paths and install semantics
  remain public contracts.
- Artwork is original NoxForge work; other themes may only be inspected for
  technical contracts.
- Existing unrelated worktree changes are preserved.
