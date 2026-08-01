"""CLI and planner tests."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from canvasforge import __version__
from canvasforge.cli import app
from canvasforge.manifest.loader import load_manifest_dict
from canvasforge.manifest.validator import parse_manifest
from canvasforge.planner import build_generation_plan

runner = CliRunner()
ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples"
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_doctor_command() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Offline mode" in result.stdout
    assert "Microsoft" in result.stdout


def test_validate_hello_success() -> None:
    result = runner.invoke(app, ["validate", str(EXAMPLES / "hello-canvasforge" / "app.yaml")])
    assert result.exit_code == 0
    assert "Valid" in result.stdout


def test_validate_oroom_success() -> None:
    result = runner.invoke(app, ["validate", str(EXAMPLES / "oroom-actions" / "app.yaml")])
    assert result.exit_code == 0
    assert "oroomActions" in result.stdout or "O-Room Actions" in result.stdout


def test_validate_invalid_fails() -> None:
    result = runner.invoke(app, ["validate", str(FIXTURES / "invalid-app.yaml")])
    assert result.exit_code != 0
    assert "Error:" in result.stdout or "Error:" in result.stderr


def test_inspect_prints_structure() -> None:
    result = runner.invoke(app, ["inspect", str(EXAMPLES / "hello-canvasforge" / "app.yaml")])
    assert result.exit_code == 0
    assert "Hello CanvasForge" in result.stdout
    assert "scrDashboard" in result.stdout
    assert "Screens" in result.stdout
    assert "Navigation" in result.stdout
    assert "Breakpoints" in result.stdout


def test_plan_is_deterministic() -> None:
    path = EXAMPLES / "hello-canvasforge" / "app.yaml"
    first = runner.invoke(app, ["plan", str(path)])
    second = runner.invoke(app, ["plan", str(path)])
    assert first.exit_code == 0
    assert first.stdout == second.stdout
    assert "Initialize theme" in first.stdout
    assert "Create screen" in first.stdout
    assert "Add section" in first.stdout
    assert "Phase 1 does not generate Power Apps YAML" in first.stdout


def test_plan_builder_stable_ordering() -> None:
    manifest = parse_manifest(load_manifest_dict(EXAMPLES / "oroom-actions" / "app.yaml"))
    plan_a = build_generation_plan(manifest).render()
    plan_b = build_generation_plan(manifest).render()
    assert plan_a == plan_b
    assert "Initialize mock collection: actions" in plan_a
    assert "Create screen: scrRequestorDashboard" in plan_a
    assert "Add section: scrRequestorDashboard/hdrMyActions" in plan_a
