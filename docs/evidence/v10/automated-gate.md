# V10.1 Lumina local qualification

Version: 10.1.0
Host installation and active desktop changes are excluded.

| Check | Result |
| --- | --- |
| Python | 119 passed, 9 skipped, 0 failures/errors |
| Fedora Qt 6.11.2 / Plasma and KWin 6.7.4 | 72/72 CTest passed |
| Pinned Arch Qt 6.11.2 / Plasma and KWin 6.7.5 | Build and 72/72 CTest passed |
| ASan and UBSan | 4/4 probes passed |
| Six-scale/RTL/focus/expanded-label/reduced-motion coverage | Automated checks passed |
| Computed state compositing | 40 contrast cases passed |
| QML lint and install/uninstall dry runs | Passed |
| Store archives and generated assets | Passed |
| Independent source archive equality | Passed after freezing evidence edits |
| RPM/SRPM build and rpmlint | Passed, 0 errors and 0 warnings |
| Actual staged 10.0.0→10.1.0→10.0.0 | User and system cycles passed, configuration bytes preserved |
| Actual Fedora RPM transactions | Upgrade, reinstall, rollback and removal passed; configuration bytes preserved |
| Media | Six current neutral-profile Wayland captures, dimensions/provenance validated |

The 10.1.0 gate must pass in one uninterrupted run, including actual
10.0.0-to-10.1.0 upgrade/rollback and RPM build with zero rpmlint errors or
warnings. The canonical CI workflow reruns the entire gate against the exact
release commit; published qualification metadata links that workflow run.

Physical login/PAM, audio, cursor/input, mixed physical monitors, the full live
scale/RTL/motion matrix, live Arch login and pacman lifecycle remain pending.
Offscreen results and the isolated Fedora Wayland session do not qualify these.
See `qualification.json`, `arch.json`, `live-capture.json`, `migration.json`,
`rpm-lifecycle.json`, and `runtime-source-hashes.json` for scoped evidence.
