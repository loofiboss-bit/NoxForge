#!/usr/bin/env bash
set -euo pipefail

theme_id="io.github.loofiboss.noxforge.desktop"
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
source_root=$(cd -- "${script_dir}/.." && pwd)
dry_run=false
user_mode=false

usage() {
    printf 'Usage: %s --user [--dry-run]\n' "${0##*/}"
}

for argument in "$@"; do
    case "${argument}" in
        --user) user_mode=true ;;
        --dry-run) dry_run=true ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'Unknown argument: %s\n' "${argument}" >&2; usage >&2; exit 2 ;;
    esac
done

if [[ "${user_mode}" != true ]]; then
    printf 'Refusing installation without explicit --user mode.\n' >&2
    exit 2
fi

data_home=${XDG_DATA_HOME:-${HOME}/.local/share}
if [[ "${data_home}" != /* ]]; then
    printf 'XDG_DATA_HOME must be an absolute path.\n' >&2
    exit 2
fi

sources=(
    "color-schemes/NoxForgeDark.colors"
    "plasma/desktoptheme/${theme_id}"
    "aurorae/${theme_id}"
    "icons/NoxForge"
    "cursors/NoxForge-Cursors"
    "sounds/NoxForge"
    "look-and-feel/${theme_id}"
    "kwin/tabbox/${theme_id}"
    "wallpapers/NoxForge"
)
targets=(
    "${data_home}/color-schemes/NoxForgeDark.colors"
    "${data_home}/plasma/desktoptheme/${theme_id}"
    "${data_home}/aurorae/themes/${theme_id}"
    "${data_home}/icons/NoxForge"
    "${data_home}/icons/NoxForge-Cursors"
    "${data_home}/sounds/NoxForge"
    "${data_home}/plasma/look-and-feel/${theme_id}"
    "${data_home}/kwin/tabbox/${theme_id}"
    "${data_home}/wallpapers/NoxForge"
)

for source in "${sources[@]}"; do
    if [[ ! -e "${source_root}/${source}" ]]; then
        printf 'Missing source component: %s\n' "${source}" >&2
        exit 1
    fi
    if [[ -d "${source_root}/${source}" ]] && find "${source_root}/${source}" -type l -print -quit | grep -q .; then
        printf 'Refusing package with symlinks: %s\n' "${source}" >&2
        exit 1
    fi
done

for index in "${!sources[@]}"; do
    source="${source_root}/${sources[index]}"
    target="${targets[index]}"
    if [[ "${dry_run}" == true ]]; then
        printf 'Would install %s -> %s\n' "${source}" "${target}"
        continue
    fi
    if [[ -d "${source}" ]]; then
        install -d -m 0755 "${target}"
        cp -a -- "${source}/." "${target}/"
    else
        install -D -m 0644 "${source}" "${target}"
    fi
done

if [[ "${dry_run}" == true ]]; then
    printf 'Dry run complete; no files or settings were changed.\n'
else
    printf 'Installed NoxForge for the current user. No KDE settings were changed.\n'
fi
