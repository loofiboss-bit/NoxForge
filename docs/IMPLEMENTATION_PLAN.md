# NoxForge Implementation Plan

This file is the canonical scope and release-gate index. The active authority is
[`NOXFORGE_V8_PLAN.md`](NOXFORGE_V8_PLAN.md); the machine-readable companion is
[`distribution/release-manifest.json`](../distribution/release-manifest.json).

## Active release scope

NoxForge 8.0.0 Forge Identity is implemented phase-by-phase from the verified
v7.0.0 baseline. The current development line is `8.0.0-dev`; it is not a
release, publication, host installation, or theme-activation authorization.

The phase gates cover deterministic component packaging, a manifest-driven
portable edition, a complete system package, trimmed source/evidence, visual
presentation and restrained polish, Fedora and Arch packaging, and final
qualification. Unavailable physical cursor, sound-routing, PAM/login, power,
and live-session checks remain `pending` or `blocked` and are never inferred
from offscreen or CI evidence.

Installation is user-local and reversible by default. No phase may apply a
theme, change a panel, write active KDE settings, install SDDM, mutate a host,
publish to an external service, or rewrite the v7 history without a separate
explicit authorization.

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
