"""Deterministic Power Apps control naming."""

from __future__ import annotations

import re

from canvasforge.errors import Diagnostic, GenerationError

MAX_CONTROL_NAME_LENGTH = 60
_INVALID_RE = re.compile(r"[^A-Za-z0-9_]")
_PREFIXES = {
    "VerticalContainer": "con",
    "HorizontalContainer": "con",
    "Text": "lbl",
    "Button": "btn",
    "Screen": "scr",
}

# Reserved / commonly conflicting Studio names (documented awareness only)
RESERVED_NAMES: frozenset[str] = frozenset(
    {
        "App",
        "Parent",
        "Self",
        "ThisItem",
        "Screen",
        "Host",
    }
)


def _pascal_case(value: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", value)
    return "".join(part[:1].upper() + part[1:] for part in parts if part)


def sanitize_control_name(raw: str) -> str:
    """Remove invalid characters and enforce length."""
    cleaned = _INVALID_RE.sub("", raw)
    if not cleaned:
        cleaned = "Control"
    if cleaned[0].isdigit():
        cleaned = f"C{cleaned}"
    return cleaned[:MAX_CONTROL_NAME_LENGTH]


def build_control_name(control_type: str, *role_parts: str) -> str:
    """Build a deterministic control name with known prefixes."""
    prefix = _PREFIXES.get(control_type, "ctl")
    suffix = _pascal_case("".join(role_parts))
    if control_type == "Screen":
        # Screens often already include scr prefix in manifest keys
        name = sanitize_control_name(suffix or "Screen")
        if not name.lower().startswith("scr"):
            name = sanitize_control_name(f"scr{name}")
        return name
    return sanitize_control_name(f"{prefix}{suffix}")


class NameAllocator:
    """Allocate unique control names with collision detection."""

    def __init__(self) -> None:
        self._used: set[str] = set()
        self._diagnostics: list[Diagnostic] = []

    @property
    def diagnostics(self) -> list[Diagnostic]:
        return list(self._diagnostics)

    def is_used(self, name: str) -> bool:
        return name in self._used

    def allocate(
        self,
        control_type: str,
        *role_parts: str,
        source_path: str = "$",
        preferred: str | None = None,
    ) -> str:
        if preferred is not None:
            name = sanitize_control_name(preferred)
        else:
            name = build_control_name(control_type, *role_parts)
        if name in RESERVED_NAMES:
            self._diagnostics.append(
                Diagnostic(
                    code="RESERVED_CONTROL_NAME",
                    message=f"Control name '{name}' is reserved",
                    path=source_path,
                    severity="error",
                    hint="Adjust section keys to avoid reserved Studio names",
                )
            )
            raise GenerationError(
                f"Reserved control name '{name}'",
                diagnostics=self._diagnostics,
            )
        if name in self._used:
            self._diagnostics.append(
                Diagnostic(
                    code="DUPLICATE_CONTROL_NAME",
                    message=f"Duplicate control name '{name}'",
                    path=source_path,
                    severity="error",
                    hint="Section keys must expand to unique Power Apps control names",
                )
            )
            raise GenerationError(
                f"Duplicate control name '{name}'",
                diagnostics=self._diagnostics,
            )
        self._used.add(name)
        return name
