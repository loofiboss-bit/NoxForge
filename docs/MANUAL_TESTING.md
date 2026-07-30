# Fedora KDE 44 manual visual gate

Run after RPM installation in a disposable Plasma 6.7+ Wayland session.
Capture evidence before any tag or publication. Results must be `passed`,
`failed`, `blocked`, or `not-applicable` in
`docs/evidence/v6/qualification.json`; automated evidence never substitutes for
a live result.

Current candidate: v6 development worktree on Fedora KDE 44. Phases 0–5 add
authentic local source, native Qt, Plasma SVG, artwork, and offscreen QML
evidence. Every final-candidate automated result remains `pending`, and every
unavailable interactive case is explicitly `blocked` in the v6 manifest. No v5
result is promoted to v6 evidence. The completed v5 isolated Wayland matrix
remains historical release evidence in
`docs/evidence/v5/live/live-session.md`; the active maintainer desktop was not
changed.

## Historical v3 structural and live baseline

The evidence committed before the v2 visual rebuild was invalidated. The old
140 percent gallery file duplicated the 100 percent capture. It has now been
replaced by an eight-capture LTR/RTL matrix with distinct pixel dimensions and
image hashes at 100, 125, 140, and 200 percent. Aurorae sprite renders remain
structural evidence and do not prove a composed window decoration.

| Check | 100% | 140% | Notes |
| --- | --- | --- | --- |
| NoxForge appears and applies from Global Theme | Passed | Passed | Isolated live apply; two-output capture recorded |
| Existing panel is preserved without resetLayout | Passed | Passed | Panel hash and count were identical before/after |
| Optional compact panel has no edge seams | Passed | Passed | Bottom, top, left, and right captured |
| Popups and dialogs read correctly with blur on/off | Blocked | Blocked | Solid/translucent assets pass; live KWin blur is unqualified |
| Qt buttons, inputs, menus, tabs and lists show every state | Passed | Passed | Native style composed live at 100/140%; full state matrix also passes offscreen |
| Keyboard focus and keyboard-only navigation remain visible | Blocked | Blocked | Focus ring passes offscreen; interaction requires a disposable session |
| RTL mirrors asymmetric controls and Forge Notch safely | Offscreen | Blocked | Eight-capture matrix passes; live shell mirroring is unqualified |
| Plasma widgets load no visible default-theme fallback | Passed | Passed | Live Plasma shell, horizontal/vertical panels, and two outputs captured |
| Aurorae active/inactive/maximized/button states are intact | Blocked | Blocked | Sprite validation passes; live KWin is unqualified |
| Alt+Tab switcher handles icons, long titles and no windows | Blocked | Blocked | Requires live KWin |
| Icons are clear at 16, 22, 24, 32 and 48 px | Passed | Passed | Live horizontal/vertical panels plus exact-size contact sheet |
| Cursors are clear at 100%, 140% and 200% | Blocked | Blocked | Physical files pass; live compositor scaling is unqualified |
| System sounds are restrained and correctly routed | Passed | Passed | PipeWire route succeeded; volume event true peak was -18.1 dBFS |
| Splash, logout and lock-screen surfaces remain coherent | Passed | Passed | Real testing/windowed processes captured in isolated session |
| SDDM user/session/layout/error/power flows work | Blocked | Blocked | Runtime-mocked preview passes; recoverable live SDDM is unavailable |
| Multi-monitor placement and all panel edges work | Passed | Passed | Two virtual outputs and all four panel edges captured |

## Evidence captured (2026-07-18, local offscreen gate)

- Qt widget gallery: LTR and RTL at 100/125/140/200%, plus the data page; all files have expected dimensions and unique hashes
- SDDM: actual `Main.qml` rendered at 960×540 with mock user/session/keyboard/SDDM objects; no clipping
- Icon render: 165 scalable SVGs, 170 physical optical variants, and a five-size semantic-state contact sheet
- Cursor validation: 96 physical files with distinct canonical zoom, color-picker, cardinal-arrow, and drag sources
- Sound validation: 32 Ogg events, all valid OggS magic
- Wallpaper: deterministic 2560×1440, 3840×2160, and 3440×1440 PNGs plus dimmed SDDM background
- QML: generated tokens and physical N/F mark copies; no raw palette hex values in runtime QML

Current automated results are summarized in
`docs/evidence/v3/automated-gate.md` and validated separately from live cases.
Available live results and limitations are recorded in
`docs/evidence/v3/live-session.md`.

## Current v5 Phase 2 offscreen evidence (2026-07-26)

The native Qt style gate renders the control surface in LTR and RTL at
100/125/140/200 percent, plus separate data, menu, state and stress surfaces at
100 percent. All 12 captures use authentic Qt 6 widgets, have the expected
pixel dimensions and have unique hashes. The matrix covers mirrored
subcontrols, sort and close indicators, tri-state checkboxes, static busy
progress, disabled content, long labels and dense geometry.

These reviewed reference renders are automated structural evidence only. They
do not change the blocked v5 live qualification manifest and do not claim
keyboard interaction, compositor behavior or desktop integration.

## Current v5 Phase 3 offscreen evidence (2026-07-26)

`docs/evidence/plasma-style-atlas.json` inventories all 43 Plasma 6.7 widget
families, weather artwork, the dialog background and every opaque, solid and
translucent background variant. Its four committed atlases contain 56 sources
at 100/125/140/200 percent and bind the complete declared state and panel-edge
orientation contracts to source and raster hashes.

This deterministic atlas qualifies generated source coverage, rasterization,
nine-slice paint consistency and edge-specific task markers. It is not live
Plasma evidence. Compositor blur, actual panel placement, interactive shell
states and visible fallback behavior remain blocked until the Phase 6 isolated
Wayland matrix is explicitly authorized and run.

## Current v5 Phase 4 artwork evidence (2026-07-26)

`docs/evidence/artwork-contact-sheets.json` binds the canonical N/F mark,
independent 16:9 and ultrawide wallpaper sources, fixed KDE/Plasma/System
Settings icon fixture, cursor coverage and normalized sound metrics to three
reviewed contact sheets. Generator checks reproduce every output byte for byte,
and validation rejects unlisted semantic duplicates, invalid cursor hotspots,
animation timing drift, loudness drift, copied package links and stale sheets.

The sheets establish editable-source and optical-review evidence. They do not
claim live cursor motion, audible speaker/headphone behavior, wallpaper
placement by Plasma, or session-surface integration; those remain part of the
explicit Phase 6 live matrix.

## Current v5 Phase 6 isolated live evidence (2026-07-26)

Separate temporary HOME, XDG, D-Bus and KWin virtual Wayland environments
qualified Global Theme application, exact panel preservation, all panel edges,
two-output composition, shell artwork, required panel icons and real Qt
composition at scale 1.0 and 1.4. The real windowed logout greeter and SDDM test
mode also rendered, but their captures do not prove private lock-screen code,
PAM authentication or power actions.

Hardware blur, complete keyboard/pointer interaction, live RTL, a held visible
Alt+Tab cycle, controllable cursor scaling, isolated PipeWire output and the v5
splash through its production integration remain blocked with specific
reasons in `docs/evidence/v5/qualification.json`.

## Current v6 Phase 5 offscreen session evidence (2026-07-30)

`docs/evidence/v6/session/manifest.json` binds 46 authentic offscreen renders
of the production Splash, SDDM, Logout, and TabBox QML to their exact source
hashes. It covers start/mid/end choreography, 1280×720, 1920×1080, 2560×1440,
and 3440×1440, plus standard, long RTL, keyboard-focus, empty, error, busy,
many-window, and reduced-motion scenarios. The SDDM first-frame process median
is separately compared with the reviewed v5 baseline and must remain within
ten percent.

This evidence qualifies deterministic QML composition and preserved mocked
runtime contracts only. It does not qualify PAM authentication, power actions,
pointer or keyboard interaction, a held KWin Alt+Tab cycle, production splash
integration, or any running SDDM/Plasma session. Those cases remain explicitly
blocked for Phase 7.

## Current v6 Phase 6 edge-polish evidence (2026-07-30)

`docs/evidence/v6/edge-polish/manifest.json` binds the exact Aurorae sources,
56 ranked high-visibility icons, all canonical cursor sources, and the
byte-frozen sound tree to three deterministic optical sheets. The icon sheet
covers 16/22/24/32/48 px without expanding the runtime fixture or optical
variant inventory. Cursor checks parse the physical Xcursor files and preserve
24/32/48 px payloads, canonical hotspots, 12 busy frames, and 80 ms timing.

The Aurorae sheet covers active/inactive materials and every menu, minimize,
maximize, restore, and close button source state. It is not a composed KWin
window. Live active/inactive/maximized/shaded composition and compositor cursor
scaling remain blocked for Phase 7.

## Current v6 Phase 7 automated qualification (2026-07-30)

`docs/evidence/v6/accessibility-review.json` records all token contrast pairs,
non-color state indicators, the system-font contract, keyboard traversal
structure, RTL, 100/125/140/200 percent coverage, and zero-duration reduced
motion. Its Qt 6.11 offscreen platform probe reported `NoPreference`, so it
does not claim that a live high-contrast preference was exercised.

`docs/evidence/v6/performance.json` compares the complete v6 tree with the
immutable reviewed v5 baseline using eleven warmed, interleaved medians.
Gallery startup, control rendering, and SDDM first frame remain within ten
percent. A native 500-cycle input and animation stress probe reports no failed
case, no retained widget, a stopped idle timer, and heap growth within its
fixed budget. These are automated offscreen and sanitizer-backed results, not
interactive frame or input evidence.

Every live case in `docs/evidence/v6/qualification.json` remains `blocked`.
The required disposable Wayland session, injected pointer/keyboard input,
hardware-composited blur, real SDDM authentication/power actions, composed
Aurorae interaction, live cursor scaling, animation-speed variants, and
two-output placement were not run and are not claimed.

## Remaining interactive checks (require a physical or input-capable test environment)

The following cannot be closed without explicitly applying the Global Theme in
an isolated System Settings session and interacting with that desktop. No live
check above has been marked passed. The test operator must:

1. Compare popups with hardware blur enabled and disabled.
2. Navigate with injected keyboard input through System Settings and session dialogs.
3. Exercise Aurorae active/inactive/maximized/hover/pressed states.
4. Hold Alt+Tab with multiple windows, long titles and the empty state.
5. Verify cursor motion at 100, 140 and 200 percent.
6. Verify speaker/headphone routing and volume.
7. Verify the production splash integration in a disposable login.
8. Verify SDDM authentication and power flows in a recoverable VM.

Automated validation and offscreen rendering are structural evidence only and
do not close these graphical checks.
