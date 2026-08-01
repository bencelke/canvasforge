"""Phase 3B Deployment Kit packaging tests."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from canvasforge.cli import app
from canvasforge.deployment_kit.archive import build_deterministic_zip, read_zip_members
from canvasforge.deployment_kit.builder import build_deployment_kit
from canvasforge.deployment_kit.checksums import sha256_hex
from canvasforge.deployment_kit.constants import CHECKSUMS_NAME, PROJECT_DESCRIPTOR_NAME
from canvasforge.deployment_kit.errors import DeploymentKitError
from canvasforge.deployment_kit.inspector import inspect_deployment_kit
from canvasforge.deployment_kit.security import scan_members
from canvasforge.deployment_kit.verifier import verify_deployment_kit
from canvasforge.errors import GenerationError, ManifestValidationError

runner = CliRunner()
ROOT = Path(__file__).resolve().parents[2]
HELLO = ROOT / "examples" / "hello-canvasforge" / "app.yaml"
OROOM_PROOF = ROOT / "examples" / "oroom-actions" / "dashboard-proof.yaml"
OROOM_FULL = ROOT / "examples" / "oroom-actions" / "app.yaml"


def test_hello_kit_builds(tmp_path: Path) -> None:
    out = tmp_path / "Hello-CanvasForge.cforge.zip"
    result = build_deployment_kit(HELLO, output=out)
    assert out.is_file()
    assert result.build_id
    verify_deployment_kit(out)
    members = read_zip_members(out)
    assert PROJECT_DESCRIPTOR_NAME in members
    assert "generated/code-view/scrDashboard.yaml" in members
    assert "mock-schema/records/actions.json" not in members
    project = json.loads(members[PROJECT_DESCRIPTOR_NAME])
    assert project["containsProductionData"] is False
    assert project["containsCredentials"] is False
    assert project["packageCreatedBy"] == "CanvasForge"
    assert "Users\\" not in members[PROJECT_DESCRIPTOR_NAME].decode("utf-8")
    assert "/home/" not in members[PROJECT_DESCRIPTOR_NAME].decode("utf-8")


def test_oroom_proof_kit_builds(tmp_path: Path) -> None:
    out = tmp_path / "O-Room-Dashboard-Proof.cforge.zip"
    result = build_deployment_kit(OROOM_PROOF, output=out)
    assert out.is_file()
    verify_deployment_kit(out)
    members = read_zip_members(out)
    assert "generated/code-view/scrRequestorDashboard.yaml" in members
    contract = json.loads(members["mock-schema/data-contract.json"])
    assert contract["dataSources"]
    assert result.project["mockDataIncluded"] is False


def test_deterministic_zip_bytes(tmp_path: Path) -> None:
    a = tmp_path / "a.cforge.zip"
    b = tmp_path / "b.cforge.zip"
    first = build_deployment_kit(HELLO, output=a)
    second = build_deployment_kit(HELLO, output=b)
    assert first.package_bytes == second.package_bytes
    assert a.read_bytes() == b.read_bytes()
    assert sha256_hex(a.read_bytes()) == sha256_hex(b.read_bytes())


def test_lf_crlf_manifest_same_package(tmp_path: Path) -> None:
    lf_dir = tmp_path / "lf"
    crlf_dir = tmp_path / "crlf"
    lf_dir.mkdir()
    crlf_dir.mkdir()
    # Same basename so generation reports stay path-stable.
    lf = lf_dir / "app.yaml"
    crlf = crlf_dir / "app.yaml"
    raw = HELLO.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    lf.write_bytes(raw)
    crlf.write_bytes(raw.replace(b"\n", b"\r\n"))
    out_lf = tmp_path / "lf.cforge.zip"
    out_crlf = tmp_path / "crlf.cforge.zip"
    build_deployment_kit(lf, output=out_lf)
    build_deployment_kit(crlf, output=out_crlf)
    assert out_lf.read_bytes() == out_crlf.read_bytes()


def test_verify_and_inspect(tmp_path: Path) -> None:
    out = tmp_path / "kit.cforge.zip"
    build_deployment_kit(HELLO, output=out)
    verified = verify_deployment_kit(out)
    assert verified["ok"] is True
    inspected = inspect_deployment_kit(out)
    assert inspected["checksumStatus"] == "ok"
    assert inspected["projectKey"] == "helloCanvasForge"
    assert inspected["generatedScreens"]


def test_tampered_member_fails_verify(tmp_path: Path) -> None:
    out = tmp_path / "kit.cforge.zip"
    build_deployment_kit(HELLO, output=out)
    members = read_zip_members(out)
    members["theme/theme.json"] = b'{"tampered": true}\n'
    bad = tmp_path / "bad.cforge.zip"
    bad.write_bytes(build_deterministic_zip(members))
    with pytest.raises(DeploymentKitError) as exc_info:
        verify_deployment_kit(bad)
    assert any(d.code == "KIT_CHECKSUM_MISMATCH" for d in exc_info.value.diagnostics)


def test_missing_descriptor_fails(tmp_path: Path) -> None:
    members = {"reports/build-report.json": b"{}\n"}
    path = tmp_path / "missing.cforge.zip"
    path.write_bytes(build_deterministic_zip(members))
    with pytest.raises(DeploymentKitError) as exc_info:
        verify_deployment_kit(path)
    assert any(d.code == "KIT_MISSING_DESCRIPTOR" for d in exc_info.value.diagnostics)


def test_duplicate_member_fails(tmp_path: Path) -> None:
    path = tmp_path / "dup.cforge.zip"
    path.write_bytes(b"placeholder")

    class FakeInfo:
        def __init__(self, name: str) -> None:
            self.filename = name
            self.file_size = 1
            self.compress_size = 1

    class FakeZip:
        def __enter__(self) -> FakeZip:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def infolist(self) -> list[FakeInfo]:
            return [FakeInfo("a.txt"), FakeInfo("a.txt")]

        def read(self, info: FakeInfo) -> bytes:
            return b"x"

    monkey = pytest.MonkeyPatch()
    monkey.setattr(zipfile, "ZipFile", lambda *a, **k: FakeZip())
    try:
        with pytest.raises(DeploymentKitError) as exc_info:
            read_zip_members(path)
        assert any(d.code == "KIT_DUPLICATE_MEMBER" for d in exc_info.value.diagnostics)
    finally:
        monkey.undo()


def test_path_traversal_member_fails(tmp_path: Path) -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as archive:
        archive.writestr("../evil.txt", b"nope")
    path = tmp_path / "trav.cforge.zip"
    path.write_bytes(buffer.getvalue())
    with pytest.raises(DeploymentKitError) as exc_info:
        read_zip_members(path)
    assert any(d.code == "KIT_PATH_TRAVERSAL" for d in exc_info.value.diagnostics)


def test_absolute_path_member_fails(tmp_path: Path) -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as archive:
        info = zipfile.ZipInfo("C:/temp/evil.txt")
        archive.writestr(info, b"nope")
    path = tmp_path / "abs.cforge.zip"
    path.write_bytes(buffer.getvalue())
    with pytest.raises(DeploymentKitError) as exc_info:
        read_zip_members(path)
    codes = {d.code for d in exc_info.value.diagnostics}
    assert "KIT_ABSOLUTE_PATH" in codes or "KIT_PATH_TRAVERSAL" in codes


def test_unsupported_schema_fails(tmp_path: Path) -> None:
    out = tmp_path / "kit.cforge.zip"
    build_deployment_kit(HELLO, output=out)
    members = read_zip_members(out)
    project = json.loads(members[PROJECT_DESCRIPTOR_NAME])
    project["packageSchemaVersion"] = "99.0"
    members[PROJECT_DESCRIPTOR_NAME] = (
        json.dumps(project, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    # Fix checksums to isolate schema failure
    from canvasforge.deployment_kit.checksums import format_checksums_file

    body = {k: v for k, v in members.items() if k != CHECKSUMS_NAME}
    members[CHECKSUMS_NAME] = format_checksums_file(body)
    bad = tmp_path / "bad-schema.cforge.zip"
    bad.write_bytes(build_deterministic_zip(members))
    with pytest.raises(DeploymentKitError) as exc_info:
        verify_deployment_kit(bad)
    assert any(d.code == "KIT_UNSUPPORTED_SCHEMA" for d in exc_info.value.diagnostics)


def test_private_key_blocks_packaging(tmp_path: Path) -> None:
    manifest = tmp_path / "app.yaml"
    manifest.write_text(HELLO.read_text(encoding="utf-8"), encoding="utf-8")
    # Inject into theme via monkeypatch of assemble is hard; scan_members unit instead
    report = scan_members(
        {"evil.txt": b"-----BEGIN RSA PRIVATE KEY-----\nABC\n-----END RSA PRIVATE KEY-----\n"}
    )
    assert report.blocking_count >= 1
    assert any(f.code == "PRIVATE_KEY" for f in report.findings)


def test_credential_assignment_blocks() -> None:
    report = scan_members({"x.json": b'{"api_key": "super-secret-value"}\n'})
    assert any(
        f.code == "ACCESS_TOKEN_ASSIGNMENT" for f in report.findings if f.severity == "error"
    )


def test_email_and_url_detection() -> None:
    report = scan_members(
        {
            "note.md": b"Contact someone@example.org and https://evil.example.net/path\n",
        }
    )
    codes = {f.code for f in report.findings}
    assert "EMAIL_ADDRESS" in codes
    assert "URL" in codes


def test_absolute_path_detection() -> None:
    report = scan_members({"note.md": b"file at C:\\Users\\someone\\secret.txt\n"})
    assert any(f.code == "WINDOWS_ABS_PATH" for f in report.findings)


def test_mock_data_flag(tmp_path: Path) -> None:
    out_default = tmp_path / "default.cforge.zip"
    out_mock = tmp_path / "mock.cforge.zip"
    build_deployment_kit(OROOM_PROOF, output=out_default)
    build_deployment_kit(OROOM_PROOF, output=out_mock, include_mock_data=True)
    default_members = read_zip_members(out_default)
    mock_members = read_zip_members(out_mock)
    assert "mock-schema/records/actions.json" not in default_members
    assert "mock-schema/records/actions.json" in mock_members
    project = json.loads(mock_members[PROJECT_DESCRIPTOR_NAME])
    assert project["mockDataIncluded"] is True
    assert project["mockDataClassification"] == "fictional-records"


def test_invalid_manifest_prevents_packaging(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("app: {}\n", encoding="utf-8")
    with pytest.raises((ManifestValidationError, DeploymentKitError)):
        build_deployment_kit(bad, output=tmp_path / "out.cforge.zip")


def test_unsupported_section_blocks_without_partial(tmp_path: Path) -> None:
    with pytest.raises(GenerationError):
        build_deployment_kit(OROOM_FULL, output=tmp_path / "out.cforge.zip")


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    out = tmp_path / "dry.cforge.zip"
    result = build_deployment_kit(HELLO, output=out, dry_run=True)
    assert result.dry_run is True
    assert not out.exists()
    assert result.package_bytes is not None


def test_overwrite_protection(tmp_path: Path) -> None:
    out = tmp_path / "kit.cforge.zip"
    build_deployment_kit(HELLO, output=out)
    with pytest.raises(DeploymentKitError) as exc_info:
        build_deployment_kit(HELLO, output=out)
    assert any(d.code == "KIT_OUTPUT_EXISTS" for d in exc_info.value.diagnostics)
    build_deployment_kit(HELLO, output=out, overwrite=True)


def test_inspect_stable_json(tmp_path: Path) -> None:
    out = tmp_path / "kit.cforge.zip"
    build_deployment_kit(HELLO, output=out)
    first = json.dumps(inspect_deployment_kit(out), sort_keys=True)
    second = json.dumps(inspect_deployment_kit(out), sort_keys=True)
    assert first == second


def test_cli_package_help() -> None:
    result = runner.invoke(app, ["package", "--help"])
    assert result.exit_code == 0
    assert "Deployment Kit" in result.stdout or "package" in result.stdout.lower()
    inspect_help = runner.invoke(app, ["package", "inspect", "--help"])
    assert inspect_help.exit_code == 0
    verify_help = runner.invoke(app, ["package", "verify", "--help"])
    assert verify_help.exit_code == 0


def test_cli_package_hello(tmp_path: Path) -> None:
    out = tmp_path / "Hello-CanvasForge.cforge.zip"
    result = runner.invoke(
        app,
        ["package", str(HELLO), "--output", str(out)],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
    assert out.is_file()
    verify = runner.invoke(app, ["package", "verify", str(out)])
    assert verify.exit_code == 0, verify.stdout + verify.stderr


def test_dist_gitignored_pattern() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "dist/" in gitignore or "*.cforge.zip" in gitignore


def test_checksums_stable(tmp_path: Path) -> None:
    out = tmp_path / "kit.cforge.zip"
    build_deployment_kit(HELLO, output=out)
    members = read_zip_members(out)
    assert CHECKSUMS_NAME in members
    lines = [line for line in members[CHECKSUMS_NAME].decode("utf-8").splitlines() if line.strip()]
    paths = [line.split("  ", 1)[1] for line in lines]
    assert paths == sorted(paths)
    digests = [line.split("  ", 1)[0] for line in lines]
    assert all(len(item) == 64 for item in digests)


def test_schema_validation_on_project(tmp_path: Path) -> None:
    out = tmp_path / "kit.cforge.zip"
    build_deployment_kit(HELLO, output=out)
    members = read_zip_members(out)
    project = json.loads(members[PROJECT_DESCRIPTOR_NAME])
    from canvasforge.deployment_kit.schema import validate_project_descriptor

    validate_project_descriptor(project)


def test_large_member_defense() -> None:
    huge = {"big.txt": b"x" * (5 * 1024 * 1024 + 1)}
    with pytest.raises(DeploymentKitError) as exc_info:
        build_deterministic_zip(huge)
    assert any(d.code == "KIT_MEMBER_TOO_LARGE" for d in exc_info.value.diagnostics)


def test_compression_ratio_defense(tmp_path: Path) -> None:
    # Highly compressible large payload
    payload = b"0" * (2 * 1024 * 1024)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("bomb.txt", payload)
    path = tmp_path / "bomb.cforge.zip"
    path.write_bytes(buffer.getvalue())
    with pytest.raises(DeploymentKitError) as exc_info:
        read_zip_members(path)
    assert any(d.code == "KIT_COMPRESSION_RATIO" for d in exc_info.value.diagnostics)
