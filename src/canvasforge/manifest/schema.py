"""JSON Schema helpers for CanvasForge manifests."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError

from canvasforge.errors import Diagnostic

_SCHEMA_CANDIDATES = (
    Path(__file__).resolve().parents[1] / "data" / "app-manifest.schema.json",
    Path(__file__).resolve().parents[3] / "schemas" / "app-manifest.schema.json",
    Path.cwd() / "schemas" / "app-manifest.schema.json",
)


def find_schema_path() -> Path:
    """Locate the bundled app manifest JSON Schema."""
    for candidate in _SCHEMA_CANDIDATES:
        if candidate.is_file():
            return candidate
    searched = ", ".join(str(path) for path in _SCHEMA_CANDIDATES)
    raise FileNotFoundError(f"Unable to locate app-manifest.schema.json (searched: {searched})")


@lru_cache(maxsize=1)
def load_schema() -> dict[str, Any]:
    """Load and cache the JSON Schema document."""
    path = find_schema_path()
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError("Schema root must be a JSON object")
    return data


def _json_pointer(error: JsonSchemaValidationError) -> str:
    parts: list[str] = []
    for part in error.absolute_path:
        parts.append(str(part))
    if not parts:
        return "$"
    return "$." + ".".join(parts)


def validate_against_schema(data: dict[str, Any]) -> list[Diagnostic]:
    """Validate a manifest dict against the JSON Schema. Returns diagnostics (empty if valid)."""
    schema = load_schema()
    validator = Draft202012Validator(schema)
    diagnostics: list[Diagnostic] = []
    for error in sorted(validator.iter_errors(data), key=lambda err: list(err.absolute_path)):
        diagnostics.append(
            Diagnostic(
                code="SCHEMA_VALIDATION",
                message=error.message,
                path=_json_pointer(error),
                hint="See docs/manifest-specification.md and schemas/app-manifest.schema.json",
                details={"validator": error.validator},
            )
        )
    return diagnostics
