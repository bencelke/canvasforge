"""In-memory project session for CanvasForge Studio."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from canvasforge.errors import Diagnostic
from canvasforge.generate.expander import build_app_ir
from canvasforge.generate.reports import compute_manifest_checksum
from canvasforge.ir.models import AppIR
from canvasforge.manifest.loader import load_manifest_dict
from canvasforge.manifest.models import AppManifest
from canvasforge.manifest.validator import parse_manifest
from canvasforge.studio.errors import StudioError, studio_error
from canvasforge.studio.models import PreviewApp, ProjectSummary
from canvasforge.studio.preview_service import build_preview_app
from canvasforge.studio.security import resolve_safe_manifest_path


@dataclass
class LoadedProject:
    manifest_path: Path
    manifest: AppManifest
    ir: AppIR
    diagnostics: list[Diagnostic]
    expanded: list[str]
    omitted: list[str]
    manifest_checksum: str
    allow_partial: bool
    preview: PreviewApp


@dataclass
class ProjectService:
    workspace_roots: list[Path]
    repo_root: Path
    current: LoadedProject | None = None
    session_builds: list[dict[str, Any]] = field(default_factory=list)

    def open_project(self, manifest_path: str, *, allow_partial: bool = True) -> ProjectSummary:
        path = resolve_safe_manifest_path(manifest_path, workspace_roots=self.workspace_roots)
        raw = path.read_bytes()
        checksum = compute_manifest_checksum(raw)
        data = load_manifest_dict(path)
        manifest = parse_manifest(data)
        ir, diagnostics, expanded, omitted = build_app_ir(
            manifest,
            allow_partial=allow_partial,
        )
        breakpoints = {
            "mobile": manifest.breakpoints.mobile,
            "tablet": manifest.breakpoints.tablet,
            "desktop": manifest.breakpoints.desktop,
        }
        unsupported_by_screen: dict[str, list[str]] = {
            manifest.app.start_screen: list(omitted),
        }
        preview = build_preview_app(
            ir,
            breakpoints=breakpoints,
            unsupported_by_screen=unsupported_by_screen,
            diagnostics=[d.to_dict() for d in diagnostics],
        )
        self.current = LoadedProject(
            manifest_path=path,
            manifest=manifest,
            ir=ir,
            diagnostics=diagnostics,
            expanded=expanded,
            omitted=omitted,
            manifest_checksum=checksum,
            allow_partial=allow_partial,
            preview=preview,
        )
        return self.summary()

    def require_current(self) -> LoadedProject:
        if self.current is None:
            raise StudioError(
                "No project loaded",
                diagnostics=[studio_error("STUDIO_NO_PROJECT", "Open a project first")],
            )
        return self.current

    def summary(self) -> ProjectSummary:
        project = self.require_current()
        manifest = project.manifest
        errors = [d for d in project.diagnostics if d.severity == "error"]
        state = "error" if errors else ("warning" if project.diagnostics else "valid")
        return ProjectSummary(
            projectKey=manifest.app.key,
            projectName=manifest.app.name,
            projectVersion=manifest.app.version,
            manifestVersion=manifest.app.manifest_version,
            manifestName=project.manifest_path.name,
            startScreen=manifest.app.start_screen,
            screens=[
                {
                    "key": screen.key,
                    "name": screen.name,
                    "title": screen.title,
                    "sectionCount": len(screen.sections),
                }
                for screen in manifest.screens
            ],
            dataSources=[
                {
                    "key": source.key,
                    "kind": source.kind,
                    "mode": source.mode,
                    "collection": source.collection,
                }
                for source in manifest.data_sources
            ],
            permissions=[
                {"key": permission.key, "description": permission.description}
                for permission in manifest.permissions
            ],
            breakpoints={
                "mobile": manifest.breakpoints.mobile,
                "tablet": manifest.breakpoints.tablet,
                "desktop": manifest.breakpoints.desktop,
            },
            validationState=state,
            diagnostics=[d.to_dict() for d in project.diagnostics],
            unsupportedSections=project.omitted,
        )

    def validate(self) -> list[dict[str, Any]]:
        project = self.require_current()
        data = load_manifest_dict(project.manifest_path)
        parse_manifest(data)
        ir, diagnostics, expanded, omitted = build_app_ir(
            project.manifest,
            allow_partial=project.allow_partial,
        )
        project.ir = ir
        project.diagnostics = diagnostics
        project.expanded = expanded
        project.omitted = omitted
        project.preview = build_preview_app(
            ir,
            breakpoints={
                "mobile": project.manifest.breakpoints.mobile,
                "tablet": project.manifest.breakpoints.tablet,
                "desktop": project.manifest.breakpoints.desktop,
            },
            unsupported_by_screen={project.manifest.app.start_screen: omitted},
            diagnostics=[d.to_dict() for d in diagnostics],
        )
        return [d.to_dict() for d in diagnostics]

    def demo_projects(self) -> list[dict[str, str]]:
        demos = [
            ("Hello CanvasForge", self.repo_root / "examples/hello-canvasforge/app.yaml"),
            (
                "O-Room Dashboard Proof",
                self.repo_root / "examples/oroom-actions/dashboard-proof.yaml",
            ),
        ]
        result: list[dict[str, str]] = []
        for label, path in demos:
            if path.is_file():
                result.append(
                    {
                        "label": label,
                        "manifestPath": path.relative_to(self.repo_root).as_posix(),
                    }
                )
        return result
