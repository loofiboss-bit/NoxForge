#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
source_root=$(cd -- "${script_dir}/.." && pwd)
dry_run=false
system_mode=false

usage() {
    printf 'Usage: %s --system [--dry-run]\n' "${0##*/}"
}

for argument in "$@"; do
    case "${argument}" in
        --system) system_mode=true ;;
        --dry-run) dry_run=true ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'Unknown argument: %s\n' "${argument}" >&2; usage >&2; exit 2 ;;
    esac
done

if [[ "${system_mode}" != true ]]; then
    printf 'Refusing installation without explicit --system mode.\n' >&2
    exit 2
fi

system_root=${NOXFORGE_SYSTEM_ROOT:-}
if [[ -n "${system_root}" && ( "${system_root}" != /* || "${system_root}" == "/" ) ]]; then
    printf 'NOXFORGE_SYSTEM_ROOT must be a safe absolute staging path.\n' >&2
    exit 2
fi
if [[ "${dry_run}" != true && -z "${system_root}" && ${EUID} -ne 0 ]]; then
    printf 'System installation requires root; rerun explicitly through your administrator tool.\n' >&2
    exit 2
fi

plugin_source="${source_root}/build/cmake/plugins/styles/libnoxforge6.so"
sddm_source="${source_root}/sddm/NoxForge"
plugin_target="${system_root}/usr/lib64/qt6/plugins/styles/libnoxforge6.so"
sddm_target="${system_root}/usr/share/sddm/themes/NoxForge"

if [[ ! -f "${plugin_source}" && "${dry_run}" != true ]]; then
    printf 'Missing built style plugin. Run cmake configure and build first.\n' >&2
    exit 1
fi
if [[ ! -d "${sddm_source}" ]] || find "${sddm_source}" -type l -print -quit | grep -q .; then
    printf 'Missing or unsafe SDDM source package.\n' >&2
    exit 1
fi

if [[ "${dry_run}" == true ]]; then
    printf 'Would install %s -> %s\n' "${plugin_source}" "${plugin_target}"
    printf 'Would install %s -> %s\n' "${sddm_source}" "${sddm_target}"
    printf 'Dry run complete; no files or settings were changed.\n'
    exit 0
fi

install -D -m 0755 "${plugin_source}" "${plugin_target}"
install -d -m 0755 "${sddm_target}"
cp -a -- "${sddm_source}/." "${sddm_target}/"
printf 'Installed the NoxForge Qt style and SDDM theme. No settings were changed.\n'
