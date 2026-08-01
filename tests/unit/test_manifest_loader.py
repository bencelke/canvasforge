"""Tests for safe manifest loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from canvasforge.errors import ManifestLoadError
from canvasforge.manifest.loader import MAX_MANIFEST_BYTES, load_manifest_dict

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


def test_load_valid_minimal_fixture() -> None:
    data = load_manifest_dict(FIXTURES / "valid-minimal-app.yaml")
    assert data["app"]["key"] == "minimalValid"
    assert isinstance(data["screens"], list)


def test_load_hello_example() -> None:
    data = load_manifest_dict(EXAMPLES / "hello-canvasforge" / "app.yaml")
    assert data["app"]["name"] == "Hello CanvasForge"


def test_load_oroom_example() -> None:
    data = load_manifest_dict(EXAMPLES / "oroom-actions" / "app.yaml")
    assert data["app"]["key"] == "oroomActions"
    assert data["dataSources"][0]["collection"] == "colActions"


def test_load_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ManifestLoadError) as exc_info:
        load_manifest_dict(tmp_path / "missing.yaml")
    assert exc_info.value.diagnostics[0].code == "LOAD_NOT_A_FILE"


def test_load_empty_yaml(tmp_path: Path) -> None:
    path = tmp_path / "empty.yaml"
    path.write_text("", encoding="utf-8")
    with pytest.raises(ManifestLoadError) as exc_info:
        load_manifest_dict(path)
    assert exc_info.value.diagnostics[0].code == "LOAD_EMPTY"


def test_load_non_mapping_root(tmp_path: Path) -> None:
    path = tmp_path / "list.yaml"
    path.write_text("- just\n- a\n- list\n", encoding="utf-8")
    with pytest.raises(ManifestLoadError) as exc_info:
        load_manifest_dict(path)
    assert exc_info.value.diagnostics[0].code == "LOAD_ROOT_TYPE"


def test_load_rejects_oversized_file(tmp_path: Path) -> None:
    path = tmp_path / "big.yaml"
    path.write_bytes(b"a" * (MAX_MANIFEST_BYTES + 1))
    with pytest.raises(ManifestLoadError) as exc_info:
        load_manifest_dict(path)
    assert exc_info.value.diagnostics[0].code == "LOAD_FILE_TOO_LARGE"


def test_load_invalid_yaml_syntax(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("app: [\n  unclosed\n", encoding="utf-8")
    with pytest.raises(ManifestLoadError) as exc_info:
        load_manifest_dict(path)
    assert exc_info.value.diagnostics[0].code == "LOAD_YAML_ERROR"
