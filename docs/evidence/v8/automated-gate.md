# NoxForge 8.0.0 automated gate

This compact report records the stable local release gate. It covers the
manifest-driven V8 artifact graph, deterministic Store packages, package safety,
source-budget checks, Python tests, sanitizer probes, CTest, QML lint,
reproducible source archives, Fedora RPM/SRPM construction, rpmlint, isolated
installation dry-runs, and `git diff --check`.

- The complete local release gate passes, including RPM/SRPM and rpmlint.
- The source archive excludes `AGENTS.md`, historical plans, full evidence,
  and future full matrices.
- Fresh 2560x1440 live input, physical cursor, audio routing, PAM/login, and
  power checks remain pending or blocked.
- Arch `makepkg`/`namcap` and external Fedora package lifecycle remain
  unverified in this release gate; the exact source archive and package
  contracts are included for independent downstream qualification.

Version: 8.0.0
Release state: release
