"""Pydantic models for Deployment Kit descriptors."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class CanvasForgeModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, populate_by_name=True)


class ProjectDescriptor(CanvasForgeModel):
    """Root ``canvasforge-project.json`` descriptor (schema 0.1)."""

    package_format: Literal["CanvasForgeDeploymentKit"] = Field(alias="packageFormat")
    package_schema_version: str = Field(alias="packageSchemaVersion")
    canvasforge_version: str = Field(alias="canvasforgeVersion")
    project_key: str = Field(alias="projectKey")
    project_name: str = Field(alias="projectName")
    project_version: str = Field(alias="projectVersion")
    manifest_version: str = Field(alias="manifestVersion")
    build_id: str = Field(alias="buildId")
    build_maturity: str = Field(alias="buildMaturity")
    target_adapter: str = Field(alias="targetAdapter")
    compatibility_profile_id: str = Field(alias="compatibilityProfileId")
    compatibility_profile_version: str = Field(alias="compatibilityProfileVersion")
    entry_manifest: str = Field(alias="entryManifest")
    generated_screens: list[str] = Field(alias="generatedScreens")
    generated_blocks: list[str] = Field(alias="generatedBlocks")
    included_features: list[str] = Field(alias="includedFeatures")
    excluded_features: list[str] = Field(alias="excludedFeatures")
    required_manual_steps: list[str] = Field(alias="requiredManualSteps")
    package_content_checksum: str = Field(alias="packageContentChecksum")
    reproducible: bool
    source_manifest_checksum: str = Field(alias="sourceManifestChecksum")
    package_created_by: Literal["CanvasForge"] = Field(alias="packageCreatedBy")
    security_classification: Literal["fictional-development"] = Field(
        alias="securityClassification"
    )
    contains_production_data: bool = Field(alias="containsProductionData")
    contains_credentials: bool = Field(alias="containsCredentials")
    contains_tenant_identifiers: bool = Field(alias="containsTenantIdentifiers")
    mock_data_included: bool = Field(alias="mockDataIncluded")
    mock_data_classification: str = Field(alias="mockDataClassification")
    notes: str = ""


class ForbiddenFinding(CanvasForgeModel):
    code: str
    severity: Literal["error", "warning"]
    path: str
    message: str
    redacted_excerpt: str = ""


class ForbiddenContentReport(CanvasForgeModel):
    status: Literal["pass", "pass-with-warnings", "fail"]
    finding_count: int = Field(alias="findingCount")
    blocking_count: int = Field(alias="blockingCount")
    warning_count: int = Field(alias="warningCount")
    findings: list[ForbiddenFinding]
    policy: str = (
        "Blocking findings prevent packaging. Credential and private-key findings "
        "cannot be bypassed. Warnings are recorded but do not block."
    )


class PackageManifestReport(CanvasForgeModel):
    """Inventory of members and omissions."""

    schema_version: str = Field(alias="schemaVersion")
    member_count: int = Field(alias="memberCount")
    members: list[str]
    omitted: list[dict[str, str]]
    reproducible: bool
    include_mock_data: bool = Field(alias="includeMockData")


class ValidationRecordTemplate(CanvasForgeModel):
    package_build_id: str = Field(default="", alias="packageBuildId")
    package_checksum: str = Field(default="", alias="packageChecksum")
    result: Literal["pending", "accepted", "accepted-with-modifications", "rejected"] = "pending"
    environment_class: str = Field(default="sandbox-unspecified", alias="environmentClass")
    studio_version: str = Field(default="", alias="studioVersion")
    tested_blocks: list[str] = Field(default_factory=list, alias="testedBlocks")
    accepted_blocks: list[str] = Field(default_factory=list, alias="acceptedBlocks")
    rejected_blocks: list[str] = Field(default_factory=list, alias="rejectedBlocks")
    error_categories: list[str] = Field(default_factory=list, alias="errorCategories")
    sanitized_errors: list[str] = Field(default_factory=list, alias="sanitizedErrors")
    manual_changes: list[str] = Field(default_factory=list, alias="manualChanges")
    tester_notes: str = Field(default="", alias="testerNotes")
    recorded_on: str = Field(default="", alias="recordedOn")


def dump_canonical_json(data: Any) -> str:
    """Stable JSON for kit members (sorted keys, LF, trailing newline)."""
    import json

    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
