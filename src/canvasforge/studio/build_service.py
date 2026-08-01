"""Deployment Kit builds from Studio (delegates to Phase 3B builder)."""

from __future__ import annotations

from pathlib import Path

from canvasforge.deployment_kit.builder import build_deployment_kit
from canvasforge.deployment_kit.verifier import verify_deployment_kit
from canvasforge.studio.models import PackageResult, SessionBuild
from canvasforge.studio.project_service import ProjectService
from canvasforge.studio.security import resolve_safe_output_path


def package_current_project(
    service: ProjectService,
    *,
    output: str | None,
    include_mock_data: bool,
    screen: str | None,
    allow_partial: bool,
    overwrite: bool,
    dist_dir: Path,
) -> PackageResult:
    project = service.require_current()
    if output:
        out_path = resolve_safe_output_path(
            output,
            workspace_roots=service.workspace_roots,
            default_dir=dist_dir,
        )
    else:
        slug = project.manifest.app.key
        out_path = resolve_safe_output_path(
            f"{slug}.cforge.zip",
            workspace_roots=service.workspace_roots,
            default_dir=dist_dir,
        )

    result = build_deployment_kit(
        project.manifest_path,
        output=out_path,
        include_mock_data=include_mock_data,
        screen=screen,
        allow_partial=allow_partial or project.allow_partial,
        overwrite=overwrite,
    )
    verified = verify_deployment_kit(out_path)
    warnings = [d.message for d in result.diagnostics if d.severity == "warning"]
    payload = PackageResult(
        buildId=result.build_id,
        outputName=out_path.name,
        packageContentChecksum=str(result.project.get("packageContentChecksum", "")),
        sizeBytes=result.expected_size,
        maturity=str(result.project.get("buildMaturity", "Candidate-StudioUnvalidated")),
        verified=bool(verified.get("ok")),
        securityStatus=result.security_status,
        members=sorted(result.members.keys()),
        warnings=warnings,
    )
    service.session_builds.append(
        SessionBuild(
            buildId=payload.build_id,
            outputName=payload.output_name,
            packageContentChecksum=payload.package_content_checksum,
            sizeBytes=payload.size_bytes,
            verified=payload.verified,
            maturity=payload.maturity,
        ).model_dump(mode="json", by_alias=True)
    )
    return payload
