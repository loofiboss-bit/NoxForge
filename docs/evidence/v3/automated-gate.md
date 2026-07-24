# NoxForge v3 automated evidence

Captured on 2026-07-24 from Fedora 44 with Python 3.14.6, Qt 6.11.1,
Plasma/KWin 6.7.3 and KDE Frameworks 6.28.

- Phase 0 validation: passed.
- Python suite before v3 packaging work: 43 of 43 passed.
- Native Qt CTest suite: 11 of 11 passed.
- QML lint: supported SDDM, splash and logout surfaces passed; the standalone
  KWin switcher reports its documented unavailable runtime import and exits
  successfully.
- Independent deterministic source archives: byte-identical.
- Fedora SRPM and x86_64 RPM: built successfully.
- `rpmlint`: 0 errors and 0 warnings.
- Disposable Fedora 44 container: install, verify, reinstall, verify and remove
  passed with an unrelated sentinel preserved.

## Public delivery readback

- Exact release commit:
  `54cc84e36777584c7db1f87518837faeac3ec2df`.
- Required-check CI run `30092958810`: passed.
- Post-release closure CI run `30115055468`: passed on `main`.
- Exact-tag release workflow run `30093255186`: passed.
- GitHub release `v3.0.0`: six public assets downloaded independently and
  verified against `SHA256SUMS`.
- COPR build `10770449`: succeeded for Fedora 44 x86_64 from the public GitHub
  source RPM.
- Supported Fedora KDE 44 container: public COPR install, `rpm -V`,
  `noxforge-doctor`, reinstall, configuration snapshot comparison, and
  `dnf remove --no-autoremove` passed. Plasma, KWin, SDDM, Qt, and an unrelated
  sentinel remained installed and unchanged.
- Public v2.0.0 source archive migration: checksum, user installation,
  matching dry-run/uninstall, v3 COPR installation, doctor, and safe removal
  passed.

This file is automated/offscreen evidence. It does not satisfy any live
Plasma, KWin, cursor, audio, multi-monitor, or SDDM case.
