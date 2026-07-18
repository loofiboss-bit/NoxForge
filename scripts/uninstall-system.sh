#!/usr/bin/env bash
set -euo pipefail

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

plugin_target="${system_root}/usr/lib64/qt6/plugins/styles/libnoxforge6.so"
sddm_target="${system_root}/usr/share/sddm/themes/NoxForge"

if [[ "${dry_run}" == true ]]; then
    printf 'Would remove %s\n' "${plugin_target}"
    printf 'Would remove %s\n' "${sddm_target}"
    printf 'Dry run complete; no files or settings were changed.\n'
    exit 0
fi

rm -f -- "${plugin_target}"
rm -rf -- "${sddm_target}"
printf 'Removed only the NoxForge Qt style plugin and SDDM theme. Settings were not changed.\n'
