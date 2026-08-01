"""Control registry and evidence models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

EvidenceStatus = Literal[
    "documented",
    "studio-exported",
    "studio-validated",
    "inferred",
    "unsupported",
]

PropertyCategory = Literal["common", "container", "text", "button", "screen"]


class PropertySpec(BaseModel):
    """Allowlisted property for a logical control type."""

    model_config = ConfigDict(extra="forbid")

    name: str
    category: PropertyCategory
    value_kind: Literal["literal", "formula", "layout"] = "literal"
    evidence_status: EvidenceStatus
    code_view_name: str | None = None
    notes: str | None = None


class ControlSpec(BaseModel):
    """Allowlisted logical control type."""

    model_config = ConfigDict(extra="forbid")

    logical_name: str
    code_view_identifier: str
    evidence_status: EvidenceStatus
    allowed_parents: list[str] = Field(default_factory=list)
    allowed_children: list[str] = Field(default_factory=list)
    properties: list[PropertySpec] = Field(default_factory=list)
    formula_properties: list[str] = Field(default_factory=list)
    notes: str | None = None


class EvidenceRecord(BaseModel):
    """Explicit evidence record for a control and/or property."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    evidence_id: str = Field(alias="evidenceId")
    control_type: str = Field(alias="controlType")
    property: str | None = None
    source_type: Literal[
        "official-documentation",
        "studio-export",
        "studio-round-trip",
        "test-fixture",
    ] = Field(alias="sourceType")
    source_reference: str = Field(alias="sourceReference")
    studio_accepted: bool | None = Field(default=None, alias="studioAccepted")
    studio_version: str | None = Field(default=None, alias="studioVersion")
    environment_class: Literal["commercial", "government", "unknown"] = Field(
        default="unknown",
        alias="environmentClass",
    )
    notes: str | None = None
    recorded_on: str = Field(alias="recordedOn")
    checksum: str
