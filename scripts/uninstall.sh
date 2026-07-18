#!/usr/bin/env bash
set -euo pipefail

theme_id="io.github.loofiboss.noxforge.desktop"
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
    printf 'Refusing uninstall without explicit --user mode.\n' >&2
    exit 2
fi

data_home=${XDG_DATA_HOME:-${HOME}/.local/share}
if [[ "${data_home}" != /* || "${data_home}" == "/" ]]; then
    printf 'XDG_DATA_HOME must be a safe absolute path.\n' >&2
    exit 2
fi

targets=(
    "${data_home}/color-schemes/NoxForgeDark.colors"
    "${data_home}/plasma/desktoptheme/${theme_id}"
    "${data_home}/aurorae/themes/${theme_id}"
    "${data_home}/icons/NoxForge"
    "${data_home}/wallpapers/NoxForge"
)

for target in "${targets[@]}"; do
    case "${target}" in
        "${data_home}/"*) ;;
        *) printf 'Refusing unsafe uninstall target: %s\n' "${target}" >&2; exit 1 ;;
    esac
    if [[ "${dry_run}" == true ]]; then
        printf 'Would remove %s\n' "${target}"
    elif [[ -d "${target}" ]]; then
        rm -rf -- "${target}"
    elif [[ -e "${target}" ]]; then
        rm -f -- "${target}"
    fi
done

if [[ "${dry_run}" == true ]]; then
    printf 'Dry run complete; no files or settings were changed.\n'
else
    printf 'Removed only NoxForge-owned paths. KDE settings were not changed.\n'
fi
