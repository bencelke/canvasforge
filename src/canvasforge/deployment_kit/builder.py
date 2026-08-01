"""Build CanvasForge Deployment Kits (``.cforge.zip``)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from canvasforge import __version__
from canvasforge.deployment_kit.archive import build_deterministic_zip, write_zip
from canvasforge.deployment_kit.checksums import finalize_kit_members, normalize_text_bytes
from canvasforge.deployment_kit.constants import (
    CHECKSUMS_NAME,
    COMPATIBILITY_PROFILE_ID,
    COMPATIBILITY_PROFILE_VERSION,
    DEFAULT_TARGET,
    ENTRY_MANIFEST_NAME,
    PACKAGE_FORMAT,
    PACKAGE_SCHEMA_VERSION,
    PROJECT_DESCRIPTOR_NAME,
)
from canvasforge.deployment_kit.documents import (
    app_onstart_placeholder,
    build_data_contract,
    collections_json,
    compatibility_profile_json,
    data_connection_checklist_md,
    evidence_summary_json,
    formulas_readme,
    install_order_md,
    known_limitations_md,
    mock_schema_readme,
    power_apps_checklist_md,
    theme_json,
    validation_record_template_json,
    validation_report_json,
)
from canvasforge.deployment_kit.errors import (
    DeploymentKitError,
    DeploymentKitSecurityError,
    blocking,
)
from canvasforge.deployment_kit.models import dump_canonical_json
from canvasforge.deployment_kit.schema import validate_project_descriptor
from canvasforge.deployment_kit.security import scan_members
from canvasforge.errors import Diagnostic
from canvasforge.generate.pipeline import GenerationResult, run_generation
from canvasforge.generate.reports import compute_manifest_checksum, dump_json
from canvasforge.manifest.loader import load_manifest_dict
from canvasforge.manifest.models import AppManifest
from canvasforge.manifest.validator import parse_manifest


@dataclass
class PackageBuildResult:
    build_id: str
    output_path: Path | None
    members: dict[str, bytes]
    project: dict[str, Any]
    package_bytes: bytes | None
    diagnostics: list[Diagnostic] = field(default_factory=list)
    dry_run: bool = False
    omitted: list[dict[str, str]] = field(default_factory=list)
    security_status: str = "pass"
    expected_size: int = 0


def _slug_project_name(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-")
    return slug or "CanvasForge-Project"


def _default_output_path(project_name: str, output: Path | None) -> Path:
    if output is not None:
        return output
    return Path("dist") / f"{_slug_project_name(project_name)}.cforge.zip"


def _find_actions_mock(manifest_path: Path) -> Path | None:
    candidate = manifest_path.resolve().parent / "mock-data" / "actions.json"
    return candidate if candidate.is_file() else None


def _assemble_members(
    *,
    manifest: AppManifest,
    manifest_raw: bytes,
    generation: GenerationResult,
    manifest_checksum: str,
    include_mock_data: bool,
    actions_path: Path | None,
    target: str,
    omitted: list[dict[str, str]],
) -> tuple[dict[str, bytes], str]:
    members: dict[str, bytes] = {}
    raw = manifest_raw if manifest_raw.endswith(b"\n") else manifest_raw + b"\n"
    members[ENTRY_MANIFEST_NAME] = raw
    members["theme/theme.json"] = theme_json(manifest).encode("utf-8")
    members["formulas/README.md"] = formulas_readme().encode("utf-8")
    members["formulas/app-onstart.powerfx"] = app_onstart_placeholder().encode("utf-8")
    members["formulas/screen-formulas/README.md"] = (
        b"# Screen formulas\n\nNot generated in Phase 3B.\n"
    )

    data_contract = build_data_contract(manifest, actions_path=actions_path)
    members["mock-schema/data-contract.json"] = dump_canonical_json(data_contract).encode("utf-8")
    members["mock-schema/collections.json"] = dump_canonical_json(
        collections_json(manifest)
    ).encode("utf-8")
    members["mock-schema/README.md"] = mock_schema_readme(
        include_mock_data=include_mock_data
    ).encode("utf-8")

    if include_mock_data and actions_path is not None:
        members["mock-schema/records/actions.json"] = normalize_text_bytes(
            actions_path.read_bytes()
        )
        members["mock-schema/records/README.md"] = (
            b"# Fictional mock records\n\n"
            b"Classification: fictional-development\n\n"
            b"These records are synthetic examples only.\n"
        )

    screens = sorted(generation.yaml_by_screen.keys())
    for screen_key in screens:
        yaml_text = generation.yaml_by_screen[screen_key]
        text = yaml_text if yaml_text.endswith("\n") else yaml_text + "\n"
        members[f"generated/code-view/{screen_key}.yaml"] = text.encode("utf-8")

    members["generated/control-tree.json"] = dump_json(generation.control_tree).encode("utf-8")
    members["generated/generation-plan.json"] = dump_json(
        generation.plan.model_dump(mode="json")
    ).encode("utf-8")

    members["deployment/install-order.md"] = install_order_md(
        screens=screens, target=target
    ).encode("utf-8")
    members["deployment/power-apps-checklist.md"] = power_apps_checklist_md().encode("utf-8")
    members["deployment/data-connection-checklist.md"] = data_connection_checklist_md().encode(
        "utf-8"
    )
    members["deployment/validation-record-template.json"] = validation_record_template_json(
        build_id=generation.build_id
    ).encode("utf-8")
    members["deployment/known-limitations.md"] = known_limitations_md().encode("utf-8")

    members["compatibility/profile.json"] = compatibility_profile_json().encode("utf-8")
    members["compatibility/evidence-summary.json"] = evidence_summary_json(
        generation.report
    ).encode("utf-8")

    members["reports/build-report.json"] = dump_json(generation.report).encode("utf-8")
    members["reports/validation-report.json"] = validation_report_json(
        manifest_checksum=manifest_checksum,
        diagnostics=[d.to_dict() for d in generation.diagnostics],
        valid=True,
    ).encode("utf-8")

    security_report = scan_members(members)
    members["reports/forbidden-content-report.json"] = dump_canonical_json(
        security_report.model_dump(mode="json", by_alias=True)
    ).encode("utf-8")

    if security_report.blocking_count:
        raise DeploymentKitSecurityError(
            "Forbidden content blocked packaging",
            diagnostics=[
                Diagnostic(
                    code=finding.code,
                    message=finding.message,
                    path=finding.path,
                    severity="error",
                )
                for finding in security_report.findings
                if finding.severity == "error"
            ],
        )

    members["reports/package-manifest.json"] = dump_canonical_json(
        {
            "schemaVersion": PACKAGE_SCHEMA_VERSION,
            "memberCount": 0,
            "members": [],
            "omitted": omitted,
            "reproducible": True,
            "includeMockData": include_mock_data,
        }
    ).encode("utf-8")
    return members, security_report.status


def build_deployment_kit(
    manifest_path: Path,
    *,
    output: Path | None = None,
    project_name: str | None = None,
    target: str = DEFAULT_TARGET,
    screen: str | None = None,
    compatibility_profile: str = COMPATIBILITY_PROFILE_ID,
    allow_partial: bool = False,
    dry_run: bool = False,
    overwrite: bool = False,
    include_mock_data: bool = False,
    non_reproducible_metadata: bool = False,
) -> PackageBuildResult:
    """Validate, generate, scan, and package a Deployment Kit."""
    if target != "code-view":
        raise DeploymentKitError(
            f"Unsupported target '{target}'",
            diagnostics=[
                blocking(
                    "KIT_UNKNOWN_TARGET",
                    "Only target 'code-view' is supported in Phase 3B",
                )
            ],
        )
    if compatibility_profile != COMPATIBILITY_PROFILE_ID:
        raise DeploymentKitError(
            "Unknown compatibility profile",
            diagnostics=[
                blocking(
                    "KIT_UNKNOWN_PROFILE",
                    f"Only '{COMPATIBILITY_PROFILE_ID}' is available in Phase 3B",
                )
            ],
        )

    path = Path(manifest_path)
    raw = normalize_text_bytes(path.read_bytes())
    manifest_checksum = compute_manifest_checksum(raw)
    data = load_manifest_dict(path)
    manifest: AppManifest = parse_manifest(data)

    generation: GenerationResult = run_generation(
        path,
        target=target,
        screen=screen,
        dry_run=True,
        allow_partial=allow_partial,
    )

    display_name = project_name or manifest.app.name
    out_path = _default_output_path(display_name, output)
    if out_path.exists() and not overwrite and not dry_run:
        raise DeploymentKitError(
            "Output already exists",
            diagnostics=[
                blocking(
                    "KIT_OUTPUT_EXISTS",
                    f"Refusing to overwrite '{out_path.name}' without --overwrite",
                    path=out_path.name,
                )
            ],
        )

    omitted: list[dict[str, str]] = [
        {"path": "generated/msapp/", "reason": "Experimental .msapp output deferred"},
        {"path": "preview/", "reason": "Local graphical preview not implemented (Phase 4)"},
    ]
    if not include_mock_data:
        omitted.append(
            {
                "path": "mock-schema/records/",
                "reason": "Mock records excluded by default; pass --include-mock-data",
            }
        )

    actions_path = _find_actions_mock(path)
    assembled, security_status = _assemble_members(
        manifest=manifest,
        manifest_raw=raw,
        generation=generation,
        manifest_checksum=manifest_checksum,
        include_mock_data=include_mock_data,
        actions_path=actions_path,
        target=target,
        omitted=omitted,
    )

    screens = sorted(generation.yaml_by_screen.keys())
    included_features = [
        "manifest",
        "candidate-code-view",
        "control-tree",
        "generation-plan",
        "mock-schema",
        "deployment-docs",
        "compatibility-profile",
        "checksums",
    ]
    if include_mock_data:
        included_features.append("fictional-mock-records")

    notes = "Deployment Kit schema 0.1. Candidate output requires Power Apps Studio validation."
    if non_reproducible_metadata:
        notes += " non-reproducible-metadata requested; no host identity recorded."

    project_fields: dict[str, object] = {
        "packageFormat": PACKAGE_FORMAT,
        "packageSchemaVersion": PACKAGE_SCHEMA_VERSION,
        "canvasforgeVersion": __version__,
        "projectKey": manifest.app.key,
        "projectName": display_name,
        "projectVersion": manifest.app.version,
        "manifestVersion": manifest.app.manifest_version,
        "buildId": generation.build_id,
        "buildMaturity": "Candidate-StudioUnvalidated",
        "targetAdapter": target,
        "compatibilityProfileId": COMPATIBILITY_PROFILE_ID,
        "compatibilityProfileVersion": COMPATIBILITY_PROFILE_VERSION,
        "entryManifest": ENTRY_MANIFEST_NAME,
        "generatedScreens": screens,
        "generatedBlocks": [f"generated/code-view/{key}.yaml" for key in screens],
        "includedFeatures": included_features,
        "excludedFeatures": [
            "msapp",
            "gui-preview",
            "runner",
            "microsoft-auth",
            "tenant-connectors",
            "power-automate",
        ],
        "requiredManualSteps": [
            "Verify kit checksums",
            "Paste Candidate Code View in Studio sandbox",
            "Record Studio validation outcomes",
            "Connect data sources manually",
            "Publish only after approval",
        ],
        "reproducible": not non_reproducible_metadata,
        "sourceManifestChecksum": manifest_checksum,
        "packageCreatedBy": "CanvasForge",
        "securityClassification": "fictional-development",
        "containsProductionData": False,
        "containsCredentials": False,
        "containsTenantIdentifiers": False,
        "mockDataIncluded": include_mock_data,
        "mockDataClassification": "fictional-records" if include_mock_data else "schema-only",
        "notes": notes,
    }

    body = {
        path: payload
        for path, payload in assembled.items()
        if path not in {CHECKSUMS_NAME, PROJECT_DESCRIPTOR_NAME}
    }
    predicted_members = sorted([*body.keys(), PROJECT_DESCRIPTOR_NAME, CHECKSUMS_NAME])
    body["reports/package-manifest.json"] = dump_canonical_json(
        {
            "schemaVersion": PACKAGE_SCHEMA_VERSION,
            "memberCount": len(predicted_members),
            "members": predicted_members,
            "omitted": omitted,
            "reproducible": not non_reproducible_metadata,
            "includeMockData": include_mock_data,
        }
    ).encode("utf-8")
    # Predicted list must account for the package-manifest path itself.
    predicted_members = sorted([*body.keys(), PROJECT_DESCRIPTOR_NAME, CHECKSUMS_NAME])
    body["reports/package-manifest.json"] = dump_canonical_json(
        {
            "schemaVersion": PACKAGE_SCHEMA_VERSION,
            "memberCount": len(predicted_members),
            "members": predicted_members,
            "omitted": omitted,
            "reproducible": not non_reproducible_metadata,
            "includeMockData": include_mock_data,
        }
    ).encode("utf-8")
    finalized, _ = finalize_kit_members(body, project_fields=project_fields)
    if sorted(finalized.keys()) != predicted_members:
        raise DeploymentKitError(
            "Package inventory mismatch",
            diagnostics=[
                blocking(
                    "KIT_INVENTORY_MISMATCH",
                    "Final member set did not match predicted package-manifest inventory",
                )
            ],
        )

    project = json.loads(finalized[PROJECT_DESCRIPTOR_NAME].decode("utf-8"))
    validate_project_descriptor(project)

    package_bytes = build_deterministic_zip(finalized)
    result = PackageBuildResult(
        build_id=generation.build_id,
        output_path=None if dry_run else out_path,
        members=finalized,
        project=project,
        package_bytes=package_bytes,
        diagnostics=list(generation.diagnostics),
        dry_run=dry_run,
        omitted=omitted,
        security_status=security_status,
        expected_size=len(package_bytes),
    )
    if dry_run:
        return result

    write_zip(out_path, finalized)
    from canvasforge.deployment_kit.verifier import verify_deployment_kit

    verify_deployment_kit(out_path)
    result.output_path = out_path
    result.package_bytes = out_path.read_bytes()
    return result
