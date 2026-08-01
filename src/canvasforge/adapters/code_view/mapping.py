"""Code View adapter mapping and serialization helpers."""

from __future__ import annotations

from typing import Any

from canvasforge.controls.registry import ControlRegistry
from canvasforge.errors import Diagnostic, GenerationError
from canvasforge.ir.models import ControlNode, PropertyValue


def property_code_view_name(
    registry: ControlRegistry,
    control_type: str,
    prop: PropertyValue,
) -> str:
    spec = registry.assert_property_generatable(control_type, prop.name)
    return spec.code_view_name or prop.name


def serialize_property_value(prop: PropertyValue) -> Any:
    if prop.kind == "formula":
        value = prop.value
        if isinstance(value, str):
            return value if value.startswith("=") else f"={value}"
        return f"={value}"
    return prop.value


def node_to_code_view_dict(node: ControlNode, registry: ControlRegistry) -> dict[str, Any]:
    """Convert a ControlNode into a Candidate Code View mapping."""
    control = registry.assert_generatable(node.control_type)
    properties: dict[str, Any] = {}
    for prop in node.properties:
        cv_name = property_code_view_name(registry, node.control_type, prop)
        properties[cv_name] = serialize_property_value(prop)

    # Ensure LayoutDirection is present for containers from layout metadata
    if node.layout and node.layout.direction and "LayoutDirection" not in properties:
        properties["LayoutDirection"] = (
            "Vertical" if node.layout.direction == "vertical" else "Horizontal"
        )

    children = [node_to_code_view_dict(child, registry) for child in node.children]
    payload: dict[str, Any] = {
        "Name": node.name,
        "Control": control.code_view_identifier,
        "Properties": properties,
    }
    if children:
        payload["Children"] = children

    # Traceability kept outside YAML emission — adapter metadata only
    payload["_CanvasForge"] = {
        "logicalType": node.control_type,
        "id": node.id,
        "sourcePath": node.source.path,
        "generationStatus": node.generation_status,
        "evidenceStatus": node.evidence_status,
    }
    return payload


def strip_trace_metadata(node: dict[str, Any]) -> dict[str, Any]:
    """Remove CanvasForge trace keys from YAML-bound structures."""
    cleaned = {key: value for key, value in node.items() if key != "_CanvasForge"}
    if "Children" in cleaned:
        cleaned["Children"] = [strip_trace_metadata(child) for child in cleaned["Children"]]
    return cleaned


def validate_unknown_properties(node: ControlNode, registry: ControlRegistry) -> None:
    """Fail closed on unknown properties."""
    for prop in node.properties:
        try:
            registry.assert_property_generatable(node.control_type, prop.name)
        except GenerationError:
            raise
    for child in node.children:
        validate_unknown_properties(child, registry)


def collect_adapter_diagnostics(
    node: ControlNode,
    registry: ControlRegistry,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    try:
        registry.assert_generatable(node.control_type)
    except GenerationError as exc:
        diagnostics.extend(exc.diagnostics)
    for prop in node.properties:
        try:
            registry.assert_property_generatable(node.control_type, prop.name)
        except GenerationError as exc:
            diagnostics.extend(exc.diagnostics)
    for child in node.children:
        diagnostics.extend(collect_adapter_diagnostics(child, registry))
    return diagnostics
