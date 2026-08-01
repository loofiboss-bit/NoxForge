# NoxForge 6 — Kinetic Precision

NoxForge is an original, complete dark Global Theme for Fedora KDE 44,
Plasma/KWin 6.7+, Qt 6.11, and Wayland. Kinetic Precision combines quiet
graphite depth, exact lime state markers, restrained cyan/violet detail, and
short motion that settles cleanly.

![NoxForge Kinetic Precision Global Theme fullscreen preview](look-and-feel/io.github.loofiboss.noxforge.desktop/contents/previews/fullscreenpreview.png)

*Authentic generated Global Theme preview from the exact v6 wallpaper package;
this is not live desktop or compositor evidence. Its canonical 16:9 source
output is the [2560×1440 Kinetic Precision wallpaper](wallpapers/NoxForge/contents/images/2560x1440.png).*

### Applications

![NoxForge native Qt controls at the settled motion state](docs/evidence/v6/qt-motion/state-100.png)

### Plasma shell

![NoxForge Plasma Style source atlas at 100 percent](docs/evidence/v6/plasma-shell/plasma-style-atlas-100pct.png)

### Sessions

![NoxForge SDDM authentic offscreen QML composition](docs/evidence/v6/session/sddm-resolution-2560x1440.png)

### Details

![NoxForge high-visibility icon optical review](docs/evidence/v6/edge-polish/icon-priority.png)

These focused images are deterministic source-bound or authentic offscreen
outputs. They are not relabeled as a live Plasma, KWin, or SDDM session.

The repository provides:

- a strict Plasma 6 Look-and-Feel package and optional compact panel layout;
- NoxForge Dark colors and an expanded Plasma Style without an explicit theme fallback;
- a native Qt 6 `QStylePlugin`, Aurorae decoration and KWin task switcher;
- 185 scalable system icons, 196 physical 16/22 px variants and only `hicolor` application-logo inheritance;
- 96 physical multi-size cursors, 32 original system sounds and four wallpaper resolutions;
- original splash, logout and Qt 6 SDDM experiences;
- safe user-local and separate explicit system installation tooling.

Installation never applies the theme, changes the panel, edits SDDM settings or
restarts Plasma. Motion follows KDE's configured animation duration; setting it
to zero produces immediate semantic states with no spatial motion. See
[Quick start](docs/QUICKSTART.md), the authoritative
[implementation plan](docs/IMPLEMENTATION_PLAN.md) and the live
[manual testing gate](docs/MANUAL_TESTING.md). The historical issues that drove
the rebuild are recorded in the [v2 visual baseline](docs/V2_VISUAL_BASELINE.md).
Contributors run the same local and Fedora 44 CI gate documented in
[CONTRIBUTING.md](docs/CONTRIBUTING.md).
Fedora installation, explicit selection, verification and rollback are covered
in [INSTALL_FEDORA.md](docs/INSTALL_FEDORA.md); read-only diagnostics and
recovery guidance are in [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Status

This checkout contains the qualified NoxForge 6.0.0 release candidate. Its
isolated Wayland matrix passed theme application, exact panel preservation,
all four panel edges, two-output placement, visible shell fallback review, and
real Qt composition at 140 percent without changing the maintainer KDE or SDDM
configuration. Exact-tag GitHub and COPR publication plus independent package
readback are pending. NoxForge 5.0.0 remains the current verified public
release until that controlled readback completes. The exact-tag
[GitHub release](https://github.com/loofiboss-bit/NoxForge/releases/tag/v5.0.0)
provides the verified source archive, SRPM, Fedora 44 RPM, qualification
manifest, automated report and checksums. The Fedora package is available from
COPR project `loofitheboss/noxforge`; exact publication and independent
readback evidence is recorded in
[`docs/NOXFORGE_V5_PLAN.md`](docs/NOXFORGE_V5_PLAN.md). The historical v4
GitHub release contains no attached build artifacts and made no v4 COPR or
fresh live-qualification claim.

The v6 local release gate covers deterministic generation, 141 Python tests,
21 CTest cases, ASan/UBSan, QML lint, isolated staging, byte-identical source
archives, SRPM/RPM build, and `rpmlint`. Automated accessibility, reduced
motion, 100/125/140/200 percent rendering, and complete-tree performance
qualification pass. Live injected Wayland input, hardware blur,
animation-speed variants, high-contrast mode, cursor composition, production
splash integration, and real SDDM authentication remain explicitly blocked.

Compatibility, COPR installation, explicit component selection, verification,
upgrade, and safe rollback are documented in
[INSTALL_FEDORA.md](docs/INSTALL_FEDORA.md). Always select a known-good theme
and SDDM configuration before removing a theme you applied manually.

## License

See [LICENSES.md](LICENSES.md). All NoxForge artwork and generated audio are
original project work.
