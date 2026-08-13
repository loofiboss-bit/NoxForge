#!/usr/bin/env python3
"""Validate the public V9 release manifest and its package/edition contracts."""

from __future__ import annotations

import json
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "distribution/release-manifest.json"


def validate() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("schemaVersion") != 2:
        raise ValueError("release manifest schemaVersion must be 2")
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if manifest["release"]["version"] != version:
        raise ValueError("manifest release version does not match VERSION")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", version):
        raise ValueError("active version is not SemVer")
    baseline = manifest["release"].get("baseline", {})
    if any(not isinstance(baseline.get(key), int) or baseline[key] <= 0 for key in ("rpmBytes", "srpmBytes")):
        raise ValueError("V8 baseline must include positive RPM and SRPM sizes")
    managers = manifest["compatibility"].get("loginManagers", {})
    fedora = managers.get("fedora44", {})
    arch = managers.get("arch", {})
    if fedora.get("default") != "plasmalogin" or set(fedora.get("supported", [])) != {"plasmalogin", "sddm"}:
        raise ValueError("Fedora 44 must model Plasma Login Manager as default with SDDM compatibility")
    if fedora.get("integrations") != {"plasmalogin": "wallpaper", "sddm": "custom-theme"}:
        raise ValueError("Fedora login-manager integrations are invalid")
    if arch.get("qualified") != "sddm" or arch.get("supported") != ["sddm"]:
        raise ValueError("Arch login-manager qualification must remain SDDM")
    artifacts = manifest.get("artifacts", [])
    keys = [item.get("key") for item in artifacts]
    filenames = [item.get("filename") for item in artifacts]
    if len(keys) != len(set(keys)) or len(filenames) != len(set(filenames)):
        raise ValueError("artifact keys and filenames must be unique")
    if any(not item.get("budgetBytes", 0) > 0 for item in artifacts):
        raise ValueError("every artifact needs a positive size budget")
    for key in ("store", "portable", "complete-system"):
        edition = manifest["editions"][key]
        if edition["widgetStyle"] not in {"Breeze", "NoxForge"}:
            raise ValueError(f"invalid widgetStyle for {key}")
    wallpapers = manifest["packages"]["wallpapers"]
    if set(wallpapers) != {"forge", "quiet", "ultrawide"}:
        raise ValueError("wallpaper contract must contain Forge, Quiet, and Ultrawide")
    if wallpapers["forge"]["id"] != "NoxForge":
        raise ValueError("the legacy NoxForge wallpaper ID must be retained")
    store_manifest = json.loads(
        (ROOT / "distribution/kde-store/package-manifest.json").read_text(encoding="utf-8")
    )
    if store_manifest.get("license") != "MIT" or store_manifest.get("storeProduct") != "2367662":
        raise ValueError("Store manifest must retain the historical product and MIT license")
    store_keys = {entry.get("key") for entry in store_manifest.get("components", [])}
    expected_store_keys = {item["key"] for item in artifacts if item.get("kind") == "store"}
    if store_keys != expected_store_keys:
        raise ValueError("Store component keys do not match the release artifact graph")
    for entry in store_manifest["components"]:
        package = entry["key"]
        package_name = {
            "global-theme": "globalTheme",
            "plasma-style": "plasmaStyle",
            "colors": "colors",
            "aurorae": "aurorae",
            "icons": "icons",
            "cursors": "cursors",
            "kwin-switcher": "kwinSwitcher",
            "sounds": "sounds",
        }.get(package)
        if package_name and entry.get("id") != manifest["packages"][package_name]["id"]:
            raise ValueError(f"Store package ID drift: {package}")
        if package == "wallpapers" and entry.get("id") != wallpapers["forge"]["id"]:
            raise ValueError("wallpaper Store package ID drift")
        if not set(entry.get("dependencies", [])) <= store_keys:
            raise ValueError(f"Store dependency references an unknown component: {package}")
    source = manifest["source"]
    excludes = source.get("exclude", [])
    if "AGENTS.md" not in excludes or "packaging/arch" not in excludes or not any(str(item).startswith("docs/evidence/v") and str(item)[-1:].isdigit() for item in excludes):
        raise ValueError("developer source must exclude AGENTS.md and full evidence")
    arch_pkgbuild = (ROOT / "packaging/arch/PKGBUILD").read_text(encoding="utf-8")
    arch_srcinfo = (ROOT / "packaging/arch/.SRCINFO").read_text(encoding="utf-8")
    source_name = next(item["filename"] for item in artifacts if item["key"] == "source")
    expected_source_url = f"https://github.com/loofiboss-bit/NoxForge/releases/download/v{manifest['release']['stableVersion']}/{source_name}"
    if "SKIP" in arch_pkgbuild or expected_source_url not in arch_pkgbuild:
        raise ValueError("Arch PKGBUILD source contract is not exact and checksum-bound")
    if "\\t" in arch_srcinfo or "\tpkgver = " not in arch_srcinfo or expected_source_url not in arch_srcinfo:
        raise ValueError("Arch .SRCINFO is not a generated tab-delimited contract")
    local_source = ROOT / "dist" / source_name
    if local_source.is_file():
        digest = hashlib.sha256(local_source.read_bytes()).hexdigest()
        if digest not in arch_pkgbuild or digest not in arch_srcinfo:
            raise ValueError("Arch checksum does not match the local source artifact")
    return {"version": version, "artifacts": len(artifacts), "editions": list(manifest["editions"])}


def main() -> int:
    try:
        print(json.dumps(validate(), sort_keys=True))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"release manifest invalid: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
