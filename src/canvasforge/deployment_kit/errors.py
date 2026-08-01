"""Deployment kit specific errors."""

from __future__ import annotations

from canvasforge.errors import CanvasForgeError, Diagnostic


class DeploymentKitError(CanvasForgeError):
    """Raised when packaging, inspection, or verification fails."""


class DeploymentKitSecurityError(DeploymentKitError):
    """Raised when forbidden content blocks packaging."""


def blocking(code: str, message: str, *, path: str = "$", hint: str | None = None) -> Diagnostic:
    return Diagnostic(code=code, message=message, path=path, severity="error", hint=hint)


def warning(code: str, message: str, *, path: str = "$", hint: str | None = None) -> Diagnostic:
    return Diagnostic(code=code, message=message, path=path, severity="warning", hint=hint)
