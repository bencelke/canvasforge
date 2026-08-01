"""Phase 2 generation and Code View adapter tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from canvasforge.cli import app
from canvasforge.controls.registry import default_registry
from canvasforge.errors import GenerationError
from canvasforge.generate.expander import build_app_ir
from canvasforge.generate.naming import NameAllocator, build_control_name
from canvasforge.generate.pipeline import run_generation
from canvasforge.generate.reports import dump_json
from canvasforge.ir.models import ControlNode, PropertyValue, SourceReference
from canvasforge.manifest.loader import load_manifest_dict
from canvasforge.manifest.validator import parse_manifest

runner = CliRunner()
ROOT = Path(__file__).resolve().parents[2]
HELLO = ROOT / "examples" / "hello-canvasforge" / "app.yaml"
OROOM_FULL = ROOT / "examples" / "oroom-actions" / "app.yaml"
OROOM_PROOF = ROOT / "examples" / "oroom-actions" / "dashboard-proof.yaml"
SNAPSHOTS = Path(__file__).resolve().parents[1] / "snapshots"


def test_hello_ir_and_control_names() -> None:
    manifest = parse_manifest(load_manifest_dict(HELLO))
    ir, diagnostics, expanded, omitted = build_app_ir(manifest)
    assert not [d for d in diagnostics if d.severity == "error"]
    assert omitted == []
    assert "hdrDashboard" in expanded
    screen = ir.screens[0]
    root = screen.root
    assert root.control_type == "Screen"
    assert root.children[0].name == "conScreenRoot"
    names = _collect_names(root)
    assert "lblPageTitle" in names
    assert "conSummaryRow" in names
    assert "conCardOpen" in names
    assert "conCardCompleted" in names
    assert "conEmptyState" in names
    assert "btnEmptyStateAction" in names


def _collect_names(node: ControlNode) -> set[str]:
    names = {node.name}
    for child in node.children:
        names |= _collect_names(child)
    return names


def test_hello_generation_deterministic(tmp_path: Path) -> None:
    first = run_generation(HELLO, output_dir=tmp_path / "a")
    second = run_generation(HELLO, output_dir=tmp_path / "b")
    assert first.build_id == second.build_id
    assert first.yaml_by_screen == second.yaml_by_screen
    assert dump_json(first.control_tree) == dump_json(second.control_tree)
    assert dump_json(first.plan.model_dump(mode="json")) == dump_json(
        second.plan.model_dump(mode="json")
    )


def test_hello_yaml_snapshot() -> None:
    result = run_generation(HELLO, dry_run=True)
    yaml_text = result.yaml_by_screen["scrDashboard"]
    snapshot = SNAPSHOTS / "hello-scrdashboard.code-view.yaml"
    if not snapshot.exists():
        snapshot.write_text(yaml_text, encoding="utf-8")
    assert yaml_text == snapshot.read_text(encoding="utf-8")
    assert "Studio-unvalidated" in yaml_text
    assert "CanvasForgeCandidate" in yaml_text
    assert "OnSelect" not in yaml_text


def test_hello_control_tree_snapshot() -> None:
    result = run_generation(HELLO, dry_run=True)
    payload = dump_json(result.control_tree)
    snapshot = SNAPSHOTS / "hello-control-tree.json"
    if not snapshot.exists():
        snapshot.write_text(payload, encoding="utf-8")
    assert payload == snapshot.read_text(encoding="utf-8")


def test_hello_plan_and_report_snapshots() -> None:
    result = run_generation(HELLO, dry_run=True)
    plan = dump_json(result.plan.model_dump(mode="json"))
    report = dump_json(result.report)
    plan_snap = SNAPSHOTS / "hello-generation-plan.json"
    report_snap = SNAPSHOTS / "hello-generation-report.json"
    if not plan_snap.exists():
        plan_snap.write_text(plan, encoding="utf-8")
    if not report_snap.exists():
        report_snap.write_text(report, encoding="utf-8")
    assert plan == plan_snap.read_text(encoding="utf-8")
    assert report == report_snap.read_text(encoding="utf-8")
    assert result.report["studioValidationState"] == "unvalidated"


def test_oroom_full_fails_without_partial() -> None:
    with pytest.raises(GenerationError) as exc_info:
        run_generation(OROOM_FULL, dry_run=True)
    codes = {d.code for d in exc_info.value.diagnostics}
    assert "SECTION_NOT_GENERATABLE" in codes


def test_oroom_full_allow_partial(tmp_path: Path) -> None:
    result = run_generation(
        OROOM_FULL,
        dry_run=True,
        allow_partial=True,
        output_dir=tmp_path / "partial",
    )
    assert "toolbarSearch" in result.report["unsupportedSections"]
    assert "galleryActions" in result.report["unsupportedSections"]


def test_oroom_proof_generates() -> None:
    result = run_generation(OROOM_PROOF, dry_run=True)
    assert "scrRequestorDashboard" in result.yaml_by_screen
    assert result.report["unsupportedSections"] == []


def test_duplicate_name_diagnostic() -> None:
    names = NameAllocator()
    names.allocate("Text", "PageTitle", preferred="lblPageTitle")
    with pytest.raises(GenerationError) as exc_info:
        names.allocate("Text", "Other", preferred="lblPageTitle")
    assert any(d.code == "DUPLICATE_CONTROL_NAME" for d in exc_info.value.diagnostics)


def test_unknown_property_rejection() -> None:
    registry = default_registry()
    node = ControlNode(
        id="test/node",
        name="lblX",
        control_type="Text",
        properties=[
            PropertyValue(
                name="TotallyFakeProperty",
                kind="literal",
                value="nope",
                evidence_status="documented",
            )
        ],
        source=SourceReference(path="$.test", app_key="test"),
    )
    with pytest.raises(GenerationError) as exc_info:
        registry.assert_property_generatable(node.control_type, "TotallyFakeProperty")
    assert any(d.code == "UNKNOWN_PROPERTY" for d in exc_info.value.diagnostics)


def test_controls_and_evidence_cli() -> None:
    controls = runner.invoke(app, ["controls", "--json"])
    assert controls.exit_code == 0
    assert "VerticalContainer" in controls.stdout
    evidence = runner.invoke(app, ["evidence", "list", "--json"])
    assert evidence.exit_code == 0
    assert "ev-screen-documented" in evidence.stdout


def test_generate_cli_hello(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "generate",
            str(HELLO),
            "--target",
            "code-view",
            "--output",
            str(tmp_path / "out"),
        ],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
    assert (tmp_path / "out" / "code-view" / "scrDashboard.yaml").is_file()
    assert (tmp_path / "out" / "reports" / "generation-report.json").is_file()


def test_naming_prefixes() -> None:
    assert build_control_name("Text", "PageTitle").startswith("lbl")
    assert build_control_name("Button", "EmptyStateAction").startswith("btn")
    assert build_control_name("VerticalContainer", "ScreenRoot").startswith("con")
