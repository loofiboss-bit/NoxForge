# NoxForge 20.0.0 candidate qualification status

Version: 20.0.0

Release state: candidate

Baseline: 19.0.0 (`69b94f23a85d4c8ad42e6df2b89be58c9bcc50e0`)

## Automated gate

The local release verification validates the full single-source design system,
kinetic iconography and multi-level status suites, Ecosystem v3 integrations,
LockScreen kinetic status indicators, and Control Center v5 Studio:

| Check | Result |
| --- | --- |
| Python test suite | Passed (249 active tests via `scripts/run_python_tests.py`) |
| CMake / CTest Qt suite | Passed (75/75 offscreen tests via `ctest`) |
| Version coherence | Synchronized across 61 version fields and 48 consumers (`scripts/sync_version.py --check`) |
| QML variant parity | Verified byte-identical from `qml/shared/` (`scripts/generate_design_system.py --check`) |
| Kinetic icons & Plasma sheets | Verified (`scripts/generate_visual_assets.py --check`, `scripts/generate_plasma_svgs.py --check`, `scripts/check_plasma_rasters.py`) |
| Validation pipeline | Clean 0 errors across 22 steps (`scripts/validate.py`) |
| Doctor diagnostics | Schema 13 valid (`tools/noxforge-doctor --json`) |
| Tokens & contracts | Tokens Schema 16, Artwork Contract, and Edge Polish verified |
| Store and portable packages | Verified (`scripts/validate_store_packages.py`) |
| Reproducible source archive | Verified (`scripts/release-check.py`) |

## Remaining qualification

Arch build and live login, Arch pacman lifecycle, physical login/PAM,
pointer/input, audio/power, mixed physical displays, and the complete live
scale/RTL/focus/motion matrix remain `pending`. Offscreen and generated results
do not establish behavior in those environments.
