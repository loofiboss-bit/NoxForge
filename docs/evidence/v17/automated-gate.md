# NoxForge 17.0.0 candidate qualification status

Version: 17.0.0

Release state: candidate

Baseline: 16.0.0 (`8fff7aff15cc7aa4f27812cd9c8ee429c1d21396`)

## Automated gate

The local release verification validates the full single-source design system,
kinetic accessibility fallbacks, guarded face-auth integration, and unified control center:

| Check | Result |
| --- | --- |
| Python test suite | Passed (all active tests passing) |
| Version coherence | Synchronized across 42+ consumers (`scripts/sync_version.py --check`) |
| QML variant parity | Verified byte-identical from `qml/shared/` (`scripts/generate_design_system.py --check`) |
| Validation pipeline | Clean 0 errors across 22 steps (`scripts/validate.py`) |
| Doctor diagnostics | Schema 9 valid (`tools/noxforge-doctor --json`) |
| Store and portable packages | Verified and structured |
| Reproducible source archive | Checksum-bound |

## Remaining qualification

Arch build and live login, Arch pacman lifecycle, physical login/PAM,
pointer/input, audio/power, mixed physical displays, and the complete live
scale/RTL/focus/motion matrix remain `pending`. Offscreen and generated results
do not establish behavior in those environments.
