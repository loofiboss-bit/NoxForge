# NoxForge 13.0.0 release and qualification status

Version: 13.0.1

Commit: `4ffd11c15989602bcddb1f6202082029be2d3520`

Release state: published

The [v13.0.0 GitHub release](https://github.com/loofiboss-bit/NoxForge/releases/tag/v13.0.0)
was built from the commit above. Its [canonical release workflow](https://github.com/loofiboss-bit/NoxForge/actions/runs/35924171954)
completed successfully for that exact tag. The build and publication jobs both
passed.

## Automated gate

The canonical workflow ran the full Fedora 44 release gate, built the release
packages, and qualified the RPM upgrade, reinstall, rollback, and removal
transactions. The results recorded in the workflow logs are:

| Check | Result |
| --- | --- |
| Python | 163 tests: 154 passed, 9 skipped, 0 failures, 0 errors |
| Fedora CTest | 73/73 passed |
| ASan and UBSan | 4/4 probes passed |
| Fedora RPM and SRPM build | Passed |
| RPM upgrade, reinstall, rollback, and removal | Passed; configuration preserved |
| Store and portable packages, including KPackage lifecycle | Passed |
| Reproducible source archive and artifact checksums | Passed |

The checked-in [`qualification.json`](qualification.json) and the qualification
asset attached to the published release contain inherited v12 details. In
particular, their Python and CTest counters say 145 and 72; those are not v13
results. Use the exact-tag workflow logs linked above for the v13 counts.

## Remaining qualification

Arch build and live login, Arch pacman lifecycle, physical login/PAM,
pointer/input, audio/power, mixed physical displays, and the complete live
scale/RTL/focus/motion matrix remain `pending`. Offscreen and generated results
do not establish behavior in those environments.
