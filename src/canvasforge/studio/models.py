"""API and preview models for CanvasForge Studio."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class HealthResponse(ApiModel):
    status: Literal["ok"] = "ok"
    canvasforge_version: str = Field(alias="canvasforgeVersion")
    studio_api_version: str = Field(alias="studioApiVersion")
    offline_mode: bool = Field(alias="offlineMode")
    current_project: str | None = Field(default=None, alias="currentProject")


class OpenProjectRequest(ApiModel):
    """Request body uses camelCase field names for FastAPI body parsing (no Field aliases)."""

    manifestPath: str
    allowPartial: bool = True


class PackageRequest(ApiModel):
    """Request body uses camelCase field names for FastAPI body parsing (no Field aliases)."""

    output: str | None = None
    includeMockData: bool = False
    screen: str | None = None
    allowPartial: bool = True
    overwrite: bool = True


class PreviewStyle(ApiModel):
    fill: str | None = None
    color: str | None = None
    font_size: int | None = Field(default=None, alias="fontSize")
    font_weight: str | None = Field(default=None, alias="fontWeight")
    padding: str | None = None
    gap: int | None = None
    width: str | None = None
    height: str | None = None
    border: str | None = None
    border_radius: int | None = Field(default=None, alias="borderRadius")
    flex_direction: Literal["row", "column"] | None = Field(default=None, alias="flexDirection")
    align_items: str | None = Field(default=None, alias="alignItems")
    justify_content: str | None = Field(default=None, alias="justifyContent")


class PreviewDiagnostic(ApiModel):
    code: str
    message: str
    severity: Literal["error", "warning", "info"] = "warning"
    path: str = "$"


class PreviewNode(ApiModel):
    id: str
    name: str
    type: str
    source_path: str = Field(alias="sourcePath")
    children: list[PreviewNode] = Field(default_factory=list)
    text: str | None = None
    styles: PreviewStyle = Field(default_factory=PreviewStyle)
    layout: dict[str, Any] = Field(default_factory=dict)
    accessibility: dict[str, str] = Field(default_factory=dict)
    binding_summary: str | None = Field(default=None, alias="bindingSummary")
    maturity: str = "candidate"
    expected_control: str | None = Field(default=None, alias="expectedControl")
    diagnostics: list[PreviewDiagnostic] = Field(default_factory=list)


class PreviewScreen(ApiModel):
    key: str
    name: str
    title: str | None = None
    root: PreviewNode
    unsupported_sections: list[str] = Field(default_factory=list, alias="unsupportedSections")
    diagnostics: list[PreviewDiagnostic] = Field(default_factory=list)


class PreviewApp(ApiModel):
    app_key: str = Field(alias="appKey")
    app_name: str = Field(alias="appName")
    theme_tokens: dict[str, str] = Field(default_factory=dict, alias="themeTokens")
    breakpoints: dict[str, int] = Field(default_factory=dict)
    screens: list[PreviewScreen] = Field(default_factory=list)
    disclaimer: str = "Local Preview — Power Apps Studio validation required"


class ProjectSummary(ApiModel):
    project_key: str = Field(alias="projectKey")
    project_name: str = Field(alias="projectName")
    project_version: str = Field(alias="projectVersion")
    manifest_version: str = Field(alias="manifestVersion")
    manifest_name: str = Field(alias="manifestName")
    start_screen: str = Field(alias="startScreen")
    screens: list[dict[str, Any]]
    data_sources: list[dict[str, Any]] = Field(alias="dataSources")
    permissions: list[dict[str, Any]]
    breakpoints: dict[str, int]
    validation_state: str = Field(alias="validationState")
    diagnostics: list[dict[str, Any]]
    unsupported_sections: list[str] = Field(default_factory=list, alias="unsupportedSections")
    maturity: str = "Candidate-StudioUnvalidated"
    offline: bool = True


class PackageResult(ApiModel):
    build_id: str = Field(alias="buildId")
    output_name: str = Field(alias="outputName")
    package_content_checksum: str = Field(alias="packageContentChecksum")
    size_bytes: int = Field(alias="sizeBytes")
    maturity: str
    verified: bool
    security_status: str = Field(alias="securityStatus")
    members: list[str]
    warnings: list[str] = Field(default_factory=list)


class SessionBuild(ApiModel):
    build_id: str = Field(alias="buildId")
    output_name: str = Field(alias="outputName")
    package_content_checksum: str = Field(alias="packageContentChecksum")
    size_bytes: int = Field(alias="sizeBytes")
    verified: bool
    maturity: str


class CapabilitiesResponse(ApiModel):
    supported_preview_types: list[str] = Field(alias="supportedPreviewTypes")
    unsupported_preview_types: list[str] = Field(alias="unsupportedPreviewTypes")
    canvas_control_maturity: str = Field(alias="canvasControlMaturity")
    deployment_targets: list[str] = Field(alias="deploymentTargets")
    feature_flags: dict[str, bool] = Field(alias="featureFlags")
    demo_projects: list[dict[str, str]] = Field(alias="demoProjects")
