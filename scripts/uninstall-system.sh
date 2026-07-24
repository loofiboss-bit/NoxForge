#!/usr/bin/env bash
set -euo pipefail

dry_run=false
system_mode=false
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
source_root=$(cd -- "${script_dir}/.." && pwd)
manifest="${source_root}/build/cmake/install_manifest.txt"

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
    printf 'Refusing uninstall without explicit --system mode.\n' >&2
    exit 2
fi

system_root=${NOXFORGE_SYSTEM_ROOT:-}
if [[ -n "${system_root}" && ( "${system_root}" != /* || "${system_root}" == "/" ) ]]; then
    printf 'NOXFORGE_SYSTEM_ROOT must be a safe absolute staging path.\n' >&2
    exit 2
fi
if [[ "${dry_run}" != true && -z "${system_root}" && ${EUID} -ne 0 ]]; then
    printf 'System uninstall requires root; rerun explicitly through your administrator tool.\n' >&2
    exit 2
fi

if [[ ! -f "${manifest}" && "${dry_run}" != true ]]; then
    printf 'Missing CMake install manifest; refusing an unscoped uninstall.\n' >&2
    exit 1
fi

if [[ "${dry_run}" == true ]]; then
    printf 'Would remove only paths recorded in %s below %s\n' "${manifest}" "${system_root:-<system root>}"
    printf 'Dry run complete; no files or settings were changed.\n'
    exit 0
fi

while IFS= read -r installed_path; do
    [[ -n "${installed_path}" && "${installed_path}" == /* ]] || {
        printf 'Unsafe CMake manifest entry: %s\n' "${installed_path}" >&2
        exit 1
    }
    target="${system_root}${installed_path}"
    case "${target}" in
        "${system_root}/usr/"*) ;;
        *) printf 'Refusing unsafe uninstall target: %s\n' "${target}" >&2; exit 1 ;;
    esac
    rm -f -- "${target}"
done < "${manifest}"

printf 'Removed only files from the NoxForge CMake install manifest. Settings were not changed.\n'
