# NoxForge v3 live qualification

Captured on 2026-07-24 in isolated KWin 6.7.3 virtual Wayland sessions on the
Fedora 44 maintainer host. Each session used a temporary `HOME`, XDG data,
configuration, cache, runtime directory, and D-Bus session. The active
maintainer desktop and its settings were not changed.

## Qualified

- NoxForge applied through `plasma-apply-lookandfeel` in the isolated session.
- The panel configuration SHA-256 remained
  `64f5fd5ab0b6b315d0d396c43373834868dec9405e207540b665fdb4803177e7`
  before and after application, and the panel count remained `1`.
- The 40 px compact panel rendered at bottom, top, left, and right without a
  visible seam in `live-panel-edges.png`.
- Two independent 1280 by 720 virtual outputs rendered as a 2560 by 720
  composed desktop in `live-plasma-multi-output.png`.
- System Settings rendered with the native NoxForge Qt style and Aurorae
  decoration at 100 and 140 percent scale. The 100 percent capture is
  `live-qt-wayland-rtl-100.png`; an RTL direction was requested for that run,
  but the Plasma shell did not mirror, so the capture qualifies scale and
  composition only. The 140 percent capture is `live-qt-wayland-140.png`.
- The real `kscreenlocker_greet --testing`, windowed logout greeter,
  `ksplashqml --test`, and `sddm-greeter-qt6 --test-mode` processes rendered
  successfully. Their captures are `live-lock-test.png`,
  `live-logout-test.png`, `live-splash-test.png`, and
  `live-sddm-test-mode.png`.
- `pw-play` routed `audio-volume-change.oga` successfully through the active
  PipeWire graph. Its measured true peak was -18.1 dBFS.

## Still unavailable

- A virtual framebuffer cannot prove compositor blur quality.
- Keyboard injection was not available, so keyboard-only navigation, Aurorae
  hover/pressed transitions, and a held Alt+Tab cycle were not claimed.
- The requested RTL environment did not mirror the live Plasma shell; only the
  existing LTR/RTL offscreen Qt matrix remains qualified.
- The virtual compositor did not expose a controllable pointer, so live cursor
  scaling was not claimed.
- SDDM test mode proves theme discovery and rendering, but not PAM
  authentication or real power actions. NoxForge was not activated on the
  maintainer login screen.

These limitations are explicit `blocked` results rather than substituted
offscreen passes.
