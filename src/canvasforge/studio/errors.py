"""Studio-specific errors."""

from __future__ import annotations

from canvasforge.errors import CanvasForgeError, Diagnostic


class StudioError(CanvasForgeError):
    """Raised for Studio API / security failures."""


def studio_error(code: str, message: str, *, path: str = "$") -> Diagnostic:
    return Diagnostic(code=code, message=message, path=path, severity="error")
