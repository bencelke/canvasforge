"""Control registry lookup and generation policy."""

from __future__ import annotations

from functools import lru_cache

from canvasforge.controls.builtins import builtin_controls
from canvasforge.controls.models import ControlSpec, EvidenceStatus, PropertySpec
from canvasforge.errors import Diagnostic, GenerationError

_ALLOWED_FOR_GENERATION: frozenset[EvidenceStatus] = frozenset(
    {"studio-validated", "studio-exported", "documented"}
)


class ControlRegistry:
    """Versioned in-memory control allowlist."""

    def __init__(self, controls: list[ControlSpec] | None = None) -> None:
        self._controls = {spec.logical_name: spec for spec in (controls or builtin_controls())}

    def list_controls(self) -> list[ControlSpec]:
        return [self._controls[key] for key in sorted(self._controls)]

    def get(self, logical_name: str) -> ControlSpec:
        try:
            return self._controls[logical_name]
        except KeyError as exc:
            raise GenerationError(
                f"Unknown logical control type '{logical_name}'",
                diagnostics=[
                    Diagnostic(
                        code="UNKNOWN_CONTROL_TYPE",
                        message=f"Control type '{logical_name}' is not in the allowlist",
                        path=f"$.controls.{logical_name}",
                        hint="Use canvasforge controls to list supported types",
                    )
                ],
            ) from exc

    def get_property(self, logical_name: str, property_name: str) -> PropertySpec:
        control = self.get(logical_name)
        for prop in control.properties:
            if prop.name == property_name:
                return prop
        raise GenerationError(
            f"Unknown property '{property_name}' on '{logical_name}'",
            diagnostics=[
                Diagnostic(
                    code="UNKNOWN_PROPERTY",
                    message=(
                        f"Property '{property_name}' is not allowlisted for control "
                        f"'{logical_name}'"
                    ),
                    path=f"$.controls.{logical_name}.properties.{property_name}",
                    hint="Fail closed: do not emit unsupported properties",
                )
            ],
        )

    def assert_generatable(self, logical_name: str) -> ControlSpec:
        control = self.get(logical_name)
        if control.evidence_status not in _ALLOWED_FOR_GENERATION:
            raise GenerationError(
                f"Control '{logical_name}' blocked by evidence policy",
                diagnostics=[
                    Diagnostic(
                        code="CONTROL_EVIDENCE_BLOCKED",
                        message=(
                            f"Evidence status '{control.evidence_status}' is not allowed "
                            "for generation"
                        ),
                        path=f"$.controls.{logical_name}",
                        hint="Only documented, studio-exported, or studio-validated controls generate",
                    )
                ],
            )
        return control

    def assert_property_generatable(self, logical_name: str, property_name: str) -> PropertySpec:
        prop = self.get_property(logical_name, property_name)
        if prop.evidence_status not in _ALLOWED_FOR_GENERATION:
            raise GenerationError(
                f"Property '{property_name}' blocked by evidence policy",
                diagnostics=[
                    Diagnostic(
                        code="PROPERTY_EVIDENCE_BLOCKED",
                        message=(
                            f"Property '{property_name}' on '{logical_name}' has evidence "
                            f"status '{prop.evidence_status}'"
                        ),
                        path=f"$.controls.{logical_name}.properties.{property_name}",
                    )
                ],
            )
        return prop


@lru_cache(maxsize=1)
def default_registry() -> ControlRegistry:
    return ControlRegistry()
