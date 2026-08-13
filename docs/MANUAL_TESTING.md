# Manual qualification

Capture evidence before any candidate tag or publication. The active record is
the V9 manifest under `docs/evidence/v9/` and the compact visual index at
`media/manifest.json`. Offscreen, generated, and composited material is never
reported as live evidence.

## Required isolated session

Use a disposable Fedora 44 or verified Arch Plasma/KWin 6.7+ Wayland session,
2560x1440 at 100%, a neutral test user, the same wallpaper/panel/app set, and
no personal data. Exercise display scales 100/125/140/150/175/200%, mixed
100+140 and 100+200, every panel edge, Aurorae and TabBox, shell/session
surfaces, keyboard focus/mnemonics, RTL, translation expansion, and normal,
reduced, and slow motion.

Store/component and portable checks must confirm user-local installation,
sentinel/configuration preservation, repeated install, precise uninstall, and
no active-settings write. Complete-system checks additionally cover native Qt
style, Fedora/Arch package lifecycle, rollback, PLM wallpaper selection, and
optional SDDM compatibility selection. A fresh Fedora 44 PLM session and an
upgraded Fedora SDDM session are separate qualification targets.

Physical cursor behavior, audio routing, PAM/login, power actions, and other
unavailable hardware evidence stay `pending` or `blocked`; they are never
promoted from CI or offscreen output.
