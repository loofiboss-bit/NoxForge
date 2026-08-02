# Artwork inventory and provenance

All shipped visual assets are original NoxForge project work and are licensed
under the repository's MIT License. No artwork from Breeze or another theme is
included. Installed KDE assets and upstream documentation were inspected only
for package layout and required identifiers.

The original wallpaper direction was explored with an OpenAI-generated concept
using the locked NoxForge palette. The concept image is not shipped. The final
wallpapers were authored separately as project-owned vector geometry:
`NoxForge.svg` is the 16:9 composition and `NoxForge-Ultrawide.svg` is an
independent panoramic composition rather than a stretched crop. They render
deterministically to 1920x1080, 2560x1440, 3840x2160, and 3440x1440 release
images. SDDM
uses a deterministically dimmed 16:9 derivative, while its preview is captured
from the real QML surface with mock runtime models.

The Kinetic Precision N/F mark is authored as editable semantic and monochrome
SVG masters with one continuous N-to-F geometry. A separate horizontal lockup
uses vector paths rather than a bundled or forced font. Generated physical
copies are committed for Splash, Logout, SDDM, and TabBox, and optical review
covers 16, 24, 48, 128, and 512 pixels.

The Aurorae decoration and all system icon SVGs are emitted from original geometry
in `scripts/generate_visual_assets.py`. Their generated SVG files are committed
so they can be inspected, edited, installed, and validated without network
access.

## Icon, cursor and sound coverage

`design/artwork-contract.json` fixes the Fedora KDE 44, Plasma 6.7 and System
Settings 6.7 runtime fixture used by the generated icon manifest. The 193
scalable icons cover actions, applets, categories, devices, emblems, MIME
types, places, preferences and status names. The 212 physical 16/22 px optical
variants are limited to dense action, applet and status contexts. Canonical
original glyph families are reused only for genuine semantic synonyms; broader
related names receive a deterministic optical discriminator. No symlinks or
artwork from another theme are used. The explicit Fedora overlay chain is
`breeze-dark,breeze,hicolor`, so third-party applications retain their own
product icons when NoxForge does not own a matching name.

The NoxForge cursor generator writes original 24, 32 and 48 pixel Xcursor image
chunks plus physical alias files. Its manifest records and validates every
canonical hotspot. Wait and progress contain twelve 80 ms frames at each size.
Canonical cursor SVG sources match their corresponding distinct glyph geometry.
The sound generator synthesizes editable WAV masters, normalizes ordinary
events to -23 dBFS RMS and the alarm to -20 dBFS RMS under a -3 dBFS peak
ceiling, and emits Ogg/Vorbis events. Cross-toolchain reproducibility is bound
to byte-identical WAV masters, coverage metrics, and valid Ogg containers. Ogg
byte equality is additionally required in the pinned Fedora release environment
with FFmpeg 8.1.2. A different host encoder may validate the canonical
PCM/source contract but must never be used to overwrite the committed sound
tree blindly. Duration and frequency signatures keep each of the ten semantic
source sounds distinct.

The reviewed v6 Phase 2 evidence is committed as four deterministic contact
sheets and `docs/evidence/artwork-contact-sheets.json`. The manifest binds
contract, source, coverage and sheet hashes; these are structural/offscreen
artwork reviews and do not claim live Plasma or cursor interaction.
