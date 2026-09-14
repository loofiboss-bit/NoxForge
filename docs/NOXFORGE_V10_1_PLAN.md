# NoxForge 10.1.0 — Lumina Edition

This plan is the active authority for the Lumina visual refinement carried by
PR #21. It follows the immutable NoxForge 10.0.0 release and must not relabel
or rewrite the historical 10.0.0 evidence.

## Product contract

Lumina keeps the NoxForge graphite surfaces, electric-lime accent, Forge Notch
identity, system typography, package IDs, user-local component model, and
non-applying installation boundary. The release intentionally refines the
wallpaper family, the SDDM preview/background, the splash surface, and the
Aurorae decoration.

Aurorae uses the documented Plasma 6 shadow contract: `Shadow=true` together
with positive `PaddingTop`, `PaddingBottom`, `PaddingLeft`, and `PaddingRight`
values. Unsupported `ActiveShadow*` and `InactiveShadow*` keys are not part of
the contract. Login-manager assets remain installable but are never activated
automatically.

## Sequential phases

1. **Scope and baseline** — move the release identity to 10.1.0, record
   10.0.0 as the exact baseline, and keep the active plan and manifest aligned.
2. **Lumina artwork** — qualify the PR's wallpaper, SDDM, splash, and Aurorae
   changes; regenerate derived PNGs, previews, contact sheets, and runtime
   hashes from the final sources.
3. **Package and contract validation** — validate all package metadata,
   Aurorae shadow padding, QML surfaces, media, and store archives.
4. **Lifecycle qualification** — run the full release gate, including the
   actual 10.0.0-to-10.1.0 upgrade/rollback checks and Fedora RPM transaction
   preservation in disposable environments.
5. **Publication** — merge the qualified PR, create the exact annotated
   `v10.1.0` tag, run the canonical release workflow, publish the named KDE
   Store and Fedora COPR surfaces, and independently read back every artifact.

## Acceptance criteria

- `VERSION`, package metadata, manifest filenames, and the exact tag all report
  `10.1.0`.
- Runtime evidence hashes and all generated media match the committed sources.
- The SDDM metadata preview is the authentic renderer output for the final
  `Main.qml` and background.
- Aurorae passes the documented shadow/padding contract and compressed SVG
  checks.
- The release gate passes against the public `v10.0.0` baseline.
- GitHub, KDE Store product `2367662`, and Fedora COPR publication are each
  independently verified after publication.

## Authority boundary

This plan authorizes repository changes and the explicit public release
requested by the user. It does not authorize installation on the active host,
automatic theme activation, display-manager changes, restarts, or claims of
physical/manual graphical verification that was not performed.
