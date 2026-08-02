# NoxForge v7 composed Wayland qualification

Date: 2026-08-02

Result: passed

Version: 7.0.0

Package: `noxforge-7.0.0-1.fc44.x86_64`

The exact local stable RPM passed `rpm -V` and `noxforge-doctor --json` before
the matrix. It was then exercised in eight disposable Fedora 44 KWin virtual
Wayland sessions: single-output 100, 125, 140, 150, 175, and 200 percent, plus
mixed-output 100+140 and 100+200 percent. All eight scenarios passed.

The matrix used KWin RemoteDesktop EIS with a libei sender for injected
keyboard and pointer input. It covered true maximize and restore, mixed-output
movement and recomposition, quick tiling, full screen, minimization, focus,
Alt mnemonics, RTL, translation expansion, System Settings, Dolphin, Konsole,
Firefox, Qt dialogs, core icons, every panel edge, launcher, task manager,
calendar, notification, OSD, Logout, production Splash, SDDM test mode, a held
TabBox, and normal, reduced, and slow motion settling.

The run used a private HOME, XDG tree, D-Bus, KWin, Plasma shell, PipeWire, and
virtual outputs. Package installation did not activate NoxForge on the
maintainer host. In the pristine headless session, the verified RPM
look-and-feel payload was copied byte-for-byte into the private XDG tree and
its defaults were staged before compositor startup because
`plasma-apply-lookandfeel` cannot initialize an otherwise empty headless
profile. The supported apply command was still executed and recorded.

The machine-readable manifest and SHA-256 binding for 110 evidence files is
`live/manifest.json`. Hardware blur quality, physical cursor appearance,
audible speaker or headphone routing, PAM authentication, and real power
actions remain unclaimed.
