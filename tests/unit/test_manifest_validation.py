"""Tests for schema and semantic manifest validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from canvasforge.errors import ManifestValidationError
from canvasforge.manifest.loader import load_manifest_dict
from canvasforge.manifest.validator import parse_manifest

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


def test_valid_minimal_fixture() -> None:
    manifest = parse_manifest(load_manifest_dict(FIXTURES / "valid-minimal-app.yaml"))
    assert manifest.app.key == "minimalValid"
    assert manifest.app.start_screen == "scrHome"


def test_hello_example_validates() -> None:
    manifest = parse_manifest(load_manifest_dict(EXAMPLES / "hello-canvasforge" / "app.yaml"))
    assert manifest.app.name == "Hello CanvasForge"
    assert len(manifest.screens) == 1
    types = [section.type for section in manifest.screens[0].sections]
    assert types == [
        "page-header",
        "summary-grid",
        "summary-card",
        "summary-card",
        "empty-state",
    ]


def test_oroom_example_validates() -> None:
    manifest = parse_manifest(load_manifest_dict(EXAMPLES / "oroom-actions" / "app.yaml"))
    assert manifest.app.start_screen == "scrRequestorDashboard"
    assert "actions" in manifest.data_source_keys()
    section_types = [section.type for section in manifest.screens[0].sections]
    assert "page-header" in section_types
    assert "summary-grid" in section_types
    assert section_types.count("summary-card") == 4
    assert "search-toolbar" in section_types
    assert "action-gallery" in section_types
    assert "empty-state" in section_types


def test_invalid_fixture_fails_with_actionable_errors() -> None:
    data = load_manifest_dict(FIXTURES / "invalid-app.yaml")
    with pytest.raises(ManifestValidationError) as exc_info:
        parse_manifest(data)

    codes = {diagnostic.code for diagnostic in exc_info.value.diagnostics}
    # Schema should catch unsupported manifest version and/or unsupported section type.
    assert codes, "expected diagnostics"
    assert all(diagnostic.path for diagnostic in exc_info.value.diagnostics)
    assert all(diagnostic.message for diagnostic in exc_info.value.diagnostics)
    rendered = exc_info.value.format_terminal()
    assert "at $" in rendered or "at $." in rendered


def test_semantic_unknown_start_screen() -> None:
    data = load_manifest_dict(FIXTURES / "valid-minimal-app.yaml")
    data["app"]["startScreen"] = "scrNope"
    with pytest.raises(ManifestValidationError) as exc_info:
        parse_manifest(data)
    assert any(d.code == "INVALID_START_SCREEN" for d in exc_info.value.diagnostics)


def test_semantic_duplicate_navigation_and_bad_target() -> None:
    data = load_manifest_dict(FIXTURES / "valid-minimal-app.yaml")
    data["navigation"] = [
        {
            "key": "navHome",
            "label": "Home",
            "targetScreen": "scrHome",
        },
        {
            "key": "navHome",
            "label": "Home again",
            "targetScreen": "scrMissing",
        },
    ]
    with pytest.raises(ManifestValidationError) as exc_info:
        parse_manifest(data)
    codes = {d.code for d in exc_info.value.diagnostics}
    assert "DUPLICATE_NAVIGATION_KEY" in codes
    assert "UNKNOWN_NAV_TARGET" in codes


def test_semantic_unknown_data_source_and_permission() -> None:
    data = load_manifest_dict(FIXTURES / "valid-minimal-app.yaml")
    data["screens"][0]["permissions"] = ["roleMissing"]
    data["screens"][0]["sections"].append(
        {
            "key": "gallery",
            "type": "action-gallery",
            "dataSource": "missingSource",
        }
    )
    with pytest.raises(ManifestValidationError) as exc_info:
        parse_manifest(data)
    codes = {d.code for d in exc_info.value.diagnostics}
    assert "UNKNOWN_PERMISSION" in codes
    assert "UNKNOWN_DATA_SOURCE" in codes


def test_breakpoint_ordering_enforced() -> None:
    data = load_manifest_dict(FIXTURES / "valid-minimal-app.yaml")
    data["breakpoints"] = {"mobile": 1000, "tablet": 900, "desktop": 800}
    with pytest.raises(ManifestValidationError) as exc_info:
        parse_manifest(data)
    assert exc_info.value.diagnostics
    assert any("mobile < tablet < desktop" in d.message for d in exc_info.value.diagnostics)


def test_unsupported_section_type_rejected() -> None:
    data = load_manifest_dict(FIXTURES / "valid-minimal-app.yaml")
    data["screens"][0]["sections"] = [{"key": "bad", "type": "magic-widget", "title": "Nope"}]
    with pytest.raises(ManifestValidationError) as exc_info:
        parse_manifest(data)
    assert exc_info.value.diagnostics
