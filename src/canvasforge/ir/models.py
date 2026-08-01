"""Normalized internal representation for CanvasForge generation."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

EvidenceStatus = Literal[
    "documented",
    "studio-exported",
    "studio-validated",
    "inferred",
    "unsupported",
]

GenerationStatus = Literal["candidate", "blocked", "omitted"]

PropertyKind = Literal["literal", "formula", "layout"]


class SourceReference(BaseModel):
    """Traceability from a generated node back to the manifest."""

    model_config = ConfigDict(extra="forbid")

    path: str
    app_key: str
    screen_key: str | None = None
    section_key: str | None = None
    role: str | None = None


class PropertyValue(BaseModel):
    """A typed property assignment on a control node."""

    model_config = ConfigDict(extra="forbid")

    name: str
    kind: PropertyKind
    value: str | int | float | bool
    evidence_status: EvidenceStatus = "documented"


class FormulaValue(BaseModel):
    """A formula-valued property (Power Fx candidate string)."""

    model_config = ConfigDict(extra="forbid")

    name: str
    expression: str
    evidence_status: EvidenceStatus = "documented"


class LayoutValue(BaseModel):
    """Layout-oriented property grouping for containers."""

    model_config = ConfigDict(extra="forbid")

    direction: Literal["vertical", "horizontal"] | None = None
    gap: int | None = None
    padding: tuple[int, int, int, int] | None = None
    fill_portions: int | None = None


class ControlNode(BaseModel):
    """A single node in the normalized control tree."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    control_type: str
    parent_id: str | None = None
    children: list[ControlNode] = Field(default_factory=list)
    properties: list[PropertyValue] = Field(default_factory=list)
    formulas: list[FormulaValue] = Field(default_factory=list)
    layout: LayoutValue | None = None
    source: SourceReference
    generation_status: GenerationStatus = "candidate"
    evidence_status: EvidenceStatus = "documented"
    notes: str | None = None


class ScreenIR(BaseModel):
    """Normalized screen representation."""

    model_config = ConfigDict(extra="forbid")

    key: str
    name: str
    title: str | None = None
    source_path: str
    root: ControlNode


class AppIR(BaseModel):
    """Normalized application IR produced from a validated manifest."""

    model_config = ConfigDict(extra="forbid")

    app_key: str
    app_name: str
    app_version: str
    manifest_version: str
    screens: list[ScreenIR] = Field(default_factory=list)
    theme_tokens: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GenerationDiagnostic(BaseModel):
    """Structured generation diagnostic."""

    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    path: str = "$"
    severity: Literal["error", "warning", "info"] = "error"
    hint: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class GenerationArtifact(BaseModel):
    """A generated file artifact descriptor."""

    model_config = ConfigDict(extra="forbid")

    kind: str
    relative_path: str
    content_type: str
    deterministic: bool = True


class GenerationPlanStep(BaseModel):
    """One expansion/adaptation step in the generation plan."""

    model_config = ConfigDict(extra="forbid")

    index: int
    action: str
    target: str
    detail: str


class GenerationPlan(BaseModel):
    """Deterministic generation plan for a build."""

    model_config = ConfigDict(extra="forbid")

    build_id: str
    app_key: str
    target: str
    steps: list[GenerationPlanStep] = Field(default_factory=list)


# Rebuild for recursive children
ControlNode.model_rebuild()
