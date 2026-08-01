"""Local Studio process launcher."""

from __future__ import annotations

import socket
import threading
import time
import webbrowser
from collections.abc import Callable
from pathlib import Path

import uvicorn

from canvasforge.studio.app import create_app
from canvasforge.studio.security import assert_loopback_host


def pick_free_port(host: str = "127.0.0.1") -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def run_studio(
    *,
    host: str = "127.0.0.1",
    api_port: int | None = None,
    project: str | Path | None = None,
    open_browser: bool = True,
    cors_origins: list[str] | None = None,
) -> None:
    assert_loopback_host(host)
    port = api_port or pick_free_port(host)
    app = create_app(
        host=host,
        cors_origins=cors_origins,
        project_path=str(project) if project else None,
    )
    config = uvicorn.Config(app, host=host, port=port, log_level="info", access_log=False)
    server = uvicorn.Server(config)

    url = f"http://{host}:{port}/"
    print(f"CanvasForge Studio (offline) listening on {url}")
    if project:
        print(f"Project: {project}")

    if open_browser:
        threading.Thread(target=_delayed_open, args=(url,), daemon=True).start()

    server.run()


def _delayed_open(url: str, delay: float = 0.8) -> None:
    time.sleep(delay)
    webbrowser.open(url)


def run_dev_proxy_note() -> Callable[[], None]:
    """Placeholder hook for future Vite orchestration."""
    return lambda: None
