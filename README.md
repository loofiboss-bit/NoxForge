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

## Status

NoxForge 2.0.0 is the current stable release. Its visual rebuild passes the full
automated release gate, including deterministic generation, the Python and
CTest suites, the LTR/RTL scale matrix, isolated repeat installs and a
byte-reproducible archive. Live Plasma, KWin and interactive SDDM checks that
require applying the theme remain honestly Pending and are not replaced by
structural or offscreen evidence.

Phase 0 of the [v3 implementation plan](docs/NOXFORGE_V3_PLAN.md) preserves the
Industrial Precision design while making Aurorae generation byte-reproducible
across supported Python environments and enforcing canonical repository URLs.
Packaging, CI, live qualification and publication remain later-phase work.

## License

See [LICENSES.md](LICENSES.md). All NoxForge artwork and generated audio are
original project work.
