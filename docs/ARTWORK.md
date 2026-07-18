# Artwork inventory and provenance

All shipped visual assets are original NoxForge project work and are licensed
under the repository's MIT License. No artwork from Breeze or another theme is
included. Installed KDE assets and upstream documentation were inspected only
for package layout and required identifiers.

The wallpaper composition was explored with an OpenAI-generated concept using
the locked NoxForge palette. The concept image is not shipped. The final
wallpaper was authored separately as editable project-owned vector geometry in
`wallpapers/NoxForge/contents/source/NoxForge.svg` and is deterministically
rendered to 2560x1440, 3840x2160, and 3440x1440 release images. SDDM uses a
deterministically dimmed derivative, while its preview is captured from the
real QML surface with mock runtime models.

The Aurorae decoration and all system icon SVGs are emitted from original geometry
in `scripts/generate_visual_assets.py`. Their generated SVG files are committed
so they can be inspected, edited, installed, and validated without network
access.

## Icon, cursor and sound coverage

The generated icon manifest covers KDE actions, applets, categories, devices,
emblems, MIME types, places, preferences and status names. Canonical original
glyph families are reused for semantic aliases by writing physical SVG files;
no symlinks or artwork from another theme are used. Only `hicolor` is inherited
so third-party applications retain their own product icons.

The NoxForge cursor generator writes original 24, 32 and 48 pixel Xcursor image
chunks plus physical alias files. Wait and progress contain twelve 80 ms frames
at each size. Canonical cursor SVG sources match their corresponding distinct
glyph geometry. The sound generator synthesizes editable WAV
masters and deterministic Ogg/Vorbis event files from project-owned waveforms.
