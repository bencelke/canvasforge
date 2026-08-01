"""Generation reports and build identifiers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from canvasforge import __version__
from canvasforge.errors import Diagnostic
from canvasforge.ir.models import (
    AppIR,
    ControlNode,
    GenerationArtifact,
    GenerationPlan,
    GenerationPlanStep,
)


def compute_manifest_checksum(raw_bytes: bytes) -> str:
    """SHA-256 of manifest bytes with newlines normalized to LF.

    Windows checkouts with ``core.autocrlf=true`` yield CRLF on disk.
    Normalizing before hashing keeps build IDs platform-stable.
    """
    normalized = raw_bytes.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(normalized).hexdigest()


def compute_build_id(
    *,
    manifest_checksum: str,
    target: str,
    screen_keys: list[str],
    allow_partial: bool,
) -> str:
    """Deterministic build ID (no timestamps)."""
    payload = "|".join(
        [
            __version__,
            target,
            manifest_checksum,
            ",".join(screen_keys),
            "partial" if allow_partial else "strict",
        ]
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return digest[:16]


def count_controls(node: ControlNode) -> int:
    return 1 + sum(count_controls(child) for child in node.children)


def count_properties(node: ControlNode) -> int:
    total = len(node.properties)
    for child in node.children:
        total += count_properties(child)
    return total


def count_formulas(node: ControlNode) -> int:
    total = len(node.formulas)
    for child in node.children:
        total += count_formulas(child)
    return total


def build_generation_plan_from_ir(
    *,
    build_id: str,
    ir: AppIR,
    target: str,
    expanded: list[str],
    omitted: list[str],
) -> GenerationPlan:
    steps: list[GenerationPlanStep] = []

    def add(action: str, target_name: str, detail: str) -> None:
        steps.append(
            GenerationPlanStep(
                index=len(steps) + 1,
                action=action,
                target=target_name,
                detail=detail,
            )
        )

    add("Initialize adapter", target, "Candidate Code View output")
    for screen in ir.screens:
        add("Create screen", screen.root.name, f"key={screen.key}")
        add(
            "Add root container",
            screen.root.children[0].name if screen.root.children else "—",
            "conScreenRoot",
        )

        def walk(node: ControlNode) -> None:
            if node.control_type == "Screen":
                for child in node.children:
                    walk(child)
                return
            if node.parent_id and node.control_type != "Screen":
                add("Add control", node.name, f"type={node.control_type}; id={node.id}")
            for child in node.children:
                walk(child)

        walk(screen.root)

    for key in expanded:
        add("Expand section", key, "generatable")
    for key in omitted:
        add("Omit section", key, "not generatable in Phase 2")

    return GenerationPlan(
        build_id=build_id,
        app_key=ir.app_key,
        target=target,
        steps=steps,
    )


def build_report(
    *,
    build_id: str,
    manifest_path: str,
    manifest_checksum: str,
    target: str,
    ir: AppIR,
    expanded: list[str],
    omitted: list[str],
    diagnostics: list[Diagnostic],
    artifacts: list[GenerationArtifact],
    screen_keys: list[str],
) -> dict[str, Any]:
    control_count = sum(count_controls(screen.root) for screen in ir.screens)
    property_count = sum(count_properties(screen.root) for screen in ir.screens)
    formula_count = sum(count_formulas(screen.root) for screen in ir.screens)
    errors = [d for d in diagnostics if d.severity == "error"]
    warnings = [d for d in diagnostics if d.severity == "warning"]
    return {
        "buildId": build_id,
        "manifestPath": Path(manifest_path).name,
        "manifestChecksum": manifest_checksum,
        "canvasforgeVersion": __version__,
        "targetAdapter": target,
        "screensRequested": screen_keys,
        "sectionsExpanded": expanded,
        "controlsGenerated": control_count,
        "propertiesGenerated": property_count,
        "formulasGenerated": formula_count,
        "unsupportedSections": omitted,
        "warnings": [d.to_dict() for d in warnings],
        "blockingErrors": [d.to_dict() for d in errors],
        "evidenceSummary": {
            "policy": "documented|studio-exported|studio-validated allowed; inferred blocked",
            "studioValidationState": "unvalidated",
            "outputStatus": "Candidate",
        },
        "studioValidationState": "unvalidated",
        "artifacts": [artifact.model_dump() for artifact in artifacts],
    }


def control_tree_dict(ir: AppIR) -> dict[str, Any]:
    return {
        "appKey": ir.app_key,
        "appName": ir.app_name,
        "screens": [screen.root.model_dump(mode="json") for screen in ir.screens],
    }


def dump_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"
