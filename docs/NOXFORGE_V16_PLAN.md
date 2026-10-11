# NoxForge 16.0.0 — Single Source & Verified Truth

This plan records the NoxForge version 16 release scope and implementation
sequence, published as `v16.0.0`. It builds upon the 15.0.0 release and
solidifies NoxForge from rapid iterative feature growth into an engineered,
strictly verified, single-source desktop experience across KDE Plasma 6.7+,
Qt 6.11, SDDM, and Wayland.

## Product contract

NoxForge 16 preserves the authentic graphite surfaces, electric-lime precision
accent, Forge Notch (4 px) identity, system typography, KDE package roots,
three-edition architecture, and non-applying installation boundary.

Version 16 expands and consolidates the scope across five major pillars:
1. **Tokens Schema 12 & Single-Source Governance:**
   Formally introduces Schema 12 into `design/tokens.json`, defining system-wide
   reduced-motion compliance (`motion.reducedMotion`: `respect-system`,
   `shakeReplacement: edge-flash`), WCAG custom accent constraints
   (`accents.custom.minContrastOnSurface: 4.5`, `minContrastOnObsidian: 4.5`),
   and establishes single-source generator authority for variant QML assets
   (`qml/shared/` to standard and Obsidian packages) and C++ palette headers
   (`src/style/noxforgepalette.h`).
2. **Accessible Kinetic Motion & Custom Accent Engine:**
   - **Reduced Motion:** Lock screens, SDDM greeters, and KWin TabBox switchers
     respect system animation suppression (`AnimationDurationFactor=0` or
     `NOXFORGE_REDUCED_MOTION=1`), substituting dynamic error-shake with high-contrast
     edge-flash indicators and bypassing spring transitions.
   - **Accessible Password Feedback:** Accessible labels and screen-reader roles
     on authentication prompts and error banners.
   - **Custom Accent Contrast:** `noxforge-ctl accent custom` enforces WCAG AA (4.5:1)
     contrast verification against both dark graphite and pure OLED canvases.
3. **Formalized LoofiFaceID Integration:**
   Seamless, guarded opt-in integration for experimental LoofiFaceID authentication
   in SDDM (`Main.qml`) and Plasma lock screens (`LockScreen.qml`), ensuring 100%
   safe password fallback when APIs are absent, cancellation upon password keystroke
   or Escape, and zero invasive daemon or PAM side-effects.
4. **Unified Control Center GUI & Headless Verification:**
   Consolidates `tools/opacity_gui.py` into a unified tabbed Control Center GUI
   (`tools/control_center.py`), supported by a compatibility shim for existing
   shortcuts, and introduces headless `QTest` GUI verification.
5. **Doctor Schema 9, Fast CI Preflight & Rolling Contract:**
   - Upgrades `tools/noxforge-doctor` to Schema 9, validating QML variant synchronization,
     reduced-motion policies, and version coherence across all consumers.
   - Introduces `<3m` fast preflight CI (`ruff`, `shellcheck`, schema drift, unit suite).
   - Establishes rolling release contract verification in `tests/test_release_contract.py`
     and archives deprecated historical test suites into `tests/archive/`.

## Sequential phases

1. **Tokens and Authority:** Establish `NOXFORGE_V16_PLAN.md`, update
   `IMPLEMENTATION_PLAN.md`, bump `VERSION` to 16.0.0, specify `reducedMotion`
   and `custom` accents in `design/tokens.json` under Schema 12, and automate
   version synchronization across all repository consumers.
2. **Single-Source Variant QML:** Establish canonical templates in `qml/shared/`,
   implement generator in `scripts/generate_design_system.py`, and add drift
   validation in `scripts/validate.py`.
3. **Test Consolidation & Rolling Contracts:** Retire obsolete per-version test
   modules into `tests/archive/`, establish rolling contract suite in
   `tests/test_release_contract.py`, and unit-test generators.
4. **Fast CI & Validation Acceleration:** Implement preflight workflow in `.github/workflows/ci.yml`,
   optimize `scripts/validate.py` runtime and step progress, and add comprehensive QML linting.
5. **Kinetic Motion & Accent Accessibility:** Implement reduced-motion edge-flash
   fallbacks in shared QML, a11y roles, and contrast checks in `noxforge-ctl`.
6. **LoofiFaceID Integration:** Implement guarded face-authentication hooks in shared QML,
   documenting API boundaries and qualification limits.
7. **Unified Control Center GUI:** Unify opacity controls into `tools/control_center.py`,
   provide `opacity_gui.py` compatibility shim, and add headless GUI tests.
8. **Doctor Schema 9, Packaging & Release Qualification:** Upgrade `tools/noxforge-doctor`
   to Schema 9, initialize `docs/evidence/v16`, update packaging (`noxforge.spec`, `PKGBUILD`),
   and execute full release gate validation.

## Acceptance criteria

- `design/tokens.json` complies with Schema 12, defining `reducedMotion` and `custom` accents.
- All versioned consumers remain synchronized without manual drift (`sync_version.py --check`).
- QML variant files are deterministically generated from `qml/shared/` without manual divergence.
- Full test suite passes without reliance on blacklisted dead tests.
- CI includes fast preflight (<3 min) covering linting, type checks, and contracts.
- Reduced-motion policies cleanly suppress springs and shakes in favor of static edge-flash indicators.
- Custom accents strictly enforce minimum 4.5:1 contrast on graphite and Obsidian surfaces.
- LoofiFaceID integration cleanly falls back to password-only authentication when APIs are absent.
- `tools/control_center.py` integrates opacity configuration with headless test coverage.
- `noxforge-doctor` Schema 9 audits all v16 components without regressions.
- All automated checks and release gates pass cleanly.
