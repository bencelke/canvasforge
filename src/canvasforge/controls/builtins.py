"""Bootstrap control allowlist for Phase 2 Candidate generation.

Evidence status policy:
- studio-validated: allowed
- studio-exported: allowed as Candidate
- documented: allowed as Candidate
- inferred: blocked by default
- unsupported: blocked

No Studio-exported fixtures exist in this repository yet. Bootstrap entries are
marked documented based on publicly documented Canvas control concepts.
Exact Code View YAML shape remains Candidate / Studio-unvalidated.
"""

from __future__ import annotations

from canvasforge.controls.models import ControlSpec, PropertySpec

_COMMON = [
    PropertySpec(
        name="Width",
        category="common",
        evidence_status="documented",
        code_view_name="Width",
        value_kind="formula",
    ),
    PropertySpec(
        name="Height",
        category="common",
        evidence_status="documented",
        code_view_name="Height",
        value_kind="formula",
    ),
    PropertySpec(
        name="Fill",
        category="common",
        evidence_status="documented",
        code_view_name="Fill",
        value_kind="formula",
    ),
    PropertySpec(
        name="Visible", category="common", evidence_status="documented", code_view_name="Visible"
    ),
]

_CONTAINER = [
    PropertySpec(
        name="LayoutDirection",
        category="container",
        evidence_status="documented",
        code_view_name="LayoutDirection",
        notes="Candidate mapping for GroupContainer layout orientation.",
    ),
    PropertySpec(
        name="LayoutGap",
        category="container",
        evidence_status="documented",
        code_view_name="LayoutGap",
    ),
    PropertySpec(name="PaddingTop", category="container", evidence_status="documented"),
    PropertySpec(name="PaddingRight", category="container", evidence_status="documented"),
    PropertySpec(name="PaddingBottom", category="container", evidence_status="documented"),
    PropertySpec(name="PaddingLeft", category="container", evidence_status="documented"),
    PropertySpec(name="AlignInContainer", category="container", evidence_status="documented"),
    PropertySpec(name="FillPortions", category="container", evidence_status="documented"),
]

_TEXT = [
    PropertySpec(name="Text", category="text", evidence_status="documented", value_kind="formula"),
    PropertySpec(name="Size", category="text", evidence_status="documented"),
    PropertySpec(name="FontWeight", category="text", evidence_status="documented"),
    PropertySpec(name="Color", category="text", evidence_status="documented", value_kind="formula"),
    PropertySpec(name="Align", category="text", evidence_status="documented"),
    PropertySpec(name="Wrap", category="text", evidence_status="documented"),
    PropertySpec(name="AccessibleLabel", category="text", evidence_status="documented"),
]

_BUTTON = [
    PropertySpec(
        name="Text", category="button", evidence_status="documented", value_kind="formula"
    ),
    PropertySpec(name="AccessibleLabel", category="button", evidence_status="documented"),
    PropertySpec(
        name="DisplayMode",
        category="button",
        evidence_status="documented",
        value_kind="formula",
    ),
    # OnSelect intentionally not allowlisted until Studio-exported evidence exists.
]


def builtin_controls() -> list[ControlSpec]:
    """Return the Phase 2 bootstrap control registry."""
    return [
        ControlSpec(
            logical_name="Screen",
            code_view_identifier="Screen",
            evidence_status="documented",
            allowed_parents=[],
            allowed_children=["VerticalContainer", "HorizontalContainer", "Text", "Button"],
            properties=[
                PropertySpec(
                    name="Fill",
                    category="screen",
                    evidence_status="documented",
                    value_kind="formula",
                ),
                PropertySpec(name="Width", category="screen", evidence_status="documented"),
                PropertySpec(name="Height", category="screen", evidence_status="documented"),
            ],
            notes="Candidate Screen node for Code View paste. Studio-unvalidated.",
        ),
        ControlSpec(
            logical_name="VerticalContainer",
            code_view_identifier="GroupContainer",
            evidence_status="documented",
            allowed_parents=["Screen", "VerticalContainer", "HorizontalContainer"],
            allowed_children=["VerticalContainer", "HorizontalContainer", "Text", "Button"],
            properties=[*_COMMON, *_CONTAINER],
            notes="Mapped to GroupContainer with LayoutDirection=Vertical. Candidate.",
        ),
        ControlSpec(
            logical_name="HorizontalContainer",
            code_view_identifier="GroupContainer",
            evidence_status="documented",
            allowed_parents=["Screen", "VerticalContainer", "HorizontalContainer"],
            allowed_children=["VerticalContainer", "HorizontalContainer", "Text", "Button"],
            properties=[*_COMMON, *_CONTAINER],
            notes="Mapped to GroupContainer with LayoutDirection=Horizontal. Candidate.",
        ),
        ControlSpec(
            logical_name="Text",
            code_view_identifier="Label",
            evidence_status="documented",
            allowed_parents=["Screen", "VerticalContainer", "HorizontalContainer"],
            allowed_children=[],
            properties=[*_COMMON, *_TEXT],
            formula_properties=["Text", "Color"],
            notes="Mapped to classic Label control identifier as Candidate.",
        ),
        ControlSpec(
            logical_name="Button",
            code_view_identifier="Button",
            evidence_status="documented",
            allowed_parents=["Screen", "VerticalContainer", "HorizontalContainer"],
            allowed_children=[],
            properties=[*_COMMON, *_BUTTON],
            formula_properties=["Text", "DisplayMode"],
            notes="OnSelect omitted until Studio-exported evidence exists.",
        ),
    ]


GENERATABLE_SECTION_TYPES: frozenset[str] = frozenset(
    {
        "page-header",
        "summary-grid",
        "summary-card",
        "empty-state",
        "vertical-stack",
        "horizontal-stack",
    }
)

NON_GENERATABLE_SECTION_TYPES: frozenset[str] = frozenset(
    {
        "action-gallery",
        "search-toolbar",
        "detail-panel",
    }
)
