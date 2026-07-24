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

This file is automated/offscreen evidence. It does not satisfy any live
Plasma, KWin, cursor, audio, multi-monitor, or SDDM case.
