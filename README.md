# NoxForge KDE

NoxForge is an original complete Global Theme for Fedora KDE 44, Plasma 6.7+
and Qt 6.11. Its Industrial Precision system combines graphite surfaces,
precision lime focus markers, restrained cyan/violet detail and the angular
Forge Notch.

The repository provides:

- a strict Plasma 6 Look-and-Feel package and optional compact panel layout;
- NoxForge Dark colors and an expanded Plasma Style without an explicit theme fallback;
- a native Qt 6 `QStylePlugin`, Aurorae decoration and KWin task switcher;
- 134 system icons with only `hicolor` application-logo inheritance;
- 96 physical multi-size cursors, 32 original system sounds and a wallpaper;
- original splash, logout and Qt 6 SDDM experiences;
- safe user-local and separate explicit system installation tooling.

Installation never applies the theme, changes the panel, edits SDDM settings or
restarts Plasma. See [Quick start](docs/QUICKSTART.md), the authoritative
[implementation plan](docs/IMPLEMENTATION_PLAN.md) and the live
[manual testing gate](docs/MANUAL_TESTING.md).

## Status

Automated validation, tests and local builds are the structural v1.0 gate.
Checks requiring a live Plasma/SDDM session remain Pending until they are
performed at the recorded scaling factors.

## License

See [LICENSES.md](LICENSES.md). All NoxForge artwork and generated audio are
original project work.
