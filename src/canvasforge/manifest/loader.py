"""Safe YAML loading for CanvasForge manifests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from canvasforge.errors import Diagnostic, ManifestLoadError

# Explicit safety limits
MAX_MANIFEST_BYTES = 1_048_576  # 1 MiB
MAX_NESTING_DEPTH = 40


def _nesting_depth(value: Any, current: int = 0) -> int:
    if current > MAX_NESTING_DEPTH:
        return current
    if isinstance(value, dict):
        if not value:
            return current
        return max(_nesting_depth(v, current + 1) for v in value.values())
    if isinstance(value, list):
        if not value:
            return current
        return max(_nesting_depth(v, current + 1) for v in value)
    return current


def _assert_safe_path(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise ManifestLoadError(
            f"Manifest path is not a file: {path}",
            diagnostics=[
                Diagnostic(
                    code="LOAD_NOT_A_FILE",
                    message=f"Path does not exist or is not a file: {resolved}",
                    path="$",
                    hint="Provide a path to a local YAML manifest file",
                )
            ],
        )
    return resolved


def load_manifest_dict(path: Path | str) -> dict[str, Any]:
    """Load a manifest YAML file using a safe loader with size/nesting limits.

    Security guarantees for Phase 1:
    - No remote includes / URL imports
    - No environment-variable interpolation
    - No arbitrary Python object construction
    - Explicit file-size and nesting limits
    """
    file_path = _assert_safe_path(Path(path))
    size = file_path.stat().st_size
    if size > MAX_MANIFEST_BYTES:
        raise ManifestLoadError(
            "Manifest exceeds maximum allowed size",
            diagnostics=[
                Diagnostic(
                    code="LOAD_FILE_TOO_LARGE",
                    message=(
                        f"Manifest is {size} bytes; maximum allowed is {MAX_MANIFEST_BYTES} bytes"
                    ),
                    path=str(file_path),
                    hint="Split or reduce the manifest; remote includes are not supported",
                )
            ],
        )

    yaml = YAML(typ="safe")
    # Disallow overly large expansions; keep defaults conservative.
    yaml.allow_duplicate_keys = False

    try:
        raw_text = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ManifestLoadError(
            f"Unable to read manifest: {file_path}",
            diagnostics=[
                Diagnostic(
                    code="LOAD_IO_ERROR",
                    message=str(exc),
                    path=str(file_path),
                )
            ],
        ) from exc

    try:
        data = yaml.load(raw_text)
    except YAMLError as exc:
        raise ManifestLoadError(
            f"Invalid YAML in manifest: {file_path}",
            diagnostics=[
                Diagnostic(
                    code="LOAD_YAML_ERROR",
                    message=str(exc).strip() or "YAML parse error",
                    path="$",
                    hint="Fix YAML syntax; only local safe YAML is accepted",
                )
            ],
        ) from exc

    if data is None:
        raise ManifestLoadError(
            "Manifest is empty",
            diagnostics=[
                Diagnostic(
                    code="LOAD_EMPTY",
                    message="YAML document is empty",
                    path="$",
                )
            ],
        )

    if not isinstance(data, dict):
        raise ManifestLoadError(
            "Manifest root must be a mapping",
            diagnostics=[
                Diagnostic(
                    code="LOAD_ROOT_TYPE",
                    message=f"Expected a YAML mapping at root, got {type(data).__name__}",
                    path="$",
                )
            ],
        )

    depth = _nesting_depth(data)
    if depth > MAX_NESTING_DEPTH:
        raise ManifestLoadError(
            "Manifest exceeds maximum nesting depth",
            diagnostics=[
                Diagnostic(
                    code="LOAD_NESTING_TOO_DEEP",
                    message=f"Nesting depth {depth} exceeds limit {MAX_NESTING_DEPTH}",
                    path="$",
                    hint="Flatten section hierarchies; recursive includes are not supported",
                )
            ],
        )

    return dict(data)
