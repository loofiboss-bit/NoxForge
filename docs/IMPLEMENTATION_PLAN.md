# NoxForge Implementation Plan

This file is the canonical scope and release-gate index. The active authority is
[`NOXFORGE_V9_PLAN.md`](NOXFORGE_V9_PLAN.md); the machine-readable companion is
[`distribution/release-manifest.json`](../distribution/release-manifest.json).

## Active release scope

NoxForge 9.0.0 System Coherence is the stable release candidate based on the
verified v8.0.0 baseline. It adds an honest Fedora 44 Plasma Login Manager model,
read-only login-surface diagnostics, and a more legible graphite hierarchy.

The phase gates cover schema migration, PLM/SDDM diagnostics, deterministic
component packaging, design-token regeneration, Fedora and Arch packaging, V8
upgrade preservation, and final qualification. Unavailable physical checks
remain `pending` or `blocked` and are never inferred from offscreen or CI.

Installation is user-local and reversible by default. This release does not
authorize automatic theme application, panel changes, active KDE settings,
display-manager activation, host installation, or history rewrite. GitHub,
COPR, and KDE Store publication is authorized for the exact v9.0.0 candidate.

## Historical release evidence

- [`NOXFORGE_V8_PLAN.md`](NOXFORGE_V8_PLAN.md) records the completed V8 scope,
  public release, edition model, and immutable `v8.0.0` lineage.
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
