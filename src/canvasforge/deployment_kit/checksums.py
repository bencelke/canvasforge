"""Checksum helpers for Deployment Kits.

Canonical algorithm (schema 0.1)
--------------------------------
1. Assemble every archive member as UTF-8 bytes with LF newlines.
2. Exclude ``checksums.sha256`` and ``canvasforge-project.json`` from the
   *package content checksum* inventory.
3. For each remaining member path (POSIX), compute ``SHA-256(member_bytes)``.
4. ``packageContentChecksum`` is SHA-256 over the canonical inventory string::

       for path in sorted(paths):
           f"{path}\\n{hex_digest}\\n"

5. Write ``packageContentChecksum`` into ``canvasforge-project.json``.
6. ``checksums.sha256`` lists every member **including** the project descriptor
   but **excluding itself**, ``sha256sum`` style::

       ``{hex_digest}  {path}\\n``

   Paths sorted. Two spaces between digest and path.
7. Verification recomputes steps 3-6 from ZIP member bytes.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping

from canvasforge.deployment_kit.constants import CHECKSUMS_NAME, PROJECT_DESCRIPTOR_NAME
from canvasforge.deployment_kit.models import dump_canonical_json


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_text_bytes(raw: bytes) -> bytes:
    """Normalize newlines to LF for stable hashing and ZIP payloads."""
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def member_digest_map(members: Mapping[str, bytes]) -> dict[str, str]:
    return {path: sha256_hex(payload) for path, payload in members.items()}


def package_content_checksum(members: Mapping[str, bytes]) -> str:
    """Checksum over members excluding checksums file and project descriptor."""
    filtered = {
        path: payload
        for path, payload in members.items()
        if path not in {CHECKSUMS_NAME, PROJECT_DESCRIPTOR_NAME}
    }
    digests = member_digest_map(filtered)
    inventory = "".join(f"{path}\n{digests[path]}\n" for path in sorted(digests))
    return sha256_hex(inventory.encode("utf-8"))


def format_checksums_file(members: Mapping[str, bytes]) -> bytes:
    """Build ``checksums.sha256`` covering all members except itself."""
    filtered = {path: payload for path, payload in members.items() if path != CHECKSUMS_NAME}
    digests = member_digest_map(filtered)
    lines = [f"{digests[path]}  {path}\n" for path in sorted(digests)]
    return "".join(lines).encode("utf-8")


def parse_checksums_file(raw: bytes) -> dict[str, str]:
    text = normalize_text_bytes(raw).decode("utf-8")
    result: dict[str, str] = {}
    for line_no, line in enumerate(text.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            raise ValueError(f"invalid checksums.sha256 line {line_no}")
        digest, path = parts[0].strip(), parts[1].strip()
        if len(digest) != 64 or path in result:
            raise ValueError(f"invalid checksums.sha256 line {line_no}")
        result[path] = digest
    return result


def finalize_kit_members(
    members: dict[str, bytes],
    *,
    project_fields: dict[str, object],
) -> tuple[dict[str, bytes], str]:
    """Finalize project descriptor and checksums without circular dependency."""
    working = {path: normalize_text_bytes(payload) for path, payload in members.items()}
    working.pop(CHECKSUMS_NAME, None)
    working.pop(PROJECT_DESCRIPTOR_NAME, None)

    content_checksum = package_content_checksum(working)
    project = dict(project_fields)
    project["packageContentChecksum"] = content_checksum
    working[PROJECT_DESCRIPTOR_NAME] = dump_canonical_json(project).encode("utf-8")

    working[CHECKSUMS_NAME] = format_checksums_file(working)
    return working, content_checksum
