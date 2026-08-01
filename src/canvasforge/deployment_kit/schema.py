"""JSON Schema loading for Deployment Kit project descriptors."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError

from canvasforge.deployment_kit.errors import DeploymentKitError, blocking


def _candidate_schema_paths() -> list[Path]:
    here = Path(__file__).resolve()
    return [
        here.parents[1] / "data" / "deployment-kit.schema.json",
        here.parents[3] / "schemas" / "deployment-kit.schema.json",
    ]


@lru_cache(maxsize=1)
def load_deployment_kit_schema() -> dict[str, Any]:
    try:
        root = resources.files("canvasforge.data")
        payload = root.joinpath("deployment-kit.schema.json").read_text(encoding="utf-8")
        return json.loads(payload)  # type: ignore[no-any-return]
    except (FileNotFoundError, ModuleNotFoundError, OSError):
        pass

    searched: list[str] = []
    for path in _candidate_schema_paths():
        searched.append(str(path))
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))  # type: ignore[no-any-return]
    raise FileNotFoundError(f"Unable to locate deployment-kit.schema.json (searched: {searched})")


def validate_project_descriptor(data: dict[str, Any]) -> None:
    schema = load_deployment_kit_schema()
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    if not errors:
        return
    diagnostics = []
    for error in errors[:20]:
        pointer = _json_pointer(error)
        diagnostics.append(
            blocking(
                "KIT_SCHEMA_INVALID",
                error.message,
                path=pointer,
            )
        )
    raise DeploymentKitError(
        "canvasforge-project.json failed schema validation", diagnostics=diagnostics
    )


def _json_pointer(error: JsonSchemaValidationError) -> str:
    parts = [str(p) for p in error.absolute_path]
    if not parts:
        return "$"
    return "$." + ".".join(parts)
