#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
source_root=$(cd -- "${script_dir}/.." && pwd)
build_root="${source_root}/build/cmake"
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

if [[ ! -f "${build_root}/cmake_install.cmake" && "${dry_run}" != true ]]; then
    printf 'Missing configured CMake build. Run cmake configure and build first.\n' >&2
    exit 1
fi

if [[ "${dry_run}" == true ]]; then
    printf 'Would run CMake install from %s with DESTDIR=%s\n' "${build_root}" "${system_root:-<system root>}"
    printf 'Dry run complete; no files or settings were changed.\n'
    exit 0
fi

DESTDIR="${system_root}" cmake --install "${build_root}"
printf 'Installed NoxForge through the CMake staging contract. No settings were changed.\n'
