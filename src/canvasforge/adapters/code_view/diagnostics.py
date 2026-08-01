"""Code View adapter diagnostics helpers."""

from __future__ import annotations

from canvasforge.adapters.code_view.mapping import collect_adapter_diagnostics
from canvasforge.controls.registry import ControlRegistry
from canvasforge.errors import Diagnostic
from canvasforge.ir.models import AppIR


def diagnose_app(ir: AppIR, registry: ControlRegistry) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for screen in ir.screens:
        diagnostics.extend(collect_adapter_diagnostics(screen.root, registry))
    return diagnostics
