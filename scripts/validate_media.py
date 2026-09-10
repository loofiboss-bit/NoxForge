#!/usr/bin/env python3
"""Validate declared media paths, PNG dimensions, and provenance without writes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import struct
import zlib

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PROVENANCE_KINDS = {"live", "offscreen", "generated", "composited"}


def png_dimensions(data: bytes) -> tuple[int, int]:
    """Validate complete non-interlaced PNG streams, including CRCs and scanlines."""
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("invalid PNG signature")
    offset, chunks, compressed = 8, [], bytearray()
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError("truncated PNG chunk")
        size = struct.unpack(">I", data[offset:offset + 4])[0]
        end = offset + 12 + size
        if end > len(data):
            raise ValueError("truncated PNG payload")
        kind, payload = data[offset + 4:offset + 8], data[offset + 8:end - 4]
        if zlib.crc32(kind + payload) != struct.unpack(">I", data[end - 4:end])[0]:
            raise ValueError("invalid PNG chunk CRC")
        chunks.append(kind)
        if len(chunks) == 1:
            if kind != b"IHDR" or len(payload) != 13:
                raise ValueError("invalid PNG IHDR")
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
        elif kind == b"IHDR":
            raise ValueError("duplicate PNG IHDR")
        if kind == b"IDAT":
            compressed.extend(payload)
        if kind == b"IEND":
            if payload or end != len(data):
                raise ValueError("invalid PNG end")
            offset = end
            break
        offset = end
    if not chunks or chunks[-1] != b"IEND" or not compressed:
        raise ValueError("PNG requires image data and IEND")
    depths = {0: {1, 2, 4, 8, 16}, 2: {8, 16}, 3: {1, 2, 4, 8}, 4: {8, 16}, 6: {8, 16}}
    if (not width or not height or depth not in depths.get(color, set())
            or compression or filtering or interlace):
        raise ValueError("unsupported PNG image format")
    if color == 3 and b"PLTE" not in chunks:
        raise ValueError("indexed PNG requires a palette")
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color]
    stride = (width * depth * channels + 7) // 8 + 1
    expected = height * stride
    if expected > 256 * 1024 * 1024:
        raise ValueError("PNG exceeds decoded media budget")
    decoder = zlib.decompressobj()
    raw = decoder.decompress(bytes(compressed), expected + 1)
    if (len(raw) != expected or not decoder.eof or decoder.unused_data
            or decoder.unconsumed_tail or any(raw[i] > 4 for i in range(0, expected, stride))):
        raise ValueError("invalid PNG image scanlines")
    return width, height


def validate_manifest(root: Path, manifest_path: Path | None = None) -> list[str]:
    root = root.resolve()
    manifest_path = manifest_path or root / "media/manifest.json"
    errors: list[str] = []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"Cannot read media manifest: {exc}"]
    if not isinstance(data, dict):
        return ["Media manifest must be an object"]
    policy = data.get("provenancePolicy", {})
    if not isinstance(policy, dict):
        return ["provenancePolicy must be an object"]
    captures, derivatives = data.get("captures"), data.get("derivatives")
    if not isinstance(captures, list) or not isinstance(derivatives, dict):
        return ["captures must be a list and derivatives must be an object"]
    entries = [(f"captures[{i}]", item, "sourceDimensions", None)
               for i, item in enumerate(captures)]
    entries += [(f"derivatives.{key}", item, "dimensions", key)
                for key, item in derivatives.items()]
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for label, item, dimension_key, derived_id in entries:
        if not isinstance(item, dict):
            errors.append(f"{label}: entry must be an object")
            continue
        identifier = item.get("id", derived_id)
        if not isinstance(identifier, str) or not identifier.strip():
            errors.append(f"{label}: missing nonempty id")
        elif identifier in seen_ids:
            errors.append(f"{label}: duplicate id {identifier}")
        else:
            seen_ids.add(identifier)
        provenance = item.get("provenance")
        kind = provenance.split("-", 1)[0] if isinstance(provenance, str) else ""
        if (kind not in PROVENANCE_KINDS or not isinstance(policy.get(kind), str)
                or not policy[kind].strip() or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", provenance or "")):
            errors.append(f"{label}: invalid or undocumented provenance {provenance!r}")
        value = item.get("path")
        if not isinstance(value, str) or not value or "\\" in value:
            errors.append(f"{label}: invalid relative path")
            continue
        relative = PurePosixPath(value)
        path = (root / value).resolve()
        if relative.is_absolute() or ".." in relative.parts or not path.is_relative_to(root):
            errors.append(f"{label}: path escapes repository: {value}")
            continue
        canonical = str(path)
        if canonical in seen_paths:
            errors.append(f"{label}: duplicate path {value}")
        seen_paths.add(canonical)
        expected = item.get(dimension_key)
        if not isinstance(expected, str) or not re.fullmatch(r"[1-9][0-9]*x[1-9][0-9]*", expected):
            errors.append(f"{label}: invalid {dimension_key}")
            continue
        try:
            image_data = path.read_bytes()
        except OSError as exc:
            errors.append(f"{label}: cannot read {value}: {exc}")
            continue
        try:
            if path.suffix.lower() != ".png":
                raise ValueError("expected PNG extension")
            width, height = png_dimensions(image_data)
        except (ValueError, zlib.error, struct.error) as exc:
            errors.append(f"{label}: invalid PNG in {value}: {exc}")
            continue
        actual = f"{width}x{height}"
        if actual != expected:
            errors.append(f"{label}: dimensions {actual} differ from declared {expected}: {value}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    errors = validate_manifest(args.root, args.manifest)
    if errors:
        print("\n".join(errors))
        return 1
    print("Media manifest paths, PNG dimensions, and provenance validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
