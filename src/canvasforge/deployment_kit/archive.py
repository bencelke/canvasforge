"""Deterministic ZIP creation and safe reading for Deployment Kits."""

from __future__ import annotations

import io
import zipfile
from collections.abc import Mapping
from pathlib import Path

from canvasforge.deployment_kit.checksums import normalize_text_bytes
from canvasforge.deployment_kit.constants import (
    MAX_ARCHIVE_BYTES,
    MAX_COMPRESSION_RATIO,
    MAX_MEMBER_BYTES,
    MAX_MEMBER_COUNT,
    MAX_UNCOMPRESSED_BYTES,
    ZIP_EPOCH,
    ZIP_EXTERNAL_ATTR,
)
from canvasforge.deployment_kit.errors import DeploymentKitError, blocking


def _posix_member(path: str) -> str:
    normalized = path.replace("\\", "/").lstrip("/")
    if not normalized or normalized.endswith("/"):
        raise DeploymentKitError(
            "invalid archive member path",
            diagnostics=[blocking("KIT_BAD_MEMBER_PATH", f"invalid path '{path}'")],
        )
    parts = normalized.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise DeploymentKitError(
            "path traversal rejected",
            diagnostics=[blocking("KIT_PATH_TRAVERSAL", f"rejected path '{path}'")],
        )
    if normalized.startswith("/") or (len(normalized) > 1 and normalized[1] == ":"):
        raise DeploymentKitError(
            "absolute archive path rejected",
            diagnostics=[blocking("KIT_ABSOLUTE_PATH", f"rejected path '{path}'")],
        )
    return normalized


def build_deterministic_zip(members: Mapping[str, bytes]) -> bytes:
    """Create a reproducible ZIP (sorted members, fixed timestamps/attrs)."""
    if len(members) > MAX_MEMBER_COUNT:
        raise DeploymentKitError(
            "too many archive members",
            diagnostics=[
                blocking(
                    "KIT_TOO_MANY_MEMBERS",
                    f"member count {len(members)} exceeds limit {MAX_MEMBER_COUNT}",
                )
            ],
        )

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(members):
            payload = members[path]
            name = _posix_member(path)
            if len(payload) > MAX_MEMBER_BYTES:
                raise DeploymentKitError(
                    "member too large",
                    diagnostics=[
                        blocking(
                            "KIT_MEMBER_TOO_LARGE",
                            f"{name} is {len(payload)} bytes (limit {MAX_MEMBER_BYTES})",
                            path=name,
                        )
                    ],
                )
            info = zipfile.ZipInfo(filename=name, date_time=ZIP_EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3  # Unix
            info.external_attr = ZIP_EXTERNAL_ATTR
            archive.writestr(info, payload)

    data = buffer.getvalue()
    if len(data) > MAX_ARCHIVE_BYTES:
        raise DeploymentKitError(
            "archive too large",
            diagnostics=[
                blocking(
                    "KIT_ARCHIVE_TOO_LARGE",
                    f"archive is {len(data)} bytes (limit {MAX_ARCHIVE_BYTES})",
                )
            ],
        )
    return data


def write_zip(path: Path, members: Mapping[str, bytes]) -> int:
    data = build_deterministic_zip(members)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return len(data)


def read_zip_members(path: Path) -> dict[str, bytes]:
    """Read and validate ZIP members (structure/safety only; checksums separate)."""
    raw = path.read_bytes()
    if len(raw) > MAX_ARCHIVE_BYTES:
        raise DeploymentKitError(
            "archive too large",
            diagnostics=[blocking("KIT_ARCHIVE_TOO_LARGE", f"archive exceeds {MAX_ARCHIVE_BYTES}")],
        )

    members: dict[str, bytes] = {}
    total_uncompressed = 0
    with zipfile.ZipFile(io.BytesIO(raw), mode="r") as archive:
        infos = archive.infolist()
        if len(infos) > MAX_MEMBER_COUNT:
            raise DeploymentKitError(
                "too many archive members",
                diagnostics=[blocking("KIT_TOO_MANY_MEMBERS", "member count exceeds limit")],
            )
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise DeploymentKitError(
                "duplicate archive members",
                diagnostics=[blocking("KIT_DUPLICATE_MEMBER", "duplicate ZIP member names")],
            )
        for info in infos:
            name = info.filename.replace("\\", "/")
            if name.endswith("/"):
                continue
            if name.startswith("/") or name.startswith("../") or "/../" in f"/{name}/":
                raise DeploymentKitError(
                    "path traversal rejected",
                    diagnostics=[blocking("KIT_PATH_TRAVERSAL", f"rejected '{name}'")],
                )
            if ".." in name.split("/"):
                raise DeploymentKitError(
                    "path traversal rejected",
                    diagnostics=[blocking("KIT_PATH_TRAVERSAL", f"rejected '{name}'")],
                )
            if len(name) > 1 and name[1] == ":":
                raise DeploymentKitError(
                    "absolute archive path rejected",
                    diagnostics=[blocking("KIT_ABSOLUTE_PATH", f"rejected '{name}'")],
                )
            if info.file_size > MAX_MEMBER_BYTES:
                raise DeploymentKitError(
                    "member too large",
                    diagnostics=[blocking("KIT_MEMBER_TOO_LARGE", f"{name} exceeds member limit")],
                )
            if info.compress_size > 0:
                ratio = info.file_size / info.compress_size
                if ratio > MAX_COMPRESSION_RATIO and info.file_size > 1024 * 1024:
                    raise DeploymentKitError(
                        "suspicious compression ratio",
                        diagnostics=[
                            blocking(
                                "KIT_COMPRESSION_RATIO",
                                f"{name} compression ratio {ratio:.1f} exceeds limit",
                            )
                        ],
                    )
            payload = archive.read(info)
            total_uncompressed += len(payload)
            if total_uncompressed > MAX_UNCOMPRESSED_BYTES:
                raise DeploymentKitError(
                    "uncompressed payload too large",
                    diagnostics=[blocking("KIT_UNCOMPRESSED_TOO_LARGE", "zip bomb defense")],
                )
            members[_posix_member(name)] = normalize_text_bytes(payload)
    return members
