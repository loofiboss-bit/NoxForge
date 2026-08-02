# NoxForge 7.0.0 automated candidate gate

The stable local gate runs against the exact `7.0.0` source without installing
or applying NoxForge on the maintainer host. It covers repository validation,
142 active Python tests with nine historical v6 skips, four sanitizer probes,
46 CTest cases, QML lint, deterministic generators, byte-identical source
archives, Fedora 44 SRPM/RPM construction, clean `rpmlint`, isolated user and
system install trees, repeated install, rollback, uninstall, configuration
preservation, provenance, and `git diff --check`.

The separate disposable Fedora 44 lifecycle starts from the public v6 COPR
package and verifies v6-to-v7 upgrade, repeated install, rollback, second
upgrade, removal, fresh v7 install, `rpm -V`, `noxforge-doctor --json`, and
unchanged KDE/SDDM sentinels. Package installation never activates the theme.

The composed live matrix is recorded separately in `live/manifest.json` and is
not represented by this automated report. Hardware blur, audible routing,
physical cursor appearance, PAM authentication, and real power actions remain
unclaimed.

Version: 7.0.0
