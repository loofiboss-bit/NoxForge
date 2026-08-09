#!/usr/bin/env bash
set -euo pipefail

user_mode=false
dry_run=false
migrate=false
usage() { printf 'Usage: %s --user [--dry-run] [--migrate]\n' "${0##*/}"; }
for argument in "$@"; do
    case "${argument}" in
        --user) user_mode=true ;;
        --dry-run) dry_run=true ;;
        --migrate) migrate=true ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'Unknown argument: %s\n' "${argument}" >&2; usage >&2; exit 2 ;;
    esac
done
if [[ "${user_mode}" != true ]]; then
    printf 'Refusing installation without explicit --user mode.\n' >&2
    exit 2
fi

data_home=${XDG_DATA_HOME:-${HOME}/.local/share}
if [[ "${data_home}" != /* || "${data_home}" == "/" ]]; then
    printf 'XDG_DATA_HOME must be a safe absolute path.\n' >&2
    exit 2
fi
source_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
portable_root="${source_root}"
has_bundle=false
[[ -d "${source_root}/components" ]] && has_bundle=true

declare -a source_paths target_paths
add_component() {
    source_paths+=("$1")
    target_paths+=("$2")
}
if [[ "${has_bundle}" == true ]]; then
    add_component "components/global-theme" "plasma/look-and-feel/io.github.loofiboss.noxforge.desktop"
    add_component "components/plasma-style" "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop"
    add_component "components/colors/NoxForgeDark.colors" "color-schemes/NoxForgeDark.colors"
    add_component "components/aurorae/io.github.loofiboss.noxforge.desktop" "aurorae/themes/io.github.loofiboss.noxforge.desktop"
    add_component "components/icons/NoxForge" "icons/NoxForge"
    add_component "components/cursors/NoxForge-Cursors" "icons/NoxForge-Cursors"
    add_component "components/kwin-switcher" "kwin/tabbox/io.github.loofiboss.noxforge.desktop"
    add_component "components/sounds/NoxForge" "sounds/NoxForge"
    add_component "components/wallpapers/NoxForge" "wallpapers/NoxForge"
    add_component "components/wallpapers/NoxForge-Quiet" "wallpapers/NoxForge-Quiet"
    add_component "components/wallpapers/NoxForge-Ultrawide" "wallpapers/NoxForge-Ultrawide"
else
    add_component "color-schemes/NoxForgeDark.colors" "color-schemes/NoxForgeDark.colors"
    add_component "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop" "plasma/desktoptheme/io.github.loofiboss.noxforge.desktop"
    add_component "aurorae/io.github.loofiboss.noxforge.desktop" "aurorae/themes/io.github.loofiboss.noxforge.desktop"
    add_component "icons/NoxForge" "icons/NoxForge"
    add_component "cursors/NoxForge-Cursors" "icons/NoxForge-Cursors"
    add_component "sounds/NoxForge" "sounds/NoxForge"
    add_component "look-and-feel/io.github.loofiboss.noxforge.desktop" "plasma/look-and-feel/io.github.loofiboss.noxforge.desktop"
    add_component "kwin/tabbox/io.github.loofiboss.noxforge.desktop" "kwin/tabbox/io.github.loofiboss.noxforge.desktop"
    add_component "wallpapers/NoxForge" "wallpapers/NoxForge"
    add_component "wallpapers/NoxForge-Quiet" "wallpapers/NoxForge-Quiet"
    add_component "wallpapers/NoxForge-Ultrawide" "wallpapers/NoxForge-Ultrawide"
fi

for index in "${!source_paths[@]}"; do
    source="${portable_root}/${source_paths[index]}"
    if [[ ! -e "${source}" ]]; then
        printf 'Missing source component: %s\n' "${source_paths[index]}" >&2
        exit 1
    fi
    if [[ -d "${source}" ]] && find "${source}" -type l -print -quit | grep -q .; then
        printf 'Refusing package with symlinks: %s\n' "${source_paths[index]}" >&2
        exit 1
    fi
done

declare -a migration_sources migration_targets
if [[ "${migrate}" == true ]]; then
    for legacy in "${data_home}/NoxForge" "${data_home}/noxforge-components"; do
        [[ -d "${legacy}" ]] || continue
        if [[ -L "${legacy}" ]]; then
            printf 'Refusing symlinked legacy root: %s\n' "${legacy}" >&2
            exit 1
        fi
        printf 'Recognized legacy root for safe migration: %s\n' "${legacy}"
        for target in "${target_paths[@]}"; do
            candidate="${legacy}/${target}"
            [[ -e "${candidate}" ]] || continue
            if [[ -d "${candidate}" ]] && find "${candidate}" -type l -print -quit | grep -q .; then
                printf 'Refusing symlinked legacy component: %s\n' "${candidate}" >&2
                exit 1
            fi
            migration_sources+=("${candidate}")
            migration_targets+=("${target}")
        done
    done
fi

stage_parent="${data_home}"
temporary_stage_parent=""
if [[ ! -d "${stage_parent}" ]]; then
    if [[ "${dry_run}" == true ]]; then
        # A dry run must not create the user's data root just to stage files.
        temporary_stage_parent=$(mktemp -d "${TMPDIR:-/tmp}/noxforge-install-parent.XXXXXX")
        stage_parent="${temporary_stage_parent}"
    else
        mkdir -p -- "${stage_parent}"
    fi
fi
stage=$(mktemp -d "${stage_parent}/.noxforge-install.XXXXXX")
cleanup() {
    rm -rf -- "${stage}"
    if [[ -n "${temporary_stage_parent}" ]]; then
        rmdir -- "${temporary_stage_parent}" 2>/dev/null || true
    fi
}
trap cleanup EXIT
declare -a owned
copy_into_stage() {
    local source="$1"
    local relative="$2"
    local target="${stage}/${relative}"
    if [[ -d "${source}" ]]; then
        while IFS= read -r -d '' file; do
            local child="${file#${source}/}"
            local child_target="${target}/${child}"
            mkdir -p -- "$(dirname -- "${child_target}")"
            install -m 0644 -- "${file}" "${child_target}"
            owned+=("${relative}/${child}")
        done < <(find "${source}" -type f -print0 | sort -z)
    else
        mkdir -p -- "$(dirname -- "${target}")"
        install -m 0644 -- "${source}" "${target}"
        owned+=("${relative}")
    fi
}
for index in "${!migration_sources[@]}"; do
    copy_into_stage "${migration_sources[index]}" "${migration_targets[index]}"
done
for index in "${!source_paths[@]}"; do
    copy_into_stage "${portable_root}/${source_paths[index]}" "${target_paths[index]}"
done

mkdir -p "${stage}/noxforge/bin"
if [[ -f "${portable_root}/manifest.json" ]]; then
    install -m 0644 "${portable_root}/manifest.json" "${stage}/noxforge/manifest.json"
    owned+=("noxforge/manifest.json")
fi
if [[ -f "${portable_root}/VERSION" ]]; then
    install -m 0644 "${portable_root}/VERSION" "${stage}/noxforge/VERSION"
    owned+=("noxforge/VERSION")
fi
if [[ -f "${portable_root}/bin/noxforge-doctor" ]]; then
    install -m 0755 "${portable_root}/bin/noxforge-doctor" "${stage}/noxforge/bin/noxforge-doctor"
else
    install -m 0755 "${source_root}/tools/noxforge-doctor" "${stage}/noxforge/bin/noxforge-doctor"
fi
owned+=("noxforge/bin/noxforge-doctor")
printf '%s\n' "${owned[@]}" "noxforge/.owned-files" | LC_ALL=C sort -u > "${stage}/noxforge/.owned-files"

if [[ "${dry_run}" == true ]]; then
    printf 'Would install %d owned files below %s\n' "${#owned[@]}" "${data_home}"
    printf 'Dry run complete; no files or settings were changed.\n'
    exit 0
fi
while IFS= read -r file; do
    [[ -n "${file}" ]] || continue
    mkdir -p -- "${data_home}/$(dirname -- "${file}")"
    mode=0644
    [[ "${file}" == "noxforge/bin/noxforge-doctor" ]] && mode=0755
    install -m "${mode}" -- "${stage}/${file}" "${data_home}/${file}"
done < <(find "${stage}" -type f -printf '%P\n' | LC_ALL=C sort)
printf 'Installed NoxForge portable components below %s. No KDE settings were changed.\n' "${data_home}"
