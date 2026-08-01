"""Verify Deployment Kit integrity and safety."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from canvasforge.deployment_kit.archive import read_zip_members
from canvasforge.deployment_kit.checksums import (
    package_content_checksum,
    parse_checksums_file,
    sha256_hex,
)
from canvasforge.deployment_kit.constants import (
    CHECKSUMS_NAME,
    PACKAGE_SCHEMA_VERSION,
    PROJECT_DESCRIPTOR_NAME,
    REQUIRED_MEMBERS,
    SUPPORTED_PACKAGE_SCHEMA_VERSIONS,
)
from canvasforge.deployment_kit.errors import DeploymentKitError, blocking
from canvasforge.deployment_kit.schema import validate_project_descriptor


def verify_deployment_kit(kit_path: Path) -> dict[str, Any]:
    path = Path(kit_path)
    if not path.is_file():
        raise DeploymentKitError(
            "Kit not found",
            diagnostics=[blocking("KIT_NOT_FOUND", f"No file at '{path.name}'")],
        )

    members = read_zip_members(path)
    diagnostics = []

    if PROJECT_DESCRIPTOR_NAME not in members:
        raise DeploymentKitError(
            "Missing project descriptor",
            diagnostics=[blocking("KIT_MISSING_DESCRIPTOR", PROJECT_DESCRIPTOR_NAME)],
        )
    if CHECKSUMS_NAME not in members:
        raise DeploymentKitError(
            "Missing checksums file",
            diagnostics=[blocking("KIT_MISSING_CHECKSUMS", CHECKSUMS_NAME)],
        )

    try:
        project = json.loads(members[PROJECT_DESCRIPTOR_NAME].decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise DeploymentKitError(
            "Invalid project descriptor JSON",
            diagnostics=[blocking("KIT_DESCRIPTOR_JSON", str(exc))],
        ) from exc

    schema_version = str(project.get("packageSchemaVersion", ""))
    if schema_version not in SUPPORTED_PACKAGE_SCHEMA_VERSIONS:
        raise DeploymentKitError(
            "Unsupported package schema version",
            diagnostics=[
                blocking(
                    "KIT_UNSUPPORTED_SCHEMA",
                    f"schema '{schema_version}' is not supported "
                    f"(supported: {sorted(SUPPORTED_PACKAGE_SCHEMA_VERSIONS)})",
                )
            ],
        )

    validate_project_descriptor(project)

    missing = sorted(name for name in REQUIRED_MEMBERS if name not in members)
    if missing:
        raise DeploymentKitError(
            "Required members missing",
            diagnostics=[
                blocking("KIT_MISSING_REQUIRED", f"missing {name}", path=name) for name in missing
            ],
        )

    try:
        digests = parse_checksums_file(members[CHECKSUMS_NAME])
    except ValueError as exc:
        raise DeploymentKitError(
            "Invalid checksums file",
            diagnostics=[blocking("KIT_CHECKSUMS_INVALID", str(exc))],
        ) from exc

    for name, digest in sorted(digests.items()):
        if name not in members:
            diagnostics.append(blocking("KIT_CHECKSUM_MISSING_MEMBER", name, path=name))
            continue
        actual = sha256_hex(members[name])
        if actual != digest:
            diagnostics.append(
                blocking(
                    "KIT_CHECKSUM_MISMATCH",
                    "member digest mismatch",
                    path=name,
                )
            )

    for name in members:
        if name == CHECKSUMS_NAME:
            continue
        if name not in digests:
            diagnostics.append(blocking("KIT_MEMBER_NOT_IN_CHECKSUMS", name, path=name))

    expected_content = package_content_checksum(members)
    if project.get("packageContentChecksum") != expected_content:
        diagnostics.append(
            blocking(
                "KIT_CONTENT_CHECKSUM_MISMATCH",
                "packageContentChecksum does not match recomputed inventory digest",
                path=PROJECT_DESCRIPTOR_NAME,
            )
        )

    # Fail closed on unknown major (already handled) and any diagnostic errors.
    if diagnostics:
        raise DeploymentKitError("Deployment kit verification failed", diagnostics=diagnostics)

    return {
        "ok": True,
        "packageSchemaVersion": schema_version or PACKAGE_SCHEMA_VERSION,
        "buildId": project.get("buildId"),
        "projectKey": project.get("projectKey"),
        "memberCount": len(members),
        "packageContentChecksum": expected_content,
    }
