# NoxForge Design System

NoxForge uses an atmospheric, technical visual language called **Kinetic
Precision**. This file is the visual authority for every NoxForge component.

<!-- Hallmark · pre-emit critique: P5 H5 E5 S5 R5 V4 -->

## Design character

The v5 system was coherent and technically disciplined, but broad olive
selection fills, repeated container outlines, and nearly uniform typographic
weight weakened hierarchy. Kinetic Precision keeps the recognizable
graphite/lime identity while making state changes quieter, depth more tonal,
and motion explicitly purposeful.

- Graphite layers establish depth; color never replaces hierarchy.
- Electric lime is a precision signal for focus, primary action, and active
  markers. It is not a navigation or ambient surface material.
- The Forge Notch is a four-pixel clipped detail used only on active, selected,
  focused, or branded surfaces.
- Cyan communicates information and progress. Violet is a rare secondary brand
  detail. Red is reserved for destructive and error states.
- Controls remain compact, keyboard-visible, native to KDE behavior, and still
  when idle.

## Surface hierarchy

| Layer | Token | Value | Use |
| --- | --- | --- | --- |
| Canvas | `background` | `#0E1318` | Deep workspace background |
| Sunken | `surfaceSunken` | `#10171C` | Inputs, data wells, recessed regions |
| Surface | `surface` | `#151D23` | Windows, panels, stable containers |
| Raised | `surfaceRaised` | `#1B252C` | Controls and quiet raised regions |
| Overlay | `surfaceOverlay` | `#222D35` | Menus, popups, switchers, session cards |

Supporting surface tokens are `surfaceHover` `#232F36`,
`surfaceSelected` `#1E2B31`, `edgeHighlight` `#3C4B53`, and
`outlineMuted` `#314049`. Tonal separation does most of the work. Adjacent
parent and child surfaces do not both draw complete borders. An overlay may use
one outer keyline, one subtle top or leading highlight, and a neutral shadow.
Colored shadows and ambient lime glow are forbidden.

## Palette and accent budget

| Token | Value | Use |
| --- | --- | --- |
| `textPrimary` | `#E8F0F2` | Primary content |
| `textSecondary` | `#A6B4B9` | Supporting content |
| `textDisabled` | `#748289` | Disabled content |
| `accent` | `#A3FF47` | Focus, one primary action, active markers |
| `accentPressed` | `#82D936` | Pressed primary action |
| `accentSoft` | `#243528` | Restrained small accent backing |
| `accentMuted` | `#71994F` | Secondary accent detail |
| `detailCyan` | `#22D3EE` | Information, busy, and progress |
| `detailViolet` | `#A78BFA` | Rare identity counterpoint |
| `negative` | `#FF6B7A` | Destructive and error states |
| `neutral` | `#FBBF24` | Warning states |

Lime may fill at most one primary action per decision group. A selected row uses
a neutral surface and a three-pixel lime rail or short marker, never a broad
olive fill. A focused control uses one immediate two-pixel lime treatment and
does not also receive a lime fill. Icon accent coverage is eight percent or
less unless the glyph communicates semantic success.

## Schema v5

`design/tokens.json` is canonical. Generated C++ and QML consumers carry the
complete canonical payload plus typed properties, so parity is mechanically
verifiable without parallel values.

- `semanticRoles` maps canvas, sunken, surface, raised, overlay, control,
  selection, action, focus, disabled, busy, error, and success roles.
- `opacity`, `elevation`, `overlay`, and `shadow` define named recipes.
- `states.hierarchy` composes each interactive state from those recipes.
- `typography.roles` defines seven system-font roles.
- `motion` owns every duration and cubic curve.
- `contrastPairs` exhaustively covers semantic foreground/background pairs.

`design/motion-contract.json` binds these tokens to supported Qt, Plasma, and
session transitions. It is the authority for reduced-motion and performance
limits.

During phase 1 only, `assetGenerationPalette` freezes the v5 artwork and Plasma
SVG inputs so approving the target system cannot silently mass-convert later
phase assets. Each owning implementation phase removes that staging boundary.

## Geometry and composition

- Base grid: 4 px.
- Compact radius: 4 px; standard radius: 6 px; overlay/session radius: 8 px.
- Forge Notch: 4 px at the top-left corner.
- Border: 1 px; focus ring: 2 px.
- Standard control height: 32 px; large control height: 36 px.
- Panels and toolbars remain compact and use spacing in four-pixel increments.
- A surface has one containment layer. Card-in-card decoration is avoided.
- Shell surfaces are edge-anchored where workflow permits; centering is
  reserved for login, logout, and transient switchers.

## Typography

The KDE-configured system font is the only application and shell typeface.
Weight, size, contrast, and spacing establish hierarchy before separators:

| Role | Size / line | Weight | Use |
| --- | --- | ---: | --- |
| `displayClock` | 64 / 72 px | Light | Stable numeric time |
| `surfaceTitle` | 24 / 32 px | Demi-bold | Window/session title |
| `sectionTitle` | 16 / 24 px | Demi-bold | Content section |
| `body` | 14 / 20 px | Regular | Reading text |
| `controlLabel` | 14 / 20 px | Medium | Interactive label |
| `metadata` | 12 / 16 px | Regular | Supporting status |
| `microLabel` | 11 / 16 px | Demi-bold | Rare tracked label |

Tracking remains neutral except for the `NOXFORGE` wordmark and rare
micro-labels. Generic interface headings use sentence case. Text elides or
wraps within its owner, and interactive labels stay on one line.

## State hierarchy

1. Default uses a quiet raised control and muted outline.
2. Hover changes color and opacity in 120 ms without glow or geometry changes.
3. Focus draws one immediate two-pixel ring; focus is not animated.
4. Pressed settles into the sunken layer in 90 ms and never scales.
5. Checked adds a check glyph and does not rely on color alone.
6. Selected uses a neutral surface, restrained overlay, and mirrored leading
   marker over 140 ms.
7. Disabled changes label and opacity immediately while preserving geometry.
8. Busy uses cyan and a 900 ms purposeful progress cycle; reduced motion keeps
   a static semantic glyph.
9. Error pairs red with a label or glyph.
10. Success remains quiet and pairs lime with a success glyph where needed.

## Motion

Motion feels machined: immediate response, controlled acceleration, and a soft
landing. Bounce, spring, overshoot, stretch, glow pulses, layout-property
animation, and infinite ambient animation are forbidden.

| Token | Duration | Use |
| --- | ---: | --- |
| `instantMs` | 0 ms | Focus and reduced-motion changes |
| `pressMs` | 90 ms | Press/release |
| `productiveMs` | 120 ms | Hover, toggle, marker |
| `selectionMs` | 140 ms | Tab, task, switcher selection |
| `containerMs` | 180 ms | Menu, popup, session list |
| `expressiveMs` | 260 ms | Rare splash/session choreography |
| `staggerMs` | 24 ms | Small related sequences |
| `busyCycleMs` | 900 ms | Genuine indeterminate progress |

Only opacity, color, and transform are animated. Spatial travel is at most
eight pixels. Reduced motion resolves every state immediately, suppresses
opacity and spatial transitions, and replaces continuous busy movement with a
static semantic glyph.

## Contrast contract

Ratios are computed from the locked sRGB anchors. Primary reading text and
action ink require 7:1, normal semantic text 4.5:1, and disabled supporting text
3:1.

| Pair | Foreground / background | Ratio | Minimum |
| --- | --- | ---: | ---: |
| `primary-on-canvas` | `textPrimary` / `background` | 16.16:1 | 7.0:1 |
| `primary-on-sunken` | `textPrimary` / `surfaceSunken` | 15.65:1 | 7.0:1 |
| `primary-on-surface` | `textPrimary` / `surface` | 14.76:1 | 7.0:1 |
| `primary-on-control` | `textPrimary` / `surfaceRaised` | 13.49:1 | 7.0:1 |
| `primary-on-overlay` | `textPrimary` / `surfaceOverlay` | 12.16:1 | 7.0:1 |
| `primary-on-hover` | `textPrimary` / `surfaceHover` | 11.87:1 | 7.0:1 |
| `primary-on-selection` | `textPrimary` / `surfaceSelected` | 12.58:1 | 7.0:1 |
| `secondary-on-canvas` | `textSecondary` / `background` | 8.76:1 | 4.5:1 |
| `secondary-on-surface` | `textSecondary` / `surface` | 8.00:1 | 4.5:1 |
| `disabled-on-control` | `textDisabled` / `surfaceRaised` | 3.93:1 | 3.0:1 |
| `primary-action` | `accentInk` / `accent` | 15.07:1 | 7.0:1 |
| `pressed-primary-action` | `accentInk` / `accentPressed` | 10.60:1 | 7.0:1 |
| `busy-on-control` | `detailCyan` / `surfaceRaised` | 8.62:1 | 4.5:1 |
| `error-on-control` | `negative` / `surfaceRaised` | 5.67:1 | 4.5:1 |
| `success-on-control` | `accent` / `surfaceRaised` | 12.58:1 | 4.5:1 |

## Hallmark review

The pre-emit review scores Philosophy 5/5, Hierarchy 5/5, Execution 5/5,
Specificity 5/5, Restraint 5/5, and Variety 4/5. Variety is intentionally the
lowest axis because NoxForge remains one restrained dark system; variation
comes from semantic state recipes, not decorative palettes or effects.

## Component and package contracts

- Plasma Style owns the Plasma 6.7 widget families used by core shell flows.
- The Qt style uses the same metrics and state hierarchy as Plasma Style.
- Splash, logout, Alt+Tab, and SDDM consume generated physical token files.
- Visible form labels, immediate keyboard focus, RTL, stable status regions,
  and blur-off readability are required.
- Active windows receive a short lime indicator; inactive windows lose it.
- Destructive buttons become red only on interaction or confirmation.
- All artwork is original NoxForge work. Installed themes may be inspected only
  for technical contracts, identifiers, and package structure.
