# NoxForge 12.0.1 Ecosystem Parity local qualification

Version: 13.0.0

The complete local v12 release check passed against the exact public 11.0.0
baseline.

| Check | Result |
| --- | --- |
| Python | 145 passed, 9 skipped, 0 failures/errors |
| Fedora Qt 6.11.2 / Plasma and KWin 6.7.4 | 72/72 CTest passed |
| ASan and UBSan | 4/4 probes passed |
| v11.0.0→v12.0.0 staged user/system migration and rollback | Passed; configuration hashes preserved |
| Store/portable archives and KPackage install-list-remove | Passed |
| QML lint and install/uninstall dry runs | Passed; no files or settings changed |
| Reproducible source archive | Passed; the final archive checksum is bound in Arch metadata and the release SHA256SUMS |
| Fedora RPM/SRPM build and rpmlint | Passed; 0 errors and 0 warnings |

The canonical GitHub workflow must still repeat the gate against the exact
release tag and qualify Fedora RPM transactions before the public release is
marked ready.

The gate covers generated design-system consumers, Obsidian and Konsole
contrast, the doctor schema 5 contract, Store and portable archives, CMake and
CTest, QML lint, install/uninstall dry runs, reproducible source archives, and
Fedora RPM/SRPM build validation. The canonical GitHub workflow repeats the
same gate against the exact release tag and performs the final RPM transaction
qualification.

Physical login/PAM, audio, cursor/input, mixed physical displays, the complete
live scale/RTL/motion matrix, live Arch login, and Arch pacman lifecycle remain
pending. Offscreen and generated evidence do not establish those behaviors.
