# NoxForge KDE

NoxForge is an original complete Global Theme for Fedora KDE 44, Plasma 6.7+
and Qt 6.11. Its Industrial Precision system combines graphite surfaces,
precision lime focus markers, restrained cyan/violet detail and the angular
Forge Notch.

The repository provides:

- a strict Plasma 6 Look-and-Feel package and optional compact panel layout;
- NoxForge Dark colors and an expanded Plasma Style without an explicit theme fallback;
- a native Qt 6 `QStylePlugin`, Aurorae decoration and KWin task switcher;
- 165 scalable system icons, 170 physical 16/22 px variants and only `hicolor` application-logo inheritance;
- 96 physical multi-size cursors, 32 original system sounds and three wallpaper resolutions;
- original splash, logout and Qt 6 SDDM experiences;
- safe user-local and separate explicit system installation tooling.

Installation never applies the theme, changes the panel, edits SDDM settings or
restarts Plasma. See [Quick start](docs/QUICKSTART.md), the authoritative
[implementation plan](docs/IMPLEMENTATION_PLAN.md) and the live
[manual testing gate](docs/MANUAL_TESTING.md). The historical issues that drove
the rebuild are recorded in the [v2 visual baseline](docs/V2_VISUAL_BASELINE.md).
Contributors run the same local and Fedora 44 CI gate documented in
[CONTRIBUTING.md](docs/CONTRIBUTING.md).
Fedora installation, explicit selection, verification and rollback are covered
in [INSTALL_FEDORA.md](docs/INSTALL_FEDORA.md); read-only diagnostics and
recovery guidance are in [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Status

NoxForge 3.0.0 is the current stable release. It preserves the v2 visual system
and adds Fedora 44 CI, a package-managed RPM path, structured live evidence and
read-only diagnostics.

The automated v3 gate covers deterministic generation, Python and CTest suites,
QML lint, isolated staging, byte-identical source archives, SRPM/RPM build and
`rpmlint`. Isolated live KWin/Plasma Wayland qualification covers theme
application, panel preservation and edges, 100/140 percent Qt composition,
multi-output placement, sound routing, and the real lock/logout/splash/SDDM
test processes. Hardware blur, injected keyboard/Alt+Tab interaction, live RTL
shell mirroring, cursor motion, and real SDDM authentication remain explicitly
unclaimed.

## License

See [LICENSES.md](LICENSES.md). All NoxForge artwork and generated audio are
original project work.
