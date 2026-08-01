"""Compatibility helpers for parent/child rules."""

from __future__ import annotations

from canvasforge.controls.registry import ControlRegistry
from canvasforge.errors import Diagnostic, GenerationError
from canvasforge.ir.models import ControlNode


def validate_tree_compatibility(root: ControlNode, registry: ControlRegistry) -> list[Diagnostic]:
    """Validate parent/child allowlist relationships. Returns diagnostics (may be empty)."""
    diagnostics: list[Diagnostic] = []

    def walk(node: ControlNode, parent: ControlNode | None) -> None:
        spec = registry.assert_generatable(node.control_type)
        if parent is None:
            if node.control_type != "Screen":
                diagnostics.append(
                    Diagnostic(
                        code="INVALID_ROOT_CONTROL",
                        message=f"Root control must be Screen, got '{node.control_type}'",
                        path=node.source.path,
                    )
                )
        else:
            parent_spec = registry.get(parent.control_type)
            if node.control_type not in parent_spec.allowed_children:
                diagnostics.append(
                    Diagnostic(
                        code="INVALID_CHILD_TYPE",
                        message=(
                            f"'{node.control_type}' is not an allowed child of "
                            f"'{parent.control_type}'"
                        ),
                        path=node.source.path,
                    )
                )
            if parent.control_type not in spec.allowed_parents and spec.allowed_parents:
                diagnostics.append(
                    Diagnostic(
                        code="INVALID_PARENT_TYPE",
                        message=(
                            f"'{node.control_type}' does not allow parent '{parent.control_type}'"
                        ),
                        path=node.source.path,
                    )
                )
        for child in node.children:
            walk(child, node)

    walk(root, None)
    return diagnostics


def ensure_compatible(root: ControlNode, registry: ControlRegistry) -> None:
    diagnostics = validate_tree_compatibility(root, registry)
    errors = [d for d in diagnostics if d.severity == "error"]
    if errors:
        raise GenerationError("Control tree failed compatibility validation", diagnostics=errors)
