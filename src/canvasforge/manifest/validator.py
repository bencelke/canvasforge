"""Semantic validation for CanvasForge manifests."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError as PydanticValidationError

from canvasforge.errors import Diagnostic, ManifestValidationError
from canvasforge.manifest.models import (
    STACK_SECTION_TYPES,
    AppManifest,
    Section,
)
from canvasforge.manifest.schema import validate_against_schema


def _pydantic_path(loc: tuple[Any, ...]) -> str:
    if not loc:
        return "$"
    parts: list[str] = []
    for item in loc:
        parts.append(str(item))
    return "$." + ".".join(parts)


def _diagnostics_from_pydantic(exc: PydanticValidationError) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for err in exc.errors():
        loc = err.get("loc", ())
        msg = err.get("msg", "Validation error")
        diagnostics.append(
            Diagnostic(
                code="MODEL_VALIDATION",
                message=str(msg),
                path=_pydantic_path(tuple(loc)),
                hint="Check required fields, types, and supported values",
                details={"type": err.get("type")},
            )
        )
    return diagnostics


def _iter_sections(sections: list[Section], prefix: str) -> list[tuple[str, Section]]:
    found: list[tuple[str, Section]] = []
    for index, section in enumerate(sections):
        path = f"{prefix}.{index}"
        found.append((path, section))
        if section.children:
            found.extend(_iter_sections(section.children, f"{path}.children"))
    return found


def _find_duplicate_keys(keys: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for key in keys:
        if key in seen and key not in duplicates:
            duplicates.append(key)
        seen.add(key)
    return duplicates


def collect_semantic_diagnostics(manifest: AppManifest) -> list[Diagnostic]:
    """Return semantic diagnostics for a parsed manifest (does not raise)."""
    diagnostics: list[Diagnostic] = []

    screen_keys = [screen.key for screen in manifest.screens]
    for dup in _find_duplicate_keys(screen_keys):
        diagnostics.append(
            Diagnostic(
                code="DUPLICATE_SCREEN_KEY",
                message=f"Duplicate screen key '{dup}'",
                path="$.screens",
                hint="Screen keys must be unique within the manifest",
            )
        )

    data_source_keys = [source.key for source in manifest.data_sources]
    for dup in _find_duplicate_keys(data_source_keys):
        diagnostics.append(
            Diagnostic(
                code="DUPLICATE_DATA_SOURCE_KEY",
                message=f"Duplicate data source key '{dup}'",
                path="$.dataSources",
            )
        )

    permission_keys = [permission.key for permission in manifest.permissions]
    for dup in _find_duplicate_keys(permission_keys):
        diagnostics.append(
            Diagnostic(
                code="DUPLICATE_PERMISSION_KEY",
                message=f"Duplicate permission key '{dup}'",
                path="$.permissions",
            )
        )

    navigation_keys = [item.key for item in manifest.navigation]
    for dup in _find_duplicate_keys(navigation_keys):
        diagnostics.append(
            Diagnostic(
                code="DUPLICATE_NAVIGATION_KEY",
                message=f"Duplicate navigation key '{dup}'",
                path="$.navigation",
            )
        )

    screen_key_set = set(screen_keys)
    if manifest.app.start_screen not in screen_key_set:
        diagnostics.append(
            Diagnostic(
                code="INVALID_START_SCREEN",
                message=(
                    f"startScreen '{manifest.app.start_screen}' does not match any screen key"
                ),
                path="$.app.startScreen",
                hint=f"Known screens: {', '.join(sorted(screen_key_set)) or '(none)'}",
            )
        )

    if manifest.app.theme is not None:
        if manifest.theme is None:
            diagnostics.append(
                Diagnostic(
                    code="MISSING_THEME",
                    message=f"app.theme '{manifest.app.theme}' is set but theme block is missing",
                    path="$.app.theme",
                )
            )
        elif manifest.theme.key != manifest.app.theme:
            diagnostics.append(
                Diagnostic(
                    code="THEME_KEY_MISMATCH",
                    message=(
                        f"app.theme '{manifest.app.theme}' does not match theme.key "
                        f"'{manifest.theme.key}'"
                    ),
                    path="$.app.theme",
                )
            )

    data_source_set = set(data_source_keys)
    permission_set = set(permission_keys)

    for screen_index, screen in enumerate(manifest.screens):
        screen_path = f"$.screens.{screen_index}"
        section_entries = _iter_sections(screen.sections, f"{screen_path}.sections")
        section_keys = [section.key for _, section in section_entries]
        for dup in _find_duplicate_keys(section_keys):
            diagnostics.append(
                Diagnostic(
                    code="DUPLICATE_SECTION_KEY",
                    message=f"Duplicate section key '{dup}' within screen '{screen.key}'",
                    path=f"{screen_path}.sections",
                    hint="Section keys must be unique within a screen (including nested children)",
                )
            )

        for perm_index, permission in enumerate(screen.permissions):
            if permission not in permission_set:
                diagnostics.append(
                    Diagnostic(
                        code="UNKNOWN_PERMISSION",
                        message=f"Unknown permission '{permission}' on screen '{screen.key}'",
                        path=f"{screen_path}.permissions.{perm_index}",
                    )
                )

        for section_path, section in section_entries:
            if section.data_source is not None and section.data_source not in data_source_set:
                diagnostics.append(
                    Diagnostic(
                        code="UNKNOWN_DATA_SOURCE",
                        message=(
                            f"Unknown dataSource '{section.data_source}' on section '{section.key}'"
                        ),
                        path=f"{section_path}.dataSource",
                    )
                )
            if section.children and section.type not in STACK_SECTION_TYPES:
                diagnostics.append(
                    Diagnostic(
                        code="UNSUPPORTED_SECTION_CHILDREN",
                        message=(f"Section type '{section.type}' cannot contain children"),
                        path=f"{section_path}.children",
                    )
                )

    for nav_index, item in enumerate(manifest.navigation):
        nav_path = f"$.navigation.{nav_index}"
        if item.target_screen not in screen_key_set:
            diagnostics.append(
                Diagnostic(
                    code="UNKNOWN_NAV_TARGET",
                    message=(
                        f"Navigation '{item.key}' targets unknown screen '{item.target_screen}'"
                    ),
                    path=f"{nav_path}.targetScreen",
                )
            )
        if item.permission is not None and item.permission not in permission_set:
            diagnostics.append(
                Diagnostic(
                    code="UNKNOWN_NAV_PERMISSION",
                    message=(
                        f"Navigation '{item.key}' references unknown permission '{item.permission}'"
                    ),
                    path=f"{nav_path}.permission",
                )
            )

    return diagnostics


def parse_manifest(data: dict[str, Any]) -> AppManifest:
    """Parse and semantically validate a manifest dict. Raises ManifestValidationError."""
    schema_diagnostics = validate_against_schema(data)
    if schema_diagnostics:
        raise ManifestValidationError(
            "Manifest failed JSON Schema validation",
            diagnostics=schema_diagnostics,
        )

    try:
        manifest = AppManifest.model_validate(data)
    except PydanticValidationError as exc:
        raise ManifestValidationError(
            "Manifest failed typed model validation",
            diagnostics=_diagnostics_from_pydantic(exc),
        ) from exc

    semantic = collect_semantic_diagnostics(manifest)
    errors = [d for d in semantic if d.severity == "error"]
    if errors:
        raise ManifestValidationError(
            "Manifest failed semantic validation",
            diagnostics=errors,
        )
    return manifest


def validate_manifest_data(data: dict[str, Any]) -> AppManifest:
    """Alias for parse_manifest for clarity at call sites."""
    return parse_manifest(data)
