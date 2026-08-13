# NoxForge 9.0.0 — System Coherence

This document is the active implementation and release-gate authority for the
9.0.0 release. V9 aligns the complete-system edition with Fedora 44's Plasma
Login Manager while retaining the SDDM theme as an explicit compatibility
component for upgraded Fedora systems and the qualified Arch journey.

## Product contract

- Fedora 44 defaults to Plasma Login Manager. NoxForge integrates only through
  the standard wallpaper configuration surface because PLM does not support
  arbitrary third-party greeter QML.
- SDDM retains the complete NoxForge custom theme. Installation never selects,
  enables, disables, or replaces a display manager.
- Store and portable editions remain user-local and contain no login-manager
  integration, native Qt plugin, root operation, or active-settings write.
- The Forge Notch, graphite hierarchy, electric-lime state marker, system font,
  compact geometry, and restrained motion remain the visual identity.

## Sequential phases

1. Activate the V9 manifest schema, platform model, development version, and
   source/package boundaries without changing V8 history.
2. Add the read-only `loginSurface` doctor contract, configuration precedence,
   service detection, and migration-preservation fixtures.
3. Move all generated visual consumers to design-token schema 6 and the System
   Coherence graphite hierarchy; retain lime for active, focus, and progress.
4. Refresh documentation and authentic media around PLM as Fedora's default,
   with SDDM clearly presented as compatibility support.
5. Run deterministic source, Store, portable, RPM, Arch-contract, sanitizer,
   QML, CTest, accessibility, scaling, and migration gates.

## Acceptance gates

The doctor must distinguish active PLM, active SDDM, another display manager,
no detected manager, and staged roots. An installed but inactive SDDM theme may
not be reported as the active login surface. PLM configuration precedence is
`/usr/lib/plasmalogin/defaults.conf`, then `/etc/plasmalogin.conf`, then sorted
drop-ins under `/etc/plasmalogin.conf.d/`.

V8-to-V9 package lifecycle tests preserve Plasma, panel, wallpaper, PLM, and
SDDM configuration byte-for-byte. Visual gates cover 100/125/140/150/175/200
percent, RTL, expanded text, normal/reduced/slow motion, contrast, focus,
keyboard navigation, icon resolution, and blur-disabled rendering.

Unavailable physical login, PAM, input, audio, power, cursor, and multi-monitor
checks remain `pending` or `blocked`; offscreen evidence never promotes them.

## Release boundary

No custom PLM greeter, automatic wallpaper or theme application, display-manager
switch, panel reset, host installation, history rewrite, or AUR publication is
in scope. The exact v9.0.0 candidate is authorized for commit, push, annotated
tagging, and publication to GitHub Releases, COPR, and KDE Store. Every public
surface must be independently read back before the release is considered closed.
