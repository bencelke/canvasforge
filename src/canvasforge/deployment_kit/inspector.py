"""Inspect Deployment Kits without extracting."""

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
from canvasforge.deployment_kit.constants import CHECKSUMS_NAME, PROJECT_DESCRIPTOR_NAME
from canvasforge.deployment_kit.errors import DeploymentKitError, blocking


def inspect_deployment_kit(kit_path: Path) -> dict[str, Any]:
    path = Path(kit_path)
    if not path.is_file():
        raise DeploymentKitError(
            "Kit not found",
            diagnostics=[blocking("KIT_NOT_FOUND", f"No file at '{path.name}'")],
        )

    members = read_zip_members(path)
    if PROJECT_DESCRIPTOR_NAME not in members:
        raise DeploymentKitError(
            "Missing project descriptor",
            diagnostics=[blocking("KIT_MISSING_DESCRIPTOR", PROJECT_DESCRIPTOR_NAME)],
        )

    project = json.loads(members[PROJECT_DESCRIPTOR_NAME].decode("utf-8"))
    checksum_status = "missing"
    if CHECKSUMS_NAME in members:
        try:
            digests = parse_checksums_file(members[CHECKSUMS_NAME])
            mismatches = []
            for name, digest in digests.items():
                if name not in members or sha256_hex(members[name]) != digest:
                    mismatches.append(name)
            extra = [name for name in members if name != CHECKSUMS_NAME and name not in digests]
            if mismatches or extra:
                checksum_status = "mismatch"
            else:
                expected = package_content_checksum(members)
                if project.get("packageContentChecksum") != expected:
                    checksum_status = "content-checksum-mismatch"
                else:
                    checksum_status = "ok"
        except ValueError:
            checksum_status = "invalid"

    install_order = members.get("deployment/install-order.md", b"").decode("utf-8")
    steps = [
        line.strip()
        for line in install_order.splitlines()
        if line.strip() and line.strip()[0].isdigit()
    ]

    omitted: list[Any] = []
    if "reports/package-manifest.json" in members:
        inventory = json.loads(members["reports/package-manifest.json"].decode("utf-8"))
        omitted = inventory.get("omitted", [])

    return {
        "packageFormat": project.get("packageFormat"),
        "packageSchemaVersion": project.get("packageSchemaVersion"),
        "canvasforgeVersion": project.get("canvasforgeVersion"),
        "projectKey": project.get("projectKey"),
        "projectName": project.get("projectName"),
        "buildId": project.get("buildId"),
        "buildMaturity": project.get("buildMaturity"),
        "targetAdapter": project.get("targetAdapter"),
        "compatibilityProfileId": project.get("compatibilityProfileId"),
        "compatibilityProfileVersion": project.get("compatibilityProfileVersion"),
        "generatedScreens": project.get("generatedScreens", []),
        "generatedBlocks": project.get("generatedBlocks", []),
        "checksumStatus": checksum_status,
        "securityClassification": project.get("securityClassification"),
        "containsProductionData": project.get("containsProductionData"),
        "containsCredentials": project.get("containsCredentials"),
        "containsTenantIdentifiers": project.get("containsTenantIdentifiers"),
        "mockDataIncluded": project.get("mockDataIncluded"),
        "mockDataClassification": project.get("mockDataClassification"),
        "reproducible": project.get("reproducible"),
        "memberCount": len(members),
        "members": sorted(members.keys()),
        "deploymentSteps": steps,
        "omitted": omitted,
        "packageContentChecksum": project.get("packageContentChecksum"),
        "sourceManifestChecksum": project.get("sourceManifestChecksum"),
        "warnings": [],
    }
