# Experimental LoofiFaceID integration

NoxForge's Graphite and Obsidian SDDM themes and Plasma lock screens can load
LoofiFaceID's separate face-authentication controls when the matching,
experimental integration API is present. The themes remain usable with
unmodified SDDM and KScreenLocker; those builds do not load the optional
controls.

## Supported theme interfaces

- SDDM 0.21.0 built with LoofiFaceID's experimental face-authentication API
  version 1. Both `sddm/NoxForge/theme.conf` and
  `sddm/NoxForgeObsidian/theme.conf` declare that interface and load the
  embedded `qrc:/theme/FaceAuthenticationControl.qml` only when the API method
  is available.
- KScreenLocker 6.7.5 built with LoofiFaceID's experimental face factor. Both
  Plasma lock screens load
  `qrc:/fallbacktheme/FaceAuthenticationControl.qml` only when the injected
  `faceAuthenticator` exposes the versioned theme-registration method.

The SDDM theme passes its current username and session to the face control.
Changing the username clears the selection immediately and refreshes it after
250 ms of inactivity. Starting password entry cancels an active face attempt
without clearing typed characters. The lock-screen control sits beside the
always-available password field; password entry, password submission, and
Escape cancel the face attempt. Escape preserves typed characters when it
cancels a running attempt.

The per-user face policy remains owned by LoofiFaceID and defaults to off.
Only a manual or enabled activity policy can show the face control. The normal
password PAM services remain separate from the dedicated face-authentication
services. The NoxForge packages install no daemon, PAM configuration, policy
file, camera helper, or display-manager patch, and do not enable user policies,
select a theme, or change the active desktop.

LoofiFaceID's version-pinned SDDM and KScreenLocker patches are maintained in
its [experimental integration PR](https://github.com/loofiboss-bit/LoofiFaceID/pull/23).

## Verification boundary

Repository tests validate the optional-interface guards, selected-user and
session hand-off, password cancellation, and password-only rendering without
the experimental APIs. They do not prove physical SDDM login, Plasma unlock,
camera cancellation, SELinux behavior, screen-reader behavior, or biometric
qualification. Those checks remain pending on a dedicated test system with the
matching experimental SDDM/KScreenLocker builds and LoofiFaceID setup.
