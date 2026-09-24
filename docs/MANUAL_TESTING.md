# Manual qualification

Capture evidence for each release candidate. The current visual and versioned
record is under `docs/evidence/v13/`, with its compact visual index at
`media/manifest.json`. The canonical v13 automated gate passed; see the
[qualification summary](evidence/v13/automated-gate.md) for its results. Some
checked-in qualification counters are inherited from V12 and must not be used
as v13 results. Offscreen, generated, and composited material is never
reported as live evidence.

## Required isolated session

Use a disposable Fedora 44 or version-pinned Arch Plasma/KWin 6.7+ Wayland session,
2560x1440 at 100%, a neutral test user, the same wallpaper/panel/app set, and
no personal data. Exercise both Graphite and Obsidian palettes across the
Global Theme, Plasma Style, color scheme, Aurorae, Qt style, wallpapers, and
editor themes. Check that doctor reports synchronized selections and flags a
deliberately mixed palette for the active surfaces it inspects. Exercise
display scales 100/125/140/150/175/200%, mixed
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

## V13 evidence boundaries

Capture desktop, Dolphin, System Settings, launcher, and Aurorae/TabBox in a
neutral isolated session at 2560x1440. Run `python3 scripts/validate_media.py`
to check declared paths, PNG dimensions, and documented provenance. Review
each image for personal data before adding it to the manifest. A container
Wayland capture proves that isolated surface only; it cannot qualify hardware
input, host login, audio, mixed physical displays, or an Arch runtime.

For v12-to-v13 repeated installation, removal, and rollback, hash Plasma,
panel, wallpaper, PLM and SDDM configuration before and after each operation.
Compare bytes, including unrelated sentinels, in disposable roots. Exercise
blur disabled, long translations, RTL, and keyboard focus on selected items.

## Historical V10 candidate evidence

The five images in `media/v10/` were captured as disposable user `demo`
(uid 2000, display name Demo User), with private HOME, XDG directories, D-Bus
and Wayland sockets, and no network. The Fedora container image ID was
`fc8ac88f56edb31c6ff027df4bd6b629979e1a6841f3996795e2cde6222e2fd1`.
Only `/dev/dri/renderD128` was exposed for rendering; no host display or home
was mounted. Exact runtime versions and image hashes are in
`docs/evidence/v10/live-capture.json`. All five images were visually reviewed.

To reproduce inside that disposable image, build/install the candidate with
CMake and run `scripts/capture_v10_session.py --evidence-dir /evidence
--injector /build/noxforge-live-input --probe /build/noxforge-live-probe` as
the neutral user. The helper refuses execution outside Podman. Clear the
container KWin file capability with `setcap -r /usr/bin/kwin_wayland` when
required by the container capability set. Never run that command on the host.

`docs/evidence/v10/migration.json` records actual v9-to-v10-to-v9 cycles in
user and staged system roots. The final v9 rollback removal uses the fixed
v10 uninstaller against the v9 build manifest, including its unterminated
last line. Actual Fedora RPM transactions are separately recorded in
`docs/evidence/v10/rpm-lifecycle.json`: v9 install, v10 upgrade, reinstall,
v9 rollback and removal all preserve configuration bytes. Reproduce with
`scripts/check_v10_rpm_lifecycle.py` inside the disposable Fedora container.
It refuses host execution. Arch pacman lifecycle and physical session checks
remain pending.
