"""FastAPI application for CanvasForge Studio."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from canvasforge import __version__
from canvasforge.controls.builtins import (
    GENERATABLE_SECTION_TYPES,
    NON_GENERATABLE_SECTION_TYPES,
)
from canvasforge.errors import CanvasForgeError
from canvasforge.studio import STUDIO_API_VERSION
from canvasforge.studio.build_service import package_current_project
from canvasforge.studio.models import (
    CapabilitiesResponse,
    HealthResponse,
    OpenProjectRequest,
    PackageRequest,
)
from canvasforge.studio.project_service import ProjectService
from canvasforge.studio.security import (
    assert_loopback_host,
    default_workspace_roots,
    resolve_repo_root,
)

FRONTEND_DIST_CANDIDATES = (
    Path(__file__).resolve().parents[3] / "studio" / "dist",
    Path.cwd() / "studio" / "dist",
)


def create_app(
    *,
    host: str = "127.0.0.1",
    cors_origins: list[str] | None = None,
    project_path: str | None = None,
    allow_partial: bool = True,
) -> FastAPI:
    assert_loopback_host(host)
    repo_root = resolve_repo_root()
    roots = default_workspace_roots(repo_root)
    dist_dir = (repo_root / "dist").resolve()
    dist_dir.mkdir(parents=True, exist_ok=True)

    service = ProjectService(workspace_roots=roots, repo_root=repo_root)
    app = FastAPI(
        title="CanvasForge Studio API",
        version=STUDIO_API_VERSION,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.service = service
    app.state.repo_root = repo_root
    app.state.dist_dir = dist_dir
    app.state.host = host

    origins = cors_origins or [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:8765",
        "http://localhost:8765",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    @app.exception_handler(CanvasForgeError)
    async def canvasforge_error_handler(_request: Request, exc: CanvasForgeError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "error": exc.message,
                "diagnostics": [d.to_dict() for d in exc.diagnostics],
            },
        )

    @app.get("/api/v1/health")
    def health() -> dict[str, Any]:
        current = service.current.manifest.app.key if service.current else None
        payload = HealthResponse(
            canvasforgeVersion=__version__,
            studioApiVersion=STUDIO_API_VERSION,
            offlineMode=True,
            currentProject=current,
        )
        return payload.model_dump(mode="json", by_alias=True)

    @app.get("/api/v1/studio/capabilities")
    def capabilities() -> dict[str, Any]:
        payload = CapabilitiesResponse(
            supportedPreviewTypes=[
                "screen",
                "vertical-container",
                "horizontal-container",
                "text",
                "button",
                "summary-grid",
                "summary-card",
                "empty-state",
                "unsupported-placeholder",
            ],
            unsupportedPreviewTypes=sorted(NON_GENERATABLE_SECTION_TYPES),
            canvasControlMaturity="documented-bootstrap-candidate",
            deploymentTargets=["code-view"],
            featureFlags={
                "aiPrompting": False,
                "dragDropEditing": False,
                "microsoftAuth": False,
                "msapp": False,
                "runner": False,
            },
            demoProjects=service.demo_projects(),
        )
        # Include generatable section list for UI hints
        data = payload.model_dump(mode="json", by_alias=True)
        data["generatableSections"] = sorted(GENERATABLE_SECTION_TYPES)
        return data

    @app.post("/api/v1/projects/open")
    def open_project(body: OpenProjectRequest) -> dict[str, Any]:
        summary = service.open_project(body.manifestPath, allow_partial=body.allowPartial)
        return summary.model_dump(mode="json", by_alias=True)

    @app.get("/api/v1/projects/current")
    def current_project() -> dict[str, Any]:
        return service.summary().model_dump(mode="json", by_alias=True)

    @app.get("/api/v1/projects/current/screens")
    def list_screens() -> dict[str, Any]:
        summary = service.summary()
        return {"screens": summary.screens}

    @app.get("/api/v1/projects/current/screens/{screen_key}")
    def get_screen(screen_key: str) -> dict[str, Any]:
        project = service.require_current()
        preview_screen = next(
            (screen for screen in project.preview.screens if screen.key == screen_key),
            None,
        )
        if preview_screen is None:
            raise HTTPException(status_code=404, detail=f"Screen '{screen_key}' not found")
        ir_screen = next((s for s in project.ir.screens if s.key == screen_key), None)
        return {
            "key": screen_key,
            "name": preview_screen.name,
            "title": preview_screen.title,
            "preview": preview_screen.model_dump(mode="json", by_alias=True),
            "controlTree": ir_screen.root.model_dump(mode="json") if ir_screen else None,
            "unsupportedSections": preview_screen.unsupported_sections,
            "diagnostics": [d.model_dump(mode="json") for d in preview_screen.diagnostics],
            "disclaimer": project.preview.disclaimer,
        }

    @app.post("/api/v1/projects/current/validate")
    def validate_project() -> dict[str, Any]:
        diagnostics = service.validate()
        return {
            "diagnostics": diagnostics,
            "summary": service.summary().model_dump(mode="json", by_alias=True),
        }

    @app.post("/api/v1/projects/current/package")
    def package_project(body: PackageRequest) -> dict[str, Any]:
        result = package_current_project(
            service,
            output=body.output,
            include_mock_data=body.includeMockData,
            screen=body.screen,
            allow_partial=body.allowPartial,
            overwrite=body.overwrite,
            dist_dir=dist_dir,
        )
        return result.model_dump(mode="json", by_alias=True)

    @app.get("/api/v1/projects/current/builds")
    def list_builds() -> dict[str, Any]:
        return {"builds": service.session_builds}

    if project_path:
        service.open_project(project_path, allow_partial=allow_partial)

    frontend_dist = next((path for path in FRONTEND_DIST_CANDIDATES if path.is_dir()), None)
    if frontend_dist is not None:
        assets = frontend_dist / "assets"
        if assets.is_dir():
            app.mount("/assets", StaticFiles(directory=assets), name="assets")

        @app.get("/")
        def index() -> FileResponse:
            return FileResponse(frontend_dist / "index.html")

        @app.get("/{full_path:path}")
        def spa_fallback(full_path: str) -> FileResponse:
            candidate = frontend_dist / full_path
            if candidate.is_file() and frontend_dist in candidate.resolve().parents:
                return FileResponse(candidate)
            return FileResponse(frontend_dist / "index.html")

    return app


# Default ASGI app for uvicorn canvasforge.studio.app:app
app = create_app()
