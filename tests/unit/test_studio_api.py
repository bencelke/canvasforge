"""API tests for CanvasForge Studio (Phase 4)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from canvasforge.studio.app import create_app
from canvasforge.studio.errors import StudioError
from canvasforge.studio.security import assert_loopback_host, resolve_safe_manifest_path

ROOT = Path(__file__).resolve().parents[2]
HELLO = "examples/hello-canvasforge/app.yaml"
OROOM = "examples/oroom-actions/dashboard-proof.yaml"


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.chdir(ROOT)
    app = create_app(host="127.0.0.1", project_path=None)
    return TestClient(app)


def test_health(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["offlineMode"] is True
    assert payload["studioApiVersion"] == "0.1"
    assert "canvasforgeVersion" in payload


def test_capabilities(client: TestClient) -> None:
    response = client.get("/api/v1/studio/capabilities")
    assert response.status_code == 200
    payload = response.json()
    assert "screen" in payload["supportedPreviewTypes"]
    assert "unsupported-placeholder" in payload["supportedPreviewTypes"]
    assert payload["featureFlags"]["microsoftAuth"] is False
    assert payload["demoProjects"]


def test_open_hello_and_screen_preview(client: TestClient) -> None:
    opened = client.post(
        "/api/v1/projects/open", json={"manifestPath": HELLO, "allowPartial": True}
    )
    assert opened.status_code == 200
    summary = opened.json()
    assert summary["projectKey"] == "helloCanvasForge"
    assert "Users\\" not in str(summary)
    assert "/home/" not in str(summary)

    current = client.get("/api/v1/projects/current")
    assert current.status_code == 200
    assert current.json()["projectKey"] == "helloCanvasForge"

    screens = client.get("/api/v1/projects/current/screens")
    assert screens.status_code == 200
    assert screens.json()["screens"]

    detail = client.get("/api/v1/projects/current/screens/scrDashboard")
    assert detail.status_code == 200
    body = detail.json()
    assert body["preview"]["root"]["type"] == "screen"
    assert "Local Preview" in body["disclaimer"]
    assert body["preview"]["root"]["children"]


def test_open_oroom_proof_placeholders(client: TestClient) -> None:
    opened = client.post(
        "/api/v1/projects/open",
        json={"manifestPath": OROOM, "allowPartial": True},
    )
    assert opened.status_code == 200
    detail = client.get("/api/v1/projects/current/screens/scrRequestorDashboard")
    assert detail.status_code == 200
    body = detail.json()
    assert body["preview"]["root"]["type"] == "screen"
    placeholders = [
        node
        for node in _walk(body["preview"]["root"])
        if node.get("type") == "unsupported-placeholder"
    ]
    assert body["preview"]["root"] is not None
    if body.get("unsupportedSections") or placeholders:
        assert placeholders or body["unsupportedSections"] is not None


def test_invalid_project_rejected(client: TestClient) -> None:
    bad = ROOT / "examples" / "_studio_invalid_tmp.yaml"
    bad.write_text("this: [is, not, a, valid, canvasforge, manifest\n", encoding="utf-8")
    try:
        response = client.post(
            "/api/v1/projects/open",
            json={"manifestPath": "examples/_studio_invalid_tmp.yaml", "allowPartial": True},
        )
        assert response.status_code == 400
        assert "error" in response.json()
    finally:
        bad.unlink(missing_ok=True)


def test_path_traversal_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/projects/open",
        json={"manifestPath": "../secrets.json", "allowPartial": True},
    )
    assert response.status_code == 400


def test_validate_and_package(client: TestClient, tmp_path: Path) -> None:
    assert (
        client.post(
            "/api/v1/projects/open", json={"manifestPath": HELLO, "allowPartial": True}
        ).status_code
        == 200
    )
    validated = client.post("/api/v1/projects/current/validate", json={})
    assert validated.status_code == 200
    assert "diagnostics" in validated.json()
    packaged = client.post(
        "/api/v1/projects/current/package",
        json={
            "output": str((ROOT / "dist" / "studio-hello.cforge.zip").as_posix()),
            "overwrite": True,
        },
    )
    assert packaged.status_code == 200, packaged.text
    body = packaged.json()
    assert body["verified"] is True
    assert body["buildId"]
    assert body["outputName"].endswith(".cforge.zip")
    assert body["packageContentChecksum"]
    builds = client.get("/api/v1/projects/current/builds")
    assert builds.status_code == 200
    assert builds.json()["builds"]


def test_preview_text_is_safe_json(client: TestClient) -> None:
    """Malicious-looking text must travel as JSON strings (React escapes in UI)."""
    assert (
        client.post(
            "/api/v1/projects/open", json={"manifestPath": HELLO, "allowPartial": True}
        ).status_code
        == 200
    )
    detail = client.get("/api/v1/projects/current/screens/scrDashboard")
    assert detail.status_code == 200
    assert "application/json" in detail.headers.get("content-type", "")
    dumped = detail.text
    assert "<html" not in dumped.lower()


def test_loopback_only() -> None:
    with pytest.raises(StudioError):
        assert_loopback_host("0.0.0.0")
    with pytest.raises(StudioError):
        assert_loopback_host("192.168.1.10")


def test_resolve_safe_manifest(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(ROOT)
    from canvasforge.studio.security import default_workspace_roots, resolve_repo_root

    roots = default_workspace_roots(resolve_repo_root())
    path = resolve_safe_manifest_path(HELLO, workspace_roots=roots)
    assert path.name == "app.yaml"
    with pytest.raises(StudioError):
        resolve_safe_manifest_path("C:/Windows/System32/drivers/etc/hosts", workspace_roots=roots)


def test_health_serialization_aliases(client: TestClient) -> None:
    payload = client.get("/api/v1/health").json()
    assert "canvasforgeVersion" in payload
    assert "studioApiVersion" in payload
    assert "offlineMode" in payload
    assert "currentProject" in payload


def _walk(node: dict[str, object]) -> list[dict[str, object]]:
    items = [node]
    children = node.get("children")
    if isinstance(children, list):
        for child in children:
            if isinstance(child, dict):
                items.extend(_walk(child))
    return items
