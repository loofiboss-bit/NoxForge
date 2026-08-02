# NoxForge 6.0.0 — Kinetic Precision

**Repository:** `loofiboss-bit/NoxForge`
**Reviewed baseline:** `main` at `6a113e71980d106c38a2bbdece6df171c0ae9ed3`
**Current stable release:** `v6.0.0` at `d6c4e3c5584b9fdd61c7bb3ae9b3b693f03e67f6`
**Target:** Fedora KDE 44, Plasma/KWin 6.7+, Qt 6.11, Wayland
**Status:** Completed historical authority; v6.0.0 is publicly released
**Release theme:** **Kinetic Precision**

This canonical plan was reconciled from the reviewed Kinetic Precision proposal
on 2026-07-30. The reviewed baseline matched exactly before reconciliation:
`main` at `6a113e71980d106c38a2bbdece6df171c0ae9ed3`, with no tracked worktree
changes. The source proposal is retained as a short provenance pointer at
`docs/NOXFORGE_V6_KINETIC_PRECISION_PLAN.md`. This file is historical; the
active authority is `docs/NOXFORGE_V7_PLAN.md`.

## Executive decision

NoxForge v6 should be a focused visual and motion release, not another breadth,
packaging, or asset-count release.

V5 already provides an unusually complete technical foundation:

- a strict Plasma 6 Global Theme and native Qt 6 `QStylePlugin`;
- all 43 covered Plasma widget families and opaque, solid, and translucent
  variants;
- 185 scalable icons, 196 physical 16/22 px optical variants, 96 cursors, and
  32 sounds;
- original session surfaces, Aurorae, TabBox, wallpapers, and brand artwork;
- deterministic generation, reference renders, accessibility contracts,
  Fedora 44 CI, RPM/COPR distribution, and exact release provenance;
- verified non-applying installation and clean removal.

The next large gain is not more components. It is making the existing system
feel authored, alive, and premium in daily use.

V6 turns the current **Industrial Precision** identity into **Kinetic
Precision**:

- quieter graphite surfaces with clearer depth;
- less border noise and less muddy selected-state color;
- stronger typography and spacing hierarchy without replacing the system font;
- a more resolved N/F mark and wallpaper composition;
- purposeful motion in the native Qt style and the QML surfaces that can
  actually animate;
- richer static Plasma SVG states without pretending SVG themes provide
  application-style animation;
- no neon-glow, glass-everywhere, cyberpunk-HUD, or “AI concept UI” excess.

## Top priority

Build and approve the v6 visual north star and motion contract before rewriting
individual assets.

Do not begin v6 by:

- adding more icon names;
- adding more theme variants;
- changing packaging or release infrastructure;
- placing animation on every surface;
- importing visual assets from another theme;
- introducing Kvantum, a third-party KWin effect, or an external widget.

The first implementation objective is one coherent target render for each of
these product layers:

1. native Qt application;
2. Plasma shell, panel, popup, and notification;
3. SDDM and session actions;
4. Alt+Tab and window chrome;
5. brand mark and wallpaper;
6. motion storyboard at start, midpoint, and settled state.

## Evidence-based review of v5

### What is already strong

- The palette is recognizable and the lime accent has a clear semantic role.
- The Forge Notch is constrained instead of being stamped onto every control.
- The theme is complete enough to avoid most Breeze fallback artwork.
- The Qt style is compact and usable at 100–200 percent scale and in RTL.
- The icon and cursor families are original and internally consistent.
- SDDM, Splash, Logout, and TabBox preserve their real runtime contracts.
- The repository has stronger test, qualification, and release discipline than
  most community themes.
- There are currently no open issues or pull requests requiring v6 scope.

### What prevents the current design from feeling top-tier

1. **Too much equal visual weight**
   - Canvas, cards, controls, tables, menus, and toolbars rely heavily on similar
     graphite fills and one-pixel outlines.
   - Parent and child containers are often both boxed.
   - Secondary chrome does not recede enough.

2. **State hierarchy is technically correct but visually blunt**
   - The current gallery can make a focused button read like a filled primary
     action.
   - Selected rows use a muddy olive field where a quieter neutral surface plus
     a precise lime rail would read better.
   - Hover, focus, checked, selected, and primary states need more distinct
     signatures.

3. **The native Qt style is effectively static**
   - `noxforgestyle.cpp` switches colors directly from `QStyle::State` flags.
   - It does not currently install a widget event filter or interpolate state.
   - `SH_Widget_Animation_Duration` is not defined by the style.
   - Busy progress is centered but static.

4. **The QML motion is too limited**
   - Splash has a simple opacity reveal and width transition.
   - Logout buttons switch colors with no transition and the composition is
     visually small on large displays.
   - SDDM is polished structurally but mostly static.
   - TabBox is a generic vertical list rather than a signature NoxForge moment.

5. **The brand and wallpaper need another art-direction pass**
   - The N/F mark is recognizable but the joins, negative space, and optical
     balance still feel more like a project logo than a mature identity.
   - The wallpaper's large lime wedge competes with windows and desktop content.
   - The composition reads “gaming theme” faster than “industrial precision.”

6. **Iconography is broad but not yet distinctive enough**
   - The white outline plus small lime fragment is coherent but can feel
     mechanically repeated.
   - Some dense symbols need fewer internal details at 16 and 22 px.
   - V6 should refine the most visible runtime icons, not increase the count.

7. **The repository proves engineering better than it presents the product**
   - README and release material explain the package well but do not yet sell
     the visual experience with a concise, premium screenshot sequence.

## Inspiration translated into NoxForge rules

These references are for principles and technical contracts only. Their
artwork, SVG paths, layouts, and brand assets must not be copied.

| Reference | Useful principle | NoxForge adaptation |
| --- | --- | --- |
| [Linear 2026 visual refresh](https://linear.app/now/behind-the-latest-design-refresh) | Secondary chrome should not compete for attention; design tokens should be tuned against the real product. | Dim inactive navigation and container edges, reduce border stacking, and review token changes in authentic Qt/Plasma renders rather than isolated swatches. |
| [Fluent 2 motion](https://fluent2.microsoft.design/motion) | Motion should be functional, natural, consistent, quick, and accessible; large top-level changes often need a fade rather than dramatic travel. | Use short state transitions, small 4–8 px entrance travel, and fades for large session surfaces. No full-screen slides. |
| [IBM Carbon motion](https://carbondesignsystem.com/elements/motion/overview/) | Separate productive microinteraction from rare expressive motion; avoid bounce, stretch, and abrupt stops. | Keep normal controls in the 90–140 ms range and reserve 180–280 ms choreography for Splash, SDDM entry, Logout, and TabBox. |
| [Carbon motion checklist](https://carbondesignsystem.com/elements/motion/resources/) | Microinteractions should be purposeful, responsive, and usually around 90–120 ms. | Every animation must identify the state change it explains and have a zero-duration reduced-motion result. |
| [KDE Plasma Style documentation](https://develop.kde.org/docs/plasma/theme/theme-details/) | Plasma Style and Qt `QStyle` are separate layers; Plasma Style is SVG-based and missing assets can fall back to Breeze. | Animate Qt/QML where supported. Keep Plasma SVG work state-based, complete, and fallback-free. |
| [Qt Quick animations](https://doc.qt.io/qt-6/qtquick-statesanimations-animations.html) | State transitions can interpolate opacity, color, position, and other properties. | Use `Behavior`, `Transition`, and explicit semantic motion tokens in session surfaces. |
| [Qt `SH_Widget_Animation_Duration`](https://doc.qt.io/qt-6/qstyle.html) | A zero duration means widget animation is disabled. | Expose and honor the effective KDE/Qt duration in the native style; reduced motion is a contract, not an optional polish item. |
| [Colloid KDE](https://github.com/vinceliuice/Colloid-kde), [Graphite KDE](https://github.com/vinceliuice/Graphite-kde-theme), and [Layan KDE](https://github.com/vinceliuice/layan-kde) | Strong desktop themes repeat one material, shape, and spacing language across every layer. | Match their cross-surface cohesion while keeping NoxForge original, Plasma 6-native, self-contained, and independent of Kvantum or companion packs. |

## V6 visual north star

### Product personality

**Technical calm.**

NoxForge should feel like a precise workstation interface with a restrained
industrial edge. It should not feel like:

- a game launcher;
- a sci-fi cockpit;
- a RGB peripheral control panel;
- a glassmorphism concept;
- a rounded mobile UI enlarged onto a desktop.

At rest, the desktop is quiet. During interaction, one precise signal shows
where attention moved.

### Surface hierarchy

Keep the existing anchor palette but rebuild how it is applied.

Required semantic layers:

1. `canvas` — deepest workspace background;
2. `sunken` — inputs, data wells, and recessed regions;
3. `surface` — windows, panels, and stable containers;
4. `raised` — controls and cards that need separation;
5. `overlay` — popups, menus, notifications, session cards, and TabBox.

Add only the supporting tokens needed to express this:

- `surfaceSunken`;
- `surfaceOverlay`;
- `edgeHighlight`;
- `outlineMuted`;
- `accentSoft`;
- `accentMuted`;
- `shadowAmbient`;
- `shadowOverlay`.

Rules:

- Tonal separation does most of the work.
- A full outline is used only when the boundary would otherwise be ambiguous.
- Adjacent parent and child surfaces must not both draw a complete border.
- Popups get one outer keyline, one subtle top/leading highlight, and a neutral
  shadow when composition permits it.
- Colored shadows and ambient lime glow are forbidden.
- Translucent variants must remain readable when blur is unavailable.

### Accent budget

- Lime is a signal, not a surface material.
- Ambient shell composition: no large lime fills.
- Selected row or task: neutral/soft selected surface plus a 3 px lime rail or
  short marker.
- Focus: one 2 px lime focus treatment; never both a lime fill and ring.
- Primary action: at most one filled lime action per decision group.
- Icon accent coverage target: 8 percent or less unless the icon itself carries
  a semantic success state.
- Cyan remains busy, information, and progress.
- Violet remains a rare brand counterpoint.
- Red appears only for destructive/error intent, primarily on interaction.

### Geometry

- Preserve the 4 px base grid.
- Compact controls: 4 px radius.
- Standard controls: 6 px radius.
- Overlay/session cards: 8 px radius.
- Forge Notch remains 4 px and appears only on active, selected, focused, or
  branded surfaces.
- Do not scale controls on hover or press.
- Do not add pill shapes unless the control is semantically a badge or switch.

### Typography

- Continue to use the KDE-configured system font.
- Do not ship or force a custom application font.
- Define generated semantic roles for:
  - display/clock;
  - surface title;
  - section title;
  - body;
  - control label;
  - metadata;
  - micro-label.
- Use weight, size, contrast, and spacing before adding more separators.
- Reserve uppercase tracking for the `NOXFORGE` wordmark and rare micro-labels.
- Replace generic all-caps headings such as `SIGN IN`, `SESSION`, and `POWER`
  where sentence case produces a calmer hierarchy.
- Keep numeric clocks and progress readouts optically stable.

### Brand mark

Refine the existing N/F concept instead of replacing it with an unrelated logo.

Required outcomes:

- cleaner N-to-F transition;
- deliberate shared angle and stroke logic;
- more stable negative space at 16, 24, 48, 128, and 512 px;
- one monochrome master plus semantic lime detail;
- a horizontal mark/wordmark lockup for README, SDDM, and Splash;
- no faux 3D extrusion, gradient chrome, or generated mascot.

### Wallpaper

Create an original v6 wallpaper family from editable deterministic vector
sources.

Direction:

- layered graphite “forged planes” with subtle depth;
- a quiet central and right-side work area;
- lime used as one narrow energy seam, not a dominant slab;
- cyan/violet details visible only on close inspection;
- independent 16:9 and ultrawide compositions;
- valid crops at 1920×1080, 2560×1440, 3840×2160, and 3440×1440;
- derived dim session background without crushing foreground contrast.

Do not add a dynamic/animated wallpaper plugin in v6.

## Motion system

### Motion character

Motion should feel machined rather than elastic:

- immediate response;
- controlled acceleration;
- soft landing;
- no bounce, spring, overshoot, stretch, rubber-band, or pulse glow;
- no infinite ambient animation;
- continuous motion is allowed only for a genuine busy/progress state.

### Semantic timing

| Token | Target | Typical use |
| --- | ---: | --- |
| `instant` | 0 ms | Reduced motion and non-animated state changes |
| `press` | 90 ms | Press/release feedback |
| `productive` | 120 ms | Hover, focus, toggle, checkbox, small marker |
| `selection` | 140 ms | Tab/task/TabBox selection movement |
| `container` | 180 ms | Menu, session list, popup/card entrance |
| `expressive` | 260 ms | Rare Splash/SDDM/Logout choreography |
| `stagger` | 24 ms | Small related item sequence only |
| `busyCycle` | 900 ms | Purposeful indeterminate progress only |

Use semantic easing:

- productive enter: fast start, smooth stop;
- standard state change: restrained ease-in-out;
- exit: shorter acceleration out;
- expressive: smooth but not springy.

Store curve values in the canonical token schema. Do not hand-author different
curves in each QML file.

### Reduced motion

- `AnimationDurationFactor=0` or an equivalent zero-duration KDE/Qt policy must
  result in immediate state changes.
- QML surfaces must derive effective durations from Kirigami/KDE duration
  policy instead of capping or bypassing it.
- The Qt style must expose a correct `SH_Widget_Animation_Duration`.
- Busy indicators become a static, semantically recognizable state.
- Reduced motion must preserve focus, selection, progress, success, and error
  meaning without relying on animation.

## Release phases

## Phase 0 — Establish v6 authority and a truthful baseline

### Objective

Start from the released v5 state without relabeling old evidence as v6.

### Work

- Create `docs/NOXFORGE_V6_PLAN.md` from this approved plan.
- Point `docs/IMPLEMENTATION_PLAN.md` to v6.
- Move version consumers to `6.0.0-dev` using the existing synchronization
  tooling.
- Record the exact baseline commit, toolchain, and current v5 evidence hashes.
- Regenerate the current authentic reference set before changing visuals.
- Create `docs/evidence/v6/baseline/` with:
  - Qt Controls, Data, Menu, States, and Stress at 100 and 140 percent;
  - Plasma panel/task/popup/tooltip/notification atlas at 100 and 140 percent;
  - SDDM, Splash, Logout, and TabBox at 2560×1440;
  - current brand/wallpaper, icon, and cursor sheets.
- Add a v6 visual scorecard covering hierarchy, state clarity, cohesion,
  branding, density, motion, accessibility, and fallback behavior.

### Gate

- Existing source, Python, CTest, QML lint, deterministic build, RPM, and
  release-contract checks pass before visual edits.
- Every v6 result starts as pending or blocked; no v5 result is silently
  promoted.
- `git diff --check` passes.

**Outcome (2026-07-30):** The checkout matched the reviewed baseline exactly
before editing. The canonical v6 authority and `6.0.0-dev` consumers are active,
while the released v5 qualification manifest remains unchanged and historical.
The immutable baseline records the Fedora 44, Plasma/KWin 6.7.3, Qt 6.11.1,
KF6 6.28.0, GCC 16.1.1, CMake 4.3.0 and Python 3.14.6 toolchain; hashes every
v5 evidence file; and contains 19 authentic offscreen captures across Qt,
Plasma, session and artwork layers. All v6 automated results remain `pending`
and unavailable live cases remain specifically `blocked`. The full local gate
passed with 95 Python tests, 18 CTest cases, generator and QML checks,
byte-identical source archives, Fedora 44 RPM/SRPM construction, `rpmlint` and
`git diff --check`. The known standalone KWin QML import-metadata warning
remains an environmental limitation and is not claimed as live qualification.

## Phase 1 — Lock the Kinetic Precision design system

### Objective

Approve a real, render-backed direction before broad implementation.

### Work

- Upgrade `design/tokens.json` to the next schema version.
- Add the surface, accent, outline, typography, and motion roles defined above.
- Add `design/motion-contract.json` for supported surfaces, transitions,
  reduced-motion outcomes, and performance limits.
- Update `DESIGN.md` from Industrial Precision to Kinetic Precision while
  preserving the recognizable graphite/lime identity.
- Generate canonical C++ and QML tokens from one source.
- Produce authentic north-star prototypes:
  - `north-star-qt.png`;
  - `north-star-plasma.png`;
  - `north-star-session.png`;
  - `north-star-tabbox.png`;
  - `north-star-brand-wallpaper.png`;
  - `north-star-motion-storyboard.png`.
- Compare each target against the Phase 0 baseline at actual output size.

### Required visual differences

- Selected rows no longer rely on a broad olive fill.
- Focus is visibly distinct from a primary action.
- Container borders are reduced without losing discoverability.
- Overlay surfaces read above controls and normal surfaces.
- Typography creates hierarchy before lines and boxes are added.
- Lime coverage is visibly reduced outside intentional actions.

### Gate

- Token generation is byte-stable.
- All documented foreground/background pairs pass their contrast threshold.
- Every semantic state has both animated and reduced-motion behavior.
- North-star renders pass the scorecard with no category below 4/5.
- Do not begin mass asset conversion while the target renders still look like
  v5 with only changed colors.

**Outcome (2026-07-30):** Schema v5 locks five graphite surface layers, neutral
selection with a three-pixel lime marker, distinct immediate focus, seven
system-font roles, an eight-percent icon accent ceiling, and canonical semantic
timings and curves. `design/motion-contract.json` gives every interactive state
both bounded animated behavior and a zero-duration reduced-motion outcome; it
forbids idle animation, spring, overshoot, layout-property motion, and animated
focus. Six authentic Qt/QPainter north-star prototypes are byte-stable and
compared to immutable Phase 0 captures at identical output sizes. Their linked
scorecard is 4/5 or better in every category and explicitly records that static
offscreen motion evidence is not live qualification. The temporary
`assetGenerationPalette` preserves later-phase artwork and Plasma SVG outputs,
so Phase 1 does not silently mass-convert production assets. The full local
phase gate passed with 101 Python tests, 18 CTest cases, generated-source and
QML checks, byte-identical source archives, Fedora 44 RPM/SRPM construction,
`rpmlint`, and `git diff --check`.

## Phase 2 — Reforge the brand and wallpaper

### Objective

Give v6 an immediately recognizable first impression without changing package
identity.

### Work

- Refine `design/brand/noxforge-mark.svg`.
- Generate physical mark copies for Splash, Logout, SDDM, and TabBox.
- Create the horizontal wordmark lockup.
- Replace the 16:9 and ultrawide wallpaper source compositions.
- Regenerate the supported raster resolutions and dim session derivative.
- Update the Global Theme preview and README hero from authentic output.
- Extend artwork contracts and optical-size contact sheets.

### Gate

- Mark remains legible at 16, 24, 48, 128, and 512 px.
- Wallpaper outputs are byte-identical across clean generations.
- Independent 16:9 and ultrawide sources are verified; no stretched master.
- Every composition retains a quiet work area.
- All artwork remains original and editable.

**Outcome (2026-07-30):** The refined N/F mark uses one continuous shared
geometry, with editable semantic-lime and monochrome masters plus a
font-independent horizontal vector lockup. Physical mark and lockup copies are
generated for their package consumers, and deterministic optical renders cover
16, 24, 48, 128, and 512 px. Independent original 16:9 and ultrawide
forged-plane compositions preserve declared quiet workspace regions and render
byte-identically at 1920×1080, 2560×1440, 3840×2160, and 3440×1440. The
dim SDDM derivative, Global Theme previews, and README hero are bound to shipped
outputs. The SDDM and Global Theme preview manifest is authentic offscreen
evidence and explicitly not live qualification; its renderer now freezes the
mock clock for reproducibility. Four source-bound artwork contact sheets passed
review. The full local phase gate passed with 106 Python tests, 18 CTest cases,
generator and QML checks, byte-identical source archives, Fedora 44 RPM/SRPM
construction, `rpmlint`, and `git diff --check`.

## Phase 3 — Native Qt visual polish and motion kernel

### Objective

Make Qt Widgets feel responsive and premium while keeping native behavior,
public Qt APIs, and low idle cost.

### Architecture

Add a small internal motion controller, for example:

- `src/style/noxforgemotion.h`;
- `src/style/noxforgemotion.cpp`.

Extend `NoxForgeStyle` with:

- `polish(QWidget *)`;
- `unpolish(QWidget *)`;
- an event filter for supported widgets;
- per-widget hover, focus, press, checked, and busy progress;
- a shared timer that runs only while at least one transition is active;
- automatic cleanup when widgets are destroyed.

Use public Qt/KDE APIs only. Do not use Qt private style animation classes.

### Supported motion scope

Animate color, opacity, indicator position/length, and shallow elevation only
for:

- push buttons and tool buttons;
- tabs;
- checkboxes and radio buttons;
- combo boxes and spin boxes;
- sliders and scrollbars;
- progress bars;
- small focus/selection markers.

Do not animate:

- widget geometry;
- font size or weight;
- large item-view row sets;
- menus through a custom window animation;
- application window movement;
- anything already owned by KWin.

### Visual polish

- Separate focused secondary action from filled primary action.
- Refine input, combo, spin, slider, scrollbar, tab, table/tree header, menu,
  group box, progress, and toolbar hierarchy.
- Reduce repeated full borders in dense data views.
- Give scrollbars a quiet idle state and a precise active state.
- Animate indeterminate progress only while it is genuinely busy.
- Preserve `QCommonStyle` fallback for unsupported controls.
- Preserve LTR/RTL geometry and current hit-testing contracts.

### KDE/Qt policy

- Read and respect the effective KDE animation duration factor.
- Return zero for `SH_Widget_Animation_Duration` when animation is disabled.
- Honor `QStyleHints::useHoverEffects()` where relevant.
- Do not add a separate NoxForge settings daemon or configuration GUI.
- Update RPM dependencies only if a native KF6 library is genuinely required.

### Gate

- Idle motion controller has no active timer and no recurring wakeup.
- Reduced-motion tests prove zero intermediate frames.
- Event tests cover enter, leave, focus, press, release, disable, and destroy.
- Deterministic 0/50/100 percent state renders pass.
- LTR/RTL renders remain distinct and valid at 100/125/140/200 percent.
- CTest, AddressSanitizer, UndefinedBehaviorSanitizer, and existing style probes
  pass.
- Gallery startup and control-render medians remain within 10 percent of the v5
  baseline unless an explicit measurement justifies the difference.

**Outcome (2026-07-30):** `NoxForgeMotion` now provides one shared,
idle-stopping public-Qt timer for hover, immediate focus, press, checked, and
genuine visible busy-progress state. `polish(QWidget *)`, `unpolish(QWidget *)`,
event filtering, destruction cleanup, the effective
`SH_Widget_Animation_Duration`, and `QStyleHints::useHoverEffects()` are covered
without Qt private animation classes. Native control rendering now separates
filled primary actions from focused secondary actions, reduces dense
item/header borders, and refines tabs, inputs, sliders, scrollbars, progress,
menus, groups, and toolbars while preserving the existing LTR/RTL geometry and
hit-testing contracts. Deterministic authentic offscreen renders cover
0/50/100 percent transition states and remain explicitly non-live evidence.
The lifecycle probe covers enter, leave, focus, press, release, disable, busy,
hide, unpolish, destroy, idle, and zero-duration behavior. Interleaved
v5-relative medians passed at 1.0342× gallery startup and 1.0346× control
rendering. The full local phase gate passed with 111 Python tests, 19 CTest
cases, ASan/UBSan probes, generator and QML checks, byte-identical source
archives, Fedora 44 RPM/SRPM construction, `rpmlint`, and
`git diff --check`.

## Phase 4 — Plasma shell material and state refinement

### Objective

Make panel, widgets, popups, notifications, and shell states match the new
material hierarchy.

### Important platform boundary

Plasma Style artwork is SVG-based. V6 must not claim that an SVG color/state
rewrite creates an animation engine. Motion owned by Plasma/KWin remains owned
by Plasma/KWin.

### Work

- Update `design/plasma-semantic-contract.json`.
- Refine generated opaque, solid, and translucent materials.
- Rework:
  - panels and all four edges;
  - tasks and progress states;
  - panel buttons and applet backgrounds;
  - popups and dialogs;
  - notifications;
  - tooltips;
  - calendar and weather surfaces;
  - line edits, sliders, scrollbars, and busy indicators;
  - OSD and containment controls.
- Add a neutral edge highlight and controlled overlay shadow recipe.
- Remove double outlines and dark seams.
- Keep active task markers edge-aware and visually identical in intent.
- Keep solid/opaque output fully usable without compositor blur.

### Gate

- All 43 widget families resolve through the semantic contract.
- No visible Breeze fallback in isolated Plasma captures.
- Complete state/orientation/scale atlas passes at 100/125/140/200 percent.
- All four panel edges, compact layout, and two virtual outputs pass.
- Blur-on and blur-off evidence is recorded separately and honestly.
- Raster/source generation remains deterministic.

**Outcome (2026-07-30):** Plasma semantic contract schema 4 now maps all 43
widget families onto the canonical v6 canvas, sunken, surface, raised, and
overlay hierarchy. Generated panels, task states, panel buttons, applet
backgrounds, popups, dialogs, notifications, tooltips, calendar/weather
artwork, inputs, busy indicators, OSD, and containment controls use quieter
neutral state fills, edge-aware task/tab markers, one neutral edge highlight,
and a controlled filter-free overlay shadow. Opaque and solid variants remain
independent of compositor blur, and no fallback theme is declared. Authentic
generated SVG sources pass deterministic raster comparison across
100/125/140/200 percent; blur-on and blur-off material atlases are committed
separately. The source contract covers four panel edges, standard/compact
layouts, and primary/secondary virtual outputs as 128 static scenarios, while
explicitly stating that this evidence does not qualify a running Plasma shell.
The targeted local gate passed with 116 Python tests. Live compositor blur,
compact-panel, multi-output, and visible-fallback qualification remains
blocked for Phase 7 and is not claimed here. The phase is locally complete
only when the authoritative release check passes on this exact tree before its
single local commit.

## Phase 5 — Signature QML surfaces and choreography

### Objective

Turn the session surfaces into the main v6 showcase while preserving every
runtime contract.

### Shared implementation

- Generate semantic motion tokens into each package.
- Generate shared physical QML components where practical; package symlinks
  remain forbidden.
- Use `Behavior` and explicit `Transition` objects instead of scattered magic
  durations.
- Add test-only deterministic progress injection through the existing render
  tools without changing production behavior.

### Splash

- Rebuild the mark entrance as a short staged reveal.
- Reveal the wordmark after the mark with one small stagger.
- Replace the full-width bottom line with a thinner, intentional progress rail.
- Keep the complete visible sequence under roughly 650 ms at normal settings.
- Reduced motion renders the settled frame immediately.

### SDDM

- Preserve user, password, session, keyboard, power, authentication, error, and
  focus contracts.
- Use an adaptive composition:
  - large displays place the login card against the quiet wallpaper region;
  - small displays center it;
  - ultrawide does not leave the card stranded at the physical center.
- Add a restrained card entrance: opacity plus no more than 8 px of travel.
- Animate focus rail/color, session-list expansion, status replacement, and
  genuine authentication busy state.
- Simplify bottom power actions and improve their relationship to the card.
- Keep stable error space; no layout jump on failure.

### Logout

- Increase the visual authority of the decision surface on large displays.
- Group session actions, power actions, and cancel with clearer hierarchy.
- Add icons only from the existing NoxForge theme.
- Use a scrim plus a short card entrance.
- Animate hover/focus color and marker; do not scale buttons.
- Destructive emphasis appears on hover, focus, or confirmation, not at rest.

### TabBox

- Replace the generic vertical list with a responsive NoxForge switcher.
- Use only model roles actually supplied by KWin.
- Prefer a horizontal rail of compact window cards when space allows.
- Show a larger icon, clear caption, and quiet minimized state.
- Add one animated highlight/Forge rail that moves between items.
- Support long titles, no-window state, many-window scrolling, RTL, keyboard,
  and narrow screens.
- Do not fake live window previews if the model/runtime does not supply them.

### Gate

- QML lint passes for every package in its authentic import environment.
- Start/mid/end frames are deterministic for each surface.
- Four-resolution matrix passes at 1280×720, 1920×1080, 2560×1440, and
  3440×1440.
- Standard, long RTL, keyboard-focus, empty, error, busy, and reduced-motion
  scenarios pass.
- No hard-coded palette values or per-file easing curves appear in runtime QML.
- First-frame median remains within 10 percent of v5.

**Outcome (2026-07-30):** Splash, SDDM, Logout, and TabBox now consume the
canonical v6 motion policy without package symlinks or runtime palette values.
Splash stages the N/F mark, wordmark, and thin progress rail; SDDM preserves
login, session, keyboard, power, focus, stable error, and genuine busy
contracts in an adaptive card; Logout groups authoritative session and power
decisions; and TabBox uses only KWin caption, icon, and minimized roles in a
responsive horizontal or vertical rail. Production test progress remains
disabled at `-1`. The authentic offscreen renderer injects deterministic
start/mid/end progress and records 46 source-bound captures across all four
required resolutions and the standard, long RTL, keyboard, empty, error, busy,
many-window, and reduced-motion scenarios. Repeated drift checks pass. The
SDDM first-frame median is 1.0621 times the reviewed v5 baseline, below the
1.10 limit. The full local phase gate passed with 123 Python tests, 19 CTest
cases, generated-source checks, QML lint, non-mutating install/uninstall
dry-runs, a reproducible source archive, and clean SRPM/RPM `rpmlint`. Real
SDDM authentication and power, production splash integration, injected
keyboard/pointer Logout, and held KWin Alt+Tab remain blocked for Phase 7 and
are not claimed here.

## Phase 6 — Window chrome, icon, and cursor optical polish

### Objective

Finish the desktop edges after the core material and motion language is stable.

### Aurorae

- Refine active/inactive frame separation.
- Use a slim neutral titlebar with one short active lime rail/notch.
- Rebuild minimize, maximize/restore, close, and menu states for optical
  consistency.
- Keep hover/pressed states clear without colored glow.
- Revalidate normal, inactive, maximized, shaded, and every button state.

### Icons

- Freeze the runtime fixture and total coverage unless a real Fedora 44 runtime
  miss is proven.
- Rank the 40–60 most visible icons from panel, System Settings, Dolphin, and
  session flows.
- Reduce internal detail and normalize stroke/negative space in those icons.
- Keep 16/22 px optical variants only where the scalable master is insufficient.
- Recheck semantic distinctions before visual consistency.

### Cursors

- Refine outline weight, hotspot visibility, and lime detail consistency.
- Preserve canonical hotspots, physical 24/32/48 px sizes, and current animated
  cursor timing unless evidence proves a problem.
- Do not add cursor variants for marketing breadth.

### Sound

- Keep the qualified v5 sound theme unchanged unless a visual interaction
  exposes a real semantic mismatch.
- Do not turn v6 into another audio-normalization phase.

### Gate

- Aurorae structural state sheet passes and a live composed decoration is
  captured.
- Top-priority icon contact sheet passes at 16/22/24/32/48 px.
- No unallowlisted semantic duplicate or package symlink is introduced.
- Cursor hotspot, frame count, duration, and scale checks pass.

**Outcome (2026-07-30):** `design/edge-polish-contract.json` freezes the Phase
6 scope. Aurorae now uses a 26 px raised active titlebar, sunken inactive
material, one 12×2 px active lime rail, and six canonical source/compressed
pairs covering decoration plus menu, minimize, maximize, restore, and close.
Every button retains all eight Aurorae states; hover and press are neutral
except for the destructive close glyph, and no glow/filter is used. The
185-icon scalable inventory, 77-name runtime fixture, and 196-file 16/22 px
optical inventory remain unchanged. Fifty-six panel, System Settings, Dolphin,
and session icons are ranked and rendered at 16/22/24/32/48 px; fifteen
formerly fallback-derived high-visibility roles now have simpler
role-specific masters. All 96 physical cursor names preserve canonical
24/32/48 px hotspots plus 12-frame, 80 ms busy timing while using a normalized
1.75 px source outline and canonical canvas fill. The qualified sound tree is
byte-identical and explicitly unchanged. Three deterministic source-bound
optical sheets pass repeated drift checks, and dependent Logout evidence was
regenerated against the new session icons. The full local phase gate passed
with 129 Python tests, 19 CTest cases, generated-source checks, QML lint,
non-mutating install/uninstall dry-runs, a reproducible source archive, and
clean SRPM/RPM `rpmlint`. A composed active/inactive/maximized/shaded KWin
decoration and live cursor scaling remain blocked for Phase 7 under the
explicit no-live boundary and are not claimed here.

## Phase 7 — Accessibility, performance, and real motion qualification

### Objective

Prove that the visual upgrade works in motion, not only in static offscreen
renders.

### Automated qualification

- Full release gate.
- Contrast and non-color state indicators.
- System-font behavior.
- Keyboard traversal and focus.
- RTL.
- 100/125/140/200 percent scale.
- Reduced motion at zero duration.
- High-contrast preference where the Qt platform exposes it.
- ASan/UBSan.
- Deterministic sources and evidence.
- Idle wakeup and active animation performance.

### Required live qualification

Use a disposable Fedora KDE 44 Plasma 6.7+ Wayland session with real or injected
pointer and keyboard input.

Verify:

1. Qt hover, focus, press, toggle, slider, scrollbar, and busy transitions.
2. No stale animation state after a widget closes or becomes disabled.
3. Plasma panel/tasks/popups/notifications with blur available and unavailable.
4. SDDM test mode, session list, field focus, busy, error, and power states.
5. Logout keyboard and pointer flow.
6. Held Alt+Tab with one, many, long-title, minimized, and empty scenarios.
7. Aurorae active/inactive/maximized and button hover/press.
8. Global animation speed set to instant, normal, and slow.
9. 100 and 140 percent composition and two-output placement.

Motion cannot be declared complete using only start/end screenshots.

### Performance budget

- No recurring timer while the desktop is idle.
- No animation-triggered memory growth across 500 repeated transitions.
- No failed frame or input case.
- Startup, control rendering, and QML first-frame medians remain within 10
  percent of v5.
- Active transitions remain responsive under the gallery stress surface.

### Gate

- No failed automated or live case.
- Any unavailable case remains `blocked` with a specific environmental reason.
- Static evidence is never relabeled as interactive evidence.
- Active desktop, panel layout, and SDDM configuration remain unchanged.

**Outcome (2026-07-30):** The automated Phase 7 qualification is complete
without installing or applying NoxForge. A v6-specific accessibility report
passes all 15 contrast pairs, non-color semantic indicators, KDE system-font
behavior, keyboard structure, RTL, 100/125/140/200 percent coverage, and
zero-duration reduced motion. Qt 6.11's offscreen accessibility API reported
`NoPreference`; live high-contrast mode is therefore not claimed. Complete-tree
performance medians for gallery startup, control rendering, and SDDM first
frame are respectively 1.0138, 1.0199, and 1.0270 times the immutable reviewed
v5 baseline, within the 1.10 ceiling. A sanitizer-covered native probe completes
500 input and animation cycles with zero failed cases, no retained widgets, a
stopped idle timer, and zero measured heap growth after warmup. The full local
gate passed with 135 Python tests, 21 CTest cases, ASan/UBSan, deterministic
evidence, QML lint, non-mutating install/uninstall dry-runs, byte-identical
source archives, and clean Fedora SRPM/RPM `rpmlint`. The isolated Wayland
follow-up on 2026-08-01 passed Global Theme application, exact panel
preservation, all four panel edges, two-output placement, visible shell
fallback review, and real Qt composition at 140 percent. The real windowed
Logout greeter, composed Aurorae, and SDDM test mode rendered and are retained
with bounded claims. Hardware blur, input-injected motion, held Alt+Tab,
cursor scaling, production splash integration, high-contrast mode, PAM
authentication, and real SDDM power actions remain `blocked` with specific
environmental reasons. The active desktop, panel, theme, and SDDM
configuration hashes were unchanged.

## Phase 8 — Product presentation and controlled 6.0.0 release

### Objective

Present v6 as a coherent product and publish through the proven v5 pipeline.

### Work

- Replace README's opening section with:
  - one authentic desktop hero;
  - a concise Kinetic Precision statement;
  - four focused images for applications, shell, sessions, and details;
  - compatibility, install, rollback, and reduced-motion notes.
- Update Global Theme preview, release notes, compatibility, manual testing,
  troubleshooting, and screenshots from exact v6 output.
- Promote all version consumers to `6.0.0`.
- Qualify the exact annotated tag.
- Reuse the exact-provenance GitHub Release and COPR process.
- Keep the existing compact artifact contract unless a separate approved change
  justifies another public asset.
- Independently download, checksum, install, inspect, and remove the released
  RPM without applying the theme.

### Gate

- GitHub tag, assets, checksums, source archive, SRPM, RPM, qualification
  manifest, and automated report all name one exact commit.
- COPR build reaches terminal success and the package is independently
  available.
- `rpm -V`, `noxforge-doctor`, installation, and removal pass.
- KDE and SDDM settings hashes remain unchanged before install, after install,
  and after removal.
- README screenshots come from the released build.

**Publication status (2026-08-02; complete):** The v6 release source and all
stable version consumers are `6.0.0`. README, Global
Theme previews, release notes, compatibility, installation, rollback,
reduced-motion, troubleshooting, and manual-testing documentation now present
Kinetic Precision using exact generated or authentic offscreen v6 outputs.
Every non-live image is labeled honestly; no fabricated live desktop screenshot
is used. The compact six-asset release contract is preserved, and the complete
stable local gate passes with 141 Python tests, 21 CTest cases, ASan/UBSan,
QML lint, deterministic evidence, non-mutating install/uninstall dry-runs,
byte-identical source archives, and clean Fedora SRPM/RPM `rpmlint`. The
release qualification manifest now records exact candidate lineage, a clean
worktree, the six-asset contract, and the isolated Wayland result.

PR #10 merged the qualified candidate after all required checks passed in CI
run `30691626413`. Annotated tag `v6.0.0` resolves to
`d6c4e3c5584b9fdd61c7bb3ae9b3b693f03e67f6`. Release workflow run
`30692016393` rebuilt that exact tag, passed the full Fedora 44 gate, verified
the commit/ref-bound payload, and published exactly six assets. A fresh public
download passed every `SHA256SUMS` entry and confirmed the source archive,
SRPM, `noxforge-6.0.0-1.fc44.x86_64.rpm`, qualification manifest, and automated
report all name the exact release lineage. A disposable Fedora 44 installation
of the released RPM passed
`rpm -V` and `noxforge-doctor` with all eleven components present and no mixed
versions. Removal with `dnf remove --no-autoremove` removed only NoxForge; KDE
and SDDM sentinel hashes remained identical before installation, after
installation, and after removal. COPR build `10802161` reached terminal
`succeeded` at `2026-08-01T12:51:55Z`, and the public Fedora 44 x86_64
repository resolves `noxforge-6.0.0-1.fc44`. Phase 8 public release closure is
complete. The environment-blocked physical/input live cases remain documented
release limitations and were not relabeled as passed.

## Cross-phase file map

| Area | Primary files |
| --- | --- |
| Authority | `docs/IMPLEMENTATION_PLAN.md`, `docs/NOXFORGE_V6_PLAN.md`, `VERSION` |
| Design system | `DESIGN.md`, `design/tokens.json`, `design/motion-contract.json`, `scripts/generate_design_system.py` |
| Qt style | `src/style/noxforgestyle.{h,cpp}`, new motion controller files, `src/style/noxforgepalette.h` |
| Qt evidence | `tools/widget_gallery.cpp`, `tests/qt/style_probe.cpp`, `scripts/render_evidence.py` |
| Plasma | `design/plasma-semantic-contract.json`, `scripts/generate_plasma_svgs.py`, `plasma/desktoptheme/...` |
| Brand | `design/brand/noxforge-mark.svg`, generated physical mark copies |
| Wallpaper | `wallpapers/NoxForge/contents/source/*.svg`, `scripts/render_wallpaper.py` |
| Session QML | `sddm/NoxForge/Main.qml`, Splash, Logout, TabBox `Switcher.qml` and generated tokens |
| Session evidence | `scripts/render_session_evidence.py`, `tools/session_renderer.cpp`, `tools/sddm_renderer.cpp` |
| Window chrome | `aurorae/io.github.loofiboss.noxforge.desktop/` |
| Icons/cursors | existing coverage manifests and generation scripts; no unproven count expansion |
| Qualification | `docs/evidence/v6/`, accessibility/performance/live scripts and tests |
| Release | existing CI/release workflows and RPM spec, changed only where v6 requires it |

## Permanent constraints

- Fedora KDE 44, Plasma/KWin 6.7+, Qt 6.11, and Wayland remain the target.
- Plasma 5, Qt 5, Light, OLED, and arbitrary color variants remain out of scope.
- Public package IDs, paths, `NoxForge` name, and installation semantics remain
  stable.
- Installation never applies the theme, changes panels, changes SDDM,
  restarts Plasma, or edits the active desktop.
- User-local installation remains available and reversible.
- No Kvantum requirement.
- No GTK theme in v6.
- No third-party KWin effect, widget, compositor shader, or dynamic wallpaper.
- No private lock-screen replacement.
- No GUI installer or settings daemon.
- No mass icon expansion.
- No copied theme artwork or SVG paths.
- No package symlinks.
- No fake window previews or illustrative screenshots presented as real output.
- No push, tag, release, COPR action, installation, or desktop-setting change
  without explicit authorization.
- Existing unrelated worktree changes are preserved.
- Code, comments, documentation, filenames, commits, and release text remain in
  English.

## Definition of done

V6 is complete only when:

- the current v5 identity is visibly evolved rather than recolored;
- the static and animated state hierarchy is consistent across Qt, Plasma,
  QML, Aurorae, icons, cursors, wallpaper, and brand;
- focus, selected, checked, primary, busy, error, and disabled states cannot be
  confused;
- reduced motion is fully functional;
- Qt motion uses no idle timer and no private APIs;
- Plasma SVG surfaces make no false animation claim;
- real interactive motion is qualified in disposable Wayland;
- every supported scale, RTL, keyboard, and contrast gate passes;
- no existing installation, packaging, release, rollback, or provenance
  guarantee regresses;
- the exact released build produces the README and evidence images;
- the result looks like one original desktop product, not a bundle of themed
  parts.

## Recommended Codex execution contract

Use **Goal mode** with this file as the release authority.

Codex should:

1. inspect the repository and confirm that the reviewed baseline still matches;
2. execute one phase at a time;
3. run each phase gate before committing;
4. create one narrow local commit per completed phase;
5. stop on a failed gate instead of weakening the contract;
6. keep unavailable graphical checks blocked and explicit;
7. avoid push, tag, publication, installation, or desktop mutation without a
   separate user instruction.

Suggested opening instruction:

> Implement NoxForge 6.0.0 “Kinetic Precision” using
> `NOXFORGE_V6_KINETIC_PRECISION_PLAN.md` as the complete release authority.
> First reconcile it into `docs/NOXFORGE_V6_PLAN.md`, verify the exact current
> baseline, and execute the phases in order. Preserve all repository
> instructions and permanent constraints. Make small, reviewable changes, run
> every phase gate, and create at most one local commit per completed phase.
> Do not push, tag, publish, install, apply the theme, alter the desktop or SDDM,
> or claim unavailable live checks. If the repository has materially diverged
> from the reviewed baseline, stop and report the mismatch before editing.
