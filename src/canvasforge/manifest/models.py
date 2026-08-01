"""Pydantic models for CanvasForge application manifests (v0.1)."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Key = Annotated[
    str,
    Field(
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z][A-Za-z0-9_-]*$",
        description="Stable identifier used for references.",
    ),
]

SUPPORTED_MANIFEST_VERSION = "0.1"

SectionType = Literal[
    "page-header",
    "summary-grid",
    "summary-card",
    "action-gallery",
    "search-toolbar",
    "detail-panel",
    "empty-state",
    "vertical-stack",
    "horizontal-stack",
]

STACK_SECTION_TYPES: frozenset[str] = frozenset({"vertical-stack", "horizontal-stack"})


class CanvasForgeModel(BaseModel):
    """Base model with strict defaults."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Theme(CanvasForgeModel):
    key: Key
    mode: Literal["light", "dark", "system"]
    tokens: dict[str, str] = Field(default_factory=dict)


class DataSource(CanvasForgeModel):
    key: Key
    kind: Literal["collection", "mock", "connector-deferred"]
    mode: Literal["offline-mock", "deferred"]
    collection: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = Field(default=None, max_length=2000)


class Permission(CanvasForgeModel):
    key: Key
    description: str | None = Field(default=None, max_length=2000)


class NavigationItem(CanvasForgeModel):
    key: Key
    label: str = Field(min_length=1, max_length=200)
    target_screen: Key = Field(alias="targetScreen")
    sort_order: int = Field(default=0, ge=0, alias="sortOrder")
    permission: Key | None = None
    implemented: bool = True

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, populate_by_name=True)


class Breakpoints(CanvasForgeModel):
    mobile: int = Field(default=640, ge=1)
    tablet: int = Field(default=1024, ge=1)
    desktop: int = Field(default=1440, ge=1)

    @model_validator(mode="after")
    def validate_ordering(self) -> Breakpoints:
        if not (self.mobile < self.tablet < self.desktop):
            raise ValueError("breakpoints must satisfy mobile < tablet < desktop")
        return self


class Metadata(CanvasForgeModel):
    tags: list[str] = Field(default_factory=list, max_length=50)
    owner: str | None = Field(default=None, max_length=200)
    created_for: str | None = Field(default=None, max_length=200, alias="createdFor")
    notes: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, populate_by_name=True)


class Section(CanvasForgeModel):
    """A UI section primitive. Does not emit Power Apps controls in Phase 1."""

    key: Key
    type: SectionType
    title: str | None = Field(default=None, max_length=200)
    data_source: Key | None = Field(default=None, alias="dataSource")
    layout: str | None = Field(default=None, max_length=128)
    properties: dict[str, Any] = Field(default_factory=dict)
    children: list[Section] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, populate_by_name=True)

    @model_validator(mode="after")
    def validate_children_allowed(self) -> Section:
        if self.children and self.type not in STACK_SECTION_TYPES:
            raise ValueError(
                f"section type '{self.type}' does not support children "
                "(only vertical-stack and horizontal-stack do)"
            )
        return self


class Screen(CanvasForgeModel):
    key: Key
    name: str = Field(min_length=1, max_length=200)
    title: str | None = Field(default=None, max_length=200)
    shell: str | None = Field(default=None, max_length=128)
    permissions: list[Key] = Field(default_factory=list)
    sections: list[Section] = Field(min_length=1)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, populate_by_name=True)


class AppInfo(CanvasForgeModel):
    key: Key
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    version: str = Field(min_length=1, max_length=64)
    manifest_version: str = Field(alias="manifestVersion")
    layout: str | None = Field(default=None, max_length=128)
    start_screen: Key = Field(alias="startScreen")
    theme: Key | None = None

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, populate_by_name=True)

    @field_validator("manifest_version")
    @classmethod
    def validate_manifest_version(cls, value: str) -> str:
        if value != SUPPORTED_MANIFEST_VERSION:
            raise ValueError(
                f"unsupported manifestVersion '{value}'; only '{SUPPORTED_MANIFEST_VERSION}' is supported"
            )
        return value


class AppManifest(CanvasForgeModel):
    """Root application manifest document."""

    app: AppInfo
    theme: Theme | None = None
    data_sources: list[DataSource] = Field(default_factory=list, alias="dataSources")
    screens: list[Screen] = Field(min_length=1)
    navigation: list[NavigationItem] = Field(default_factory=list)
    permissions: list[Permission] = Field(default_factory=list)
    breakpoints: Breakpoints = Field(default_factory=Breakpoints)
    metadata: Metadata | None = None

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, populate_by_name=True)

    def screen_keys(self) -> set[str]:
        return {screen.key for screen in self.screens}

    def data_source_keys(self) -> set[str]:
        return {source.key for source in self.data_sources}

    def permission_keys(self) -> set[str]:
        return {permission.key for permission in self.permissions}


# Rebuild for forward refs on recursive Section.children
Section.model_rebuild()
