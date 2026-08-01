"""Candidate Code View adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from canvasforge.adapters.code_view.diagnostics import diagnose_app
from canvasforge.adapters.code_view.mapping import node_to_code_view_dict, strip_trace_metadata
from canvasforge.adapters.code_view.metadata import wrap_candidate_yaml
from canvasforge.adapters.code_view.serializer import dumps_code_view_yaml
from canvasforge.controls.compatibility import ensure_compatible
from canvasforge.controls.registry import ControlRegistry, default_registry
from canvasforge.errors import Diagnostic, GenerationError
from canvasforge.ir.models import AppIR


@dataclass(frozen=True, slots=True)
class CodeViewScreenArtifact:
    screen_key: str
    yaml_text: str
    tree: dict[str, Any]


@dataclass(frozen=True, slots=True)
class CodeViewResult:
    screens: list[CodeViewScreenArtifact]
    diagnostics: list[Diagnostic]


class CodeViewAdapter:
    """First target adapter: Candidate Power Apps Code View YAML."""

    target = "code-view"

    def __init__(self, registry: ControlRegistry | None = None) -> None:
        self.registry = registry or default_registry()

    def generate(self, ir: AppIR, *, build_id: str) -> CodeViewResult:
        diagnostics = diagnose_app(ir, self.registry)
        errors = [d for d in diagnostics if d.severity == "error"]
        if errors:
            raise GenerationError(
                "Code View adapter rejected the control tree",
                diagnostics=errors,
            )

        artifacts: list[CodeViewScreenArtifact] = []
        for screen in ir.screens:
            ensure_compatible(screen.root, self.registry)
            tree_with_meta = node_to_code_view_dict(screen.root, self.registry)
            tree = strip_trace_metadata(tree_with_meta)
            # Candidate document shape: single screen control tree
            document = {
                "CanvasForgeCandidate": True,
                "Status": "Studio-unvalidated",
                "Screen": tree,
            }
            body = dumps_code_view_yaml(document)
            yaml_text = wrap_candidate_yaml(body, build_id=build_id, screen_key=screen.key)
            artifacts.append(
                CodeViewScreenArtifact(
                    screen_key=screen.key,
                    yaml_text=yaml_text,
                    tree=tree,
                )
            )
        return CodeViewResult(screens=artifacts, diagnostics=diagnostics)
