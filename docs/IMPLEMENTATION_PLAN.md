# NoxForge Implementation Plan

This file is the canonical scope and release-gate index. The active authority is
[`NOXFORGE_V8_PLAN.md`](NOXFORGE_V8_PLAN.md); the machine-readable companion is
[`distribution/release-manifest.json`](../distribution/release-manifest.json).

## Active release scope

NoxForge 8.0.0 Forge Identity is the stable release implemented phase-by-phase
from the verified v7.0.0 baseline. GitHub release publication and the update of
the historical KDE Store product `2367662` are the explicit V8 closure surfaces;
no host installation or theme activation is implied.

The phase gates cover deterministic component packaging, a manifest-driven
portable edition, a complete system package, trimmed source/evidence, visual
presentation and restrained polish, Fedora and Arch packaging, and final
qualification. Unavailable physical cursor, sound-routing, PAM/login, power,
and live-session checks remain `pending` or `blocked` and are never inferred
from offscreen or CI evidence.

Installation is user-local and reversible by default. This release does not
authorize automatic theme application, panel changes, active KDE settings,
SDDM activation, host installation, AUR publication, or v7 history rewriting.
The GitHub and KDE Store publication surfaces above are the separately
authorized release operations.

## Historical release evidence

- [`NOXFORGE_V7_PLAN.md`](NOXFORGE_V7_PLAN.md) records the completed v7 scope,
  qualification boundary, and immutable `v7.0.0` lineage.
- [`releases/v7.0.0.md`](releases/v7.0.0.md) records the historical v7 release
  without changing its source or evidence.
- [`NOXFORGE_V6_PLAN.md`](NOXFORGE_V6_PLAN.md) records the completed v6 scope,
  public release, COPR publication, and bounded live evidence.
- [`NOXFORGE_V5_PLAN.md`](NOXFORGE_V5_PLAN.md) records the completed v5 scope,
  stable release, publication and independent readback.
- [`NOXFORGE_V4_PLAN.md`](NOXFORGE_V4_PLAN.md) records the closed v4 scope and
  its source-tag-only public outcome.
- [`releases/v4.0.0.md`](releases/v4.0.0.md) records that the public v4 release
  has no attached artifacts and makes no COPR or fresh live-qualification claim.
- [`NOXFORGE_V3_PLAN.md`](NOXFORGE_V3_PLAN.md) records the completed v3.0.0
  reliability, distribution, and live-qualification release.
- [`V2_IMPLEMENTATION_PLAN.md`](V2_IMPLEMENTATION_PLAN.md) records the completed
  v2.0.0 visual rebuild scope and gates.
- [`releases/v3.0.0.md`](releases/v3.0.0.md) records the stable v3.0.0 release outcome.
- [`MANUAL_TESTING.md`](MANUAL_TESTING.md) remains authoritative for current
  live checks; unavailable graphical checks stay honestly `blocked` in the
  versioned structured evidence manifest.

Normal installation remains non-applying and reversible. No plan authorizes
automatic theme application, panel changes, SDDM activation, Plasma restarts,
publication, or external-service changes without explicit user approval.
