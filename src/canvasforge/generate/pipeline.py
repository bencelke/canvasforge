"""End-to-end generation pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from canvasforge.adapters.code_view import CodeViewAdapter
from canvasforge.errors import Diagnostic, GenerationError
from canvasforge.generate.expander import build_app_ir
from canvasforge.generate.reports import (
    build_generation_plan_from_ir,
    build_report,
    compute_build_id,
    compute_manifest_checksum,
    control_tree_dict,
    dump_json,
)
from canvasforge.ir.models import AppIR, GenerationArtifact, GenerationPlan
from canvasforge.manifest.loader import load_manifest_dict
from canvasforge.manifest.models import AppManifest
from canvasforge.manifest.validator import parse_manifest


@dataclass
class GenerationResult:
    build_id: str
    ir: AppIR
    plan: GenerationPlan
    report: dict[str, Any]
    control_tree: dict[str, Any]
    diagnostics: list[Diagnostic]
    yaml_by_screen: dict[str, str]
    artifacts: list[GenerationArtifact] = field(default_factory=list)
    output_dir: Path | None = None


def run_generation(
    manifest_path: Path,
    *,
    target: str = "code-view",
    output_dir: Path | None = None,
    screen: str | None = None,
    dry_run: bool = False,
    allow_partial: bool = False,
) -> GenerationResult:
    """Validate, expand, adapt, and optionally write Candidate artifacts."""
    if target != "code-view":
        raise GenerationError(
            f"Unsupported target adapter '{target}'",
            diagnostics=[
                Diagnostic(
                    code="UNKNOWN_TARGET",
                    message=f"Only 'code-view' is implemented in Phase 2 (got '{target}')",
                    path="$",
                )
            ],
        )

    path = Path(manifest_path)
    raw = path.read_bytes()
    checksum = compute_manifest_checksum(raw)
    data = load_manifest_dict(path)
    manifest: AppManifest = parse_manifest(data)

    screen_keys = [screen] if screen else [manifest.app.start_screen]
    build_id = compute_build_id(
        manifest_checksum=checksum,
        target=target,
        screen_keys=screen_keys,
        allow_partial=allow_partial,
    )

    ir, diagnostics, expanded, omitted = build_app_ir(
        manifest,
        screen_keys=screen_keys,
        allow_partial=allow_partial,
    )

    blocking = [d for d in diagnostics if d.severity == "error"]
    if blocking:
        raise GenerationError(
            "Generation blocked by diagnostics",
            diagnostics=blocking,
        )

    adapter = CodeViewAdapter()
    adapted = adapter.generate(ir, build_id=build_id)
    diagnostics.extend(adapted.diagnostics)

    yaml_by_screen = {item.screen_key: item.yaml_text for item in adapted.screens}
    plan = build_generation_plan_from_ir(
        build_id=build_id,
        ir=ir,
        target=target,
        expanded=expanded,
        omitted=omitted,
    )
    tree = control_tree_dict(ir)

    slug = _slugify(manifest.app.key)
    artifacts = [
        GenerationArtifact(
            kind="code-view-yaml",
            relative_path=f"code-view/{screen_key}.yaml",
            content_type="application/yaml",
            deterministic=True,
        )
        for screen_key in yaml_by_screen
    ]
    artifacts.extend(
        [
            GenerationArtifact(
                kind="generation-plan",
                relative_path="reports/generation-plan.json",
                content_type="application/json",
                deterministic=True,
            ),
            GenerationArtifact(
                kind="generation-report",
                relative_path="reports/generation-report.json",
                content_type="application/json",
                deterministic=True,
            ),
            GenerationArtifact(
                kind="control-tree",
                relative_path="reports/control-tree.json",
                content_type="application/json",
                deterministic=True,
            ),
            GenerationArtifact(
                kind="diagnostics",
                relative_path="reports/diagnostics.json",
                content_type="application/json",
                deterministic=True,
            ),
            GenerationArtifact(
                kind="readme",
                relative_path="reports/README.md",
                content_type="text/markdown",
                deterministic=True,
            ),
        ]
    )

    report = build_report(
        build_id=build_id,
        manifest_path=str(path),
        manifest_checksum=checksum,
        target=target,
        ir=ir,
        expanded=expanded,
        omitted=omitted,
        diagnostics=diagnostics,
        artifacts=artifacts,
        screen_keys=screen_keys,
    )

    result = GenerationResult(
        build_id=build_id,
        ir=ir,
        plan=plan,
        report=report,
        control_tree=tree,
        diagnostics=diagnostics,
        yaml_by_screen=yaml_by_screen,
        artifacts=artifacts,
    )

    if dry_run:
        return result

    out = output_dir or (Path("generated") / slug)
    _write_artifacts(out, result, manifest_name=path.name)
    result.output_dir = out
    return result


def _slugify(app_key: str) -> str:
    import re

    return re.sub(r"[^a-zA-Z0-9]+", "-", app_key).strip("-").lower() or "app"


def _write_artifacts(output_dir: Path, result: GenerationResult, *, manifest_name: str) -> None:
    code_view_dir = output_dir / "code-view"
    reports_dir = output_dir / "reports"
    code_view_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    for screen_key, yaml_text in result.yaml_by_screen.items():
        (code_view_dir / f"{screen_key}.yaml").write_text(yaml_text, encoding="utf-8")

    (reports_dir / "generation-plan.json").write_text(
        dump_json(result.plan.model_dump(mode="json")),
        encoding="utf-8",
    )
    (reports_dir / "generation-report.json").write_text(
        dump_json(result.report),
        encoding="utf-8",
    )
    (reports_dir / "control-tree.json").write_text(
        dump_json(result.control_tree),
        encoding="utf-8",
    )
    (reports_dir / "diagnostics.json").write_text(
        dump_json([d.to_dict() for d in result.diagnostics]),
        encoding="utf-8",
    )
    (reports_dir / "README.md").write_text(
        _reports_readme(result, manifest_name=manifest_name),
        encoding="utf-8",
    )


def _reports_readme(result: GenerationResult, *, manifest_name: str) -> str:
    screens = ", ".join(result.yaml_by_screen.keys()) or "(none)"
    return f"""# Generation report — Candidate output

**STATUS: Studio-unvalidated Candidate**

Power Apps Studio remains the final validation authority.

| Field | Value |
|-------|-------|
| Manifest source | `{manifest_name}` (basename only; no absolute paths) |
| CanvasForge version | `{result.report["canvasforgeVersion"]}` |
| Build ID | `{result.build_id}` |
| Target adapter | `{result.report["targetAdapter"]}` |
| Screens | {screens} |
| Evidence status | documented bootstrap (no studio-exported fixture) |
| Studio validation status | unvalidated |
| Paste target | Power Apps Studio → select screen/container → Code View → paste Candidate YAML carefully |

## Required manual steps

1. Open a blank or sandbox Canvas app in Power Apps Studio.
2. Review `code-view/*.yaml` — do not edit generated files; change the manifest and regenerate.
3. Paste only after comparing against a known-good Studio export when available.
4. Record acceptance/rejection via `canvasforge evidence` workflow.
5. Never paste into production apps without review.

## Known limitations

- YAML structure is Candidate and may require Studio adjustments.
- OnSelect formulas are omitted until Studio-exported evidence exists.
- Galleries, forms, connectors, and packaging are out of scope for Phase 2.
- Generated files under `generated/` are gitignored by default.
"""
