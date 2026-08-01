"""Structured error types for CanvasForge."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Severity = Literal["error", "warning", "info"]


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """A structured, path-associated diagnostic message."""

    code: str
    message: str
    path: str = "$"
    severity: Severity = "error"
    hint: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def format_terminal(self) -> str:
        """Render a human-readable terminal line."""
        base = f"[{self.severity}] {self.code} at {self.path}: {self.message}"
        if self.hint:
            return f"{base} ({self.hint})"
        return base

    def to_dict(self) -> dict[str, Any]:
        """Serialize for future machine consumption."""
        payload: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
            "path": self.path,
            "severity": self.severity,
        }
        if self.hint is not None:
            payload["hint"] = self.hint
        if self.details:
            payload["details"] = self.details
        return payload


class CanvasForgeError(Exception):
    """Base error for CanvasForge."""

    def __init__(self, message: str, *, diagnostics: list[Diagnostic] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.diagnostics: list[Diagnostic] = diagnostics or []

    def format_terminal(self) -> str:
        lines = [self.message]
        lines.extend(d.format_terminal() for d in self.diagnostics)
        return "\n".join(lines)


class ManifestLoadError(CanvasForgeError):
    """Raised when a manifest cannot be loaded safely."""


class ManifestValidationError(CanvasForgeError):
    """Raised when schema or semantic validation fails."""


class GenerationError(CanvasForgeError):
    """Raised when IR expansion or adapter generation fails."""


class EvidenceError(CanvasForgeError):
    """Raised when evidence import or validation recording fails."""
