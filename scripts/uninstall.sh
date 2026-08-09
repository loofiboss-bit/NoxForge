#!/usr/bin/env bash
set -euo pipefail

user_mode=false
dry_run=false
usage() { printf 'Usage: %s --user [--dry-run]\n' "${0##*/}"; }
for argument in "$@"; do
    case "${argument}" in
        --user) user_mode=true ;;
        --dry-run) dry_run=true ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'Unknown argument: %s\n' "${argument}" >&2; usage >&2; exit 2 ;;
    esac
done
if [[ "${user_mode}" != true ]]; then
    printf 'Refusing uninstall without explicit --user mode.\n' >&2
    exit 2
fi
data_home=${XDG_DATA_HOME:-${HOME}/.local/share}
if [[ "${data_home}" != /* || "${data_home}" == "/" ]]; then
    printf 'XDG_DATA_HOME must be a safe absolute path.\n' >&2
    exit 2
fi

owned_manifest="${data_home}/noxforge/.owned-files"
declare -a targets=()
if [[ -f "${owned_manifest}" ]]; then
    while IFS= read -r relative; do
        [[ -n "${relative}" && "${relative}" != /* && "${relative}" != *..* ]] || continue
        targets+=("${data_home}/${relative}")
    done < "${owned_manifest}"
else
    targets=(
        "${data_home}/color-schemes/NoxForgeDark.colors"
        "${data_home}/plasma/desktoptheme/io.github.loofiboss.noxforge.desktop"
        "${data_home}/aurorae/themes/io.github.loofiboss.noxforge.desktop"
        "${data_home}/icons/NoxForge"
        "${data_home}/icons/NoxForge-Cursors"
        "${data_home}/sounds/NoxForge"
        "${data_home}/plasma/look-and-feel/io.github.loofiboss.noxforge.desktop"
        "${data_home}/kwin/tabbox/io.github.loofiboss.noxforge.desktop"
        "${data_home}/wallpapers/NoxForge"
        "${data_home}/wallpapers/NoxForge-Quiet"
        "${data_home}/wallpapers/NoxForge-Ultrawide"
    )
fi

for target in "${targets[@]}"; do
    case "${target}" in
        "${data_home}/"*) ;;
        *) printf 'Refusing unsafe uninstall target: %s\n' "${target}" >&2; exit 1 ;;
    esac
    target_real=$(realpath -m -- "${target}")
    data_real=$(realpath -m -- "${data_home}")
    case "${target_real}" in
        "${data_real}/"*) ;;
        *) printf 'Refusing symlink-escaped uninstall target: %s\n' "${target}" >&2; exit 1 ;;
    esac
    if [[ "${dry_run}" == true ]]; then
        printf 'Would remove %s\n' "${target}"
    elif [[ -d "${target}" ]]; then
        # A manifest normally names files.  The finite legacy fallback may
        # name directories; remove only files beneath those known roots and
        # retain unrelated sentinel files.
        find "${target}" -type f -delete
        find "${target}" -depth -type d -empty -delete
    elif [[ -e "${target}" ]]; then
        rm -f -- "${target}"
    fi
done
if [[ "${dry_run}" == true ]]; then
    printf 'Dry run complete; no files or settings were changed.\n'
else
    # A manifest names files for precision.  Remove only empty directories
    # beneath the known component roots afterwards; unrelated files and
    # non-empty directories remain untouched.
    cleanup_roots=(
        "${data_home}/noxforge"
        "${data_home}/color-schemes"
        "${data_home}/plasma/desktoptheme/io.github.loofiboss.noxforge.desktop"
        "${data_home}/plasma/look-and-feel/io.github.loofiboss.noxforge.desktop"
        "${data_home}/aurorae/themes/io.github.loofiboss.noxforge.desktop"
        "${data_home}/icons/NoxForge"
        "${data_home}/icons/NoxForge-Cursors"
        "${data_home}/sounds/NoxForge"
        "${data_home}/kwin/tabbox/io.github.loofiboss.noxforge.desktop"
        "${data_home}/wallpapers/NoxForge"
        "${data_home}/wallpapers/NoxForge-Quiet"
        "${data_home}/wallpapers/NoxForge-Ultrawide"
    )
    for root in "${cleanup_roots[@]}"; do
        [[ -d "${root}" ]] || continue
        find "${root}" -depth -type d -empty -delete
    done
    find "${data_home}/noxforge" -depth -type d -empty -delete 2>/dev/null || true
    printf 'Removed only NoxForge-owned paths. KDE settings were not changed.\n'
fi
