# NoxForge 21.0.0 candidate qualification status

Version: 21.0.4

Release state: candidate

Baseline: 20.0.0 (`5be527cc3fae42dfadec2125819cc84afeb89977`)

## Automated gate

The local release verification validates the full single-source design system,
Duotone Surface Iconography (482 scalable + 1052 optical), Aurorae v2, modular
Plasma 6.8 Union CSS, event-driven native Qt 6 style, Ecosystem v4 (25 apps),
OSD & SystemDialog QML, Live Control Core, and Control Center v6:

| Check | Result |
| --- | --- |
| Python test suite | Passed (257 active tests via `scripts/run_python_tests.py`) |
| CMake / CTest Qt suite | Passed (75/75 offscreen tests via `ctest` + 4/4 ASan/UBSan probes) |
| Version coherence | Synchronized across 63 version fields and 50 consumers (`scripts/sync_version.py --check`) |
| QML variant parity | Verified 18 outputs byte-identical from `qml/shared/` (`scripts/generate_design_system.py --check`) |
| Duotone icons, cursors, audio & Plasma SVGs | Verified (`generate_visual_assets.py --check`, `generate_cursors.py --check`, `generate_sound_theme.py --check`, `generate_plasma_svgs.py --check`, `check_plasma_rasters.py`) |
| Validation pipeline | Clean 0 errors across 22 steps (`scripts/validate.py`) |
| Doctor diagnostics | Schema 14 valid (`tools/noxforge-doctor --json`) |
| Tokens & contracts | Tokens Schema 17, Artwork Contract, and Edge Polish verified |
| Store and portable packages | Verified (`scripts/validate_store_packages.py`, `scripts/check_store_kpackages.py`) |
| Reproducible source archive & RPM | Verified (`scripts/release-check.py`) |

## Remaining qualification

Arch build and live login, Arch pacman lifecycle, physical login/PAM,
pointer/input, audio/power, mixed physical displays, and the complete live
scale/RTL/focus/motion matrix remain `pending`. Offscreen and generated results
do not establish behavior in those environments.
