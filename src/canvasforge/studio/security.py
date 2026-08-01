"""Workspace path security for CanvasForge Studio."""

from __future__ import annotations

from pathlib import Path

from canvasforge.studio.errors import StudioError, studio_error

MAX_MANIFEST_BYTES = 1_000_000
FORBIDDEN_NAME_PARTS = {
    ".env",
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    "credentials.json",
    "secrets.json",
    "auth.json",
}


def default_workspace_roots(repo_root: Path) -> list[Path]:
    root = repo_root.resolve()
    return [root, (root / "examples").resolve()]


def resolve_repo_root() -> Path:
    """Locate repository root from CWD or package parents."""
    cwd = Path.cwd().resolve()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / "pyproject.toml").is_file() and (candidate / "examples").is_dir():
            return candidate
    # Fallback: package installed from src layout
    here = Path(__file__).resolve()
    for candidate in here.parents:
        if (candidate / "pyproject.toml").is_file() and (candidate / "examples").is_dir():
            return candidate
    return cwd


def assert_loopback_host(host: str) -> None:
    normalized = host.strip().lower()
    if normalized not in {"127.0.0.1", "localhost", "::1"}:
        raise StudioError(
            "Non-loopback bind refused",
            diagnostics=[
                studio_error(
                    "STUDIO_NON_LOOPBACK",
                    f"Host '{host}' is not allowed; Phase 4 binds to loopback only",
                )
            ],
        )


def resolve_safe_manifest_path(raw_path: str | Path, *, workspace_roots: list[Path]) -> Path:
    """Resolve a manifest path strictly within allowed workspace roots."""
    path = Path(raw_path)
    if not path.is_absolute():
        # Try each root
        candidates = [(root / path).resolve() for root in workspace_roots]
    else:
        candidates = [path.resolve()]

    for resolved in candidates:
        if _is_under_roots(resolved, workspace_roots) and resolved.is_file():
            _assert_safe_file(resolved)
            return resolved

    raise StudioError(
        "Manifest path rejected",
        diagnostics=[
            studio_error(
                "STUDIO_PATH_REJECTED",
                "Path is outside allowed workspace roots or does not exist",
                path=str(raw_path),
            )
        ],
    )


def resolve_safe_output_path(
    raw_path: str | Path,
    *,
    workspace_roots: list[Path],
    default_dir: Path,
) -> Path:
    path = Path(raw_path)
    path = (default_dir / path).resolve() if not path.is_absolute() else path.resolve()
    parent = path.parent
    if not _is_under_roots(parent, [*workspace_roots, default_dir.resolve()]):
        raise StudioError(
            "Output path rejected",
            diagnostics=[
                studio_error(
                    "STUDIO_OUTPUT_REJECTED",
                    "Output must remain under workspace or configured dist directory",
                )
            ],
        )
    if path.suffix.lower() != ".zip" and not str(path).endswith(".cforge.zip"):
        if path.is_dir() or path.suffix == "":
            path = path / "studio-build.cforge.zip"
        else:
            raise StudioError(
                "Output must be a .cforge.zip path",
                diagnostics=[studio_error("STUDIO_OUTPUT_TYPE", "Expected .cforge.zip")],
            )
    return path


def _is_under_roots(path: Path, roots: list[Path]) -> bool:
    resolved = path.resolve()
    for root in roots:
        try:
            resolved.relative_to(root.resolve())
            return True
        except ValueError:
            continue
    return False


def _assert_safe_file(path: Path) -> None:
    name = path.name.lower()
    if any(part in path.parts for part in FORBIDDEN_NAME_PARTS):
        raise StudioError(
            "Forbidden path component",
            diagnostics=[
                studio_error("STUDIO_FORBIDDEN_PATH", "Path contains a blocked component")
            ],
        )
    if name.endswith((".pem", ".key", ".pfx", ".p12", ".msapp", ".env")):
        raise StudioError(
            "Forbidden file type",
            diagnostics=[studio_error("STUDIO_FORBIDDEN_TYPE", f"Refusing to open '{name}'")],
        )
    size = path.stat().st_size
    if size > MAX_MANIFEST_BYTES:
        raise StudioError(
            "Manifest too large",
            diagnostics=[
                studio_error(
                    "STUDIO_MANIFEST_TOO_LARGE",
                    f"Manifest exceeds {MAX_MANIFEST_BYTES} bytes",
                )
            ],
        )
