# NoxForge 8.0.0 — Forge Identity

This document is the active implementation and release-gate authority for the
8.0.0 development line. It is intentionally English so that it can also serve
as the public engineering record. `VERSION` is `8.0.0-dev` until every
available mandatory gate is green and one exact candidate line is bound.

## Verified v7 baseline

The baseline is the clean `main` tree at commit
`ce51c0117059fe926129d64c89e0f783dd2d430c`, tagged `v7.0.0`. The tree contains
157,316,401 tracked bytes, of which approximately 151.6 MB is evidence.
The public v7 source, SRPM, and RPM were respectively 98,993,432 bytes,
99,037,329 bytes, and 1,166,680 bytes. The v7 GitHub release is the historical
source for those numbers; no v7 tag, release asset, or historical evidence is
rewritten by V8.

The KDE Store product `2367662` is also historical input. Its one downloadable
archive is the same 98,993,432-byte source payload under a
`NoxForge-7.0.0/` directory, has no Global Theme metadata at the archive root,
and describes nine components as if they were one transaction. It uses GPL and
CC-BY-SA wording although this repository is MIT licensed, and it makes broader
compatibility claims than the qualification record. V8 corrects the package
boundaries and records the existing product ID in the release manifest; new
external IDs stay `null` until their owner creates them.

The focused local v7 gate passed 152 Python tests, nine historical skips, four
sanitizer probes, 46 CTest cases, QML checks, and `git diff --check`. Physical
Wayland input, cursor, audio, PAM/login, power, and other unavailable hardware
evidence remained unverified.

## User journeys and permanent boundaries

* **Store/component.** A user selects one or more user-local components. A
  component package never claims to include native Qt styling, SDDM, or root
  privileges. The Global Theme package is a coordinator, not a complete
  transaction; the Store description says that components are installed
  separately.
* **Portable.** The portable bundle installs all user-local Plasma components,
  Breeze application controls, an installer, an uninstaller, and a portable
  doctor below `$XDG_DATA_HOME/noxforge/`. It never installs SDDM, a native Qt
  plugin, or writes active KDE settings.
* **Complete system.** A Fedora or Arch package adds the native Qt style and a
  system doctor to the portable content. SDDM is a separately selectable system
  component. Applying a theme remains an explicit user action.

## Public contracts and budgets

`distribution/release-manifest.json` is the version-neutral source of release
version, active plan, compatibility, package IDs, edition contents, artifact
names, size budgets, and evidence policy. Scripts, candidate tooling, and
workflows must read it instead of embedding v7 paths or a six-asset count.

The existing wallpaper ID `NoxForge` is retained with display name “NoxForge
Forge”. `NoxForge-Quiet` and `NoxForge-Ultrawide` are additional selectable
wallpaper packages. Main artifacts use these names:

`noxforge-8.0.0-{source,portable,global-theme,plasma-style,colors,aurorae,icons,cursors,kwin-switcher,sounds,wallpapers}.tar.xz`

Every archive is deterministic, checksum-bound, and independently reproducible.
Each Store component is below 10 MB; the wallpaper bundle is below 8 MB;
portable is below 10 MB; developer source and a V8 tag archive are below 20 MB;
the binary RPM is below 2 MB and normally no more than 25% larger than v7.

`noxforge-doctor --json` exposes a stable `edition` object with `kind`
(`component`, `portable`, `complete-system`, `mixed`, or `absent`), `status`,
capabilities, and the actual missing mandatory components. Missing Qt plugin
and SDDM are valid for portable installations.

Store and portable Global Theme defaults use `widgetStyle=Breeze`; system
packages use `widgetStyle=NoxForge`. Both are generated from the same edition
contract.

## Sequential phases

### Phase 0 — Baseline and scope

Create this plan, make it active in `docs/IMPLEMENTATION_PLAN.md`, move active
consumers to `8.0.0-dev`, retain immutable v7 history and metadata, and register
KDE Store product `2367662` in the manifest. Define and test the three user
journeys above.

### Phase 1 — Correct Store packaging

Implement deterministic allowlist-based Store builders and a validator that
rejects unsafe paths, links, devices, foreign files, metadata drift, and budget
overruns. Put Global Theme and Plasma Style metadata at their KPackage roots;
follow the KNewStuff target roots for Aurorae, icons, cursors, colors, sounds,
and wallpapers. Exercise install/list/remove with `kpackagetool6` and isolated
HOME/XDG roots, including repeated installs, sentinels, and configuration
hashes. Add English MIT-licensed Store copy with verified compatibility and
component dependencies.

### Phase 2 — Runtime/source/evidence separation

Trim full historical image matrices from the V8 tree without rewriting the v7
history. Keep compact manifests, final reports, and a small representative
selection; ignore future full matrices and retain their hash manifests only as
temporary CI evidence. Split source, portable, and all builds in `build.py`.
The developer source contains build/test/legal inputs but not historical plans,
full matrices, unnecessary containers, or `AGENTS.md`. Both the source archive
and a V8 tag archive stay below 20 MB and can build native style/RPM after
extraction. RPM Source0, `release-check.py`, and `release.yml` consume the
manifest graph.

### Phase 3 — Portable and complete editions

Make installation atomic and manifest-based below `$XDG_DATA_HOME/noxforge/`,
with safe migration of known older roots, dry-run, reinstall, and precise
uninstall. Install a portable doctor under the owned data root and document its
exact invocation. Generate Breeze defaults for Store/portable and NoxForge
defaults only for system packages with the native plugin. Doctor reports a full
portable install as `ok`, detects user/system shadowing, and reports active
`widgetStyle=NoxForge` without a plugin as a repairable mixed state. Fedora
install/upgrade/rollback/removal remain scriptlet-free and non-activating.

### Phase 4 — Visual presentation

Add `media/manifest.json` and six authentic V8 captures from one isolated Plasma
session at 2560x1440, 100%, with a neutral test user and no personal data.
Record live/offscreen/generated/composited provenance separately. Generate Store
icon/hero, GitHub social preview, and Global Theme previews only from authentic
underlying material. Restructure the README around the real desktop hero,
value proposition, install choices, gallery, components, compatibility,
rollback, then development/evidence.

### Phase 5 — Restrained visual polish

Limit visual changes to semantic surface/raised/overlay colors, neutral keylines,
and active/inactive decoration. Keep the background, electric lime, spacing,
radii, motion, and Forge Notch anchors. Improve blur-disabled behavior without
glow, broad accent fills, new gradients, or card-in-card patterns. Preserve
pointer target sizes, reserve destructive red for hover/press, and adjust only
observed shell/settings/session icons. Add and regenerate the Forge, Quiet, and
Ultrawide wallpaper contracts, then run identical V7/V8 comparisons and
regenerate Phase 4 media.

### Phase 6 — Arch complete package

Add verified `packaging/arch/PKGBUILD` and generated `.SRCINFO` for `noxforge`
(MIT, x86_64, CMake/Ninja, Qt 6, Kirigami, Plasma/KWin 6.7+, Breeze icons,
Python, and SDDM). Use the exact V8 source URL and SHA-256; preload that file in
temporary `SRCDEST` for local candidates rather than using `SKIP`. Where an
Arch environment is available, run `makepkg --verifysource --cleanbuild`,
`namcap`, isolated pacman-root install, repeat install, rollback, uninstall,
doctor, and configuration-preservation checks. Do not publish to AUR.

### Phase 7 — Documentation and release qualification

Update Quickstart, Fedora/portable/Arch installation, compatibility,
troubleshooting, contributing, doctor manual, release notes, changelogs, and
metadata to V8. Add a regression test that forbids V6/V7 as current release
claims in user-facing documents. Add four focused issue templates and an
English GitHub metadata proposal. Run Fedora, Arch, Store/portable, and the
full display/input matrix. Only the exact qualified candidate may become
`8.0.0`; unavailable hardware remains `pending` or `blocked`.

## Acceptance gates

Two independent builds of every archive are byte-identical and match
`SHA256SUMS`. Good and malicious archive fixtures cover path safety, metadata,
license/ID parity, allowlists, and all budgets. Isolated install/upgrade/reinstall
/remove covers every Store package and the portable bundle, with sentinels,
configuration hashes, and no activation. Doctor covers component, portable,
complete, mixed, legacy migration, missing plugin, missing Store dependency, and
complete uninstall. The distributed source archive itself is built and tested.

Run Python, CMake/Ninja, CTest, ASan/UBSan, QML lint, generator drift,
RPM/SRPM/rpmlint, Arch makepkg/namcap where available, and `git diff --check`.
The display matrix covers 100/125/140/150/175/200%, mixed scaling, every panel
edge, Aurorae/TabBox, shell/session surfaces, focus/mnemonics/RTL/translation
expansion, and normal/reduced/slow motion. Final review rejects generated
accidents, host mutations, and unrelated changes.

## Explicit non-scope

No history rewrite, commit, push, tag, release, KDE Store/AUR/GitHub settings
change, host installation, automatic activation, GUI installer, Kvantum,
light/OLED/accent variant, panel reset, or broad compatibility claim is part of
this plan.
