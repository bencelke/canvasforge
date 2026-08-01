"""Offline environment diagnostics."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path

from canvasforge import __version__


@dataclass(frozen=True, slots=True)
class DoctorCheck:
    name: str
    status: str  # ok | warn | fail
    detail: str


def _package_version() -> str:
    try:
        return metadata.version("canvasforge")
    except metadata.PackageNotFoundError:
        return __version__


def _example_manifests(repo_root: Path) -> list[Path]:
    return [
        repo_root / "examples" / "hello-canvasforge" / "app.yaml",
        repo_root / "examples" / "oroom-actions" / "app.yaml",
    ]


def find_repo_root(start: Path | None = None) -> Path | None:
    """Walk parents looking for pyproject.toml naming canvasforge."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        pyproject = candidate / "pyproject.toml"
        if pyproject.is_file():
            text = pyproject.read_text(encoding="utf-8")
            if 'name = "canvasforge"' in text:
                return candidate
    return None


def run_doctor(cwd: Path | None = None) -> list[DoctorCheck]:
    """Run offline doctor checks. Never contacts Microsoft services."""
    working = (cwd or Path.cwd()).resolve()
    checks: list[DoctorCheck] = []

    py_ok = sys.version_info >= (3, 12)
    checks.append(
        DoctorCheck(
            name="Python version",
            status="ok" if py_ok else "fail",
            detail=f"{sys.version.split()[0]} (requires >= 3.12)",
        )
    )

    version = _package_version()
    checks.append(
        DoctorCheck(
            name="Package installation",
            status="ok",
            detail=f"canvasforge {version} importable",
        )
    )

    checks.append(
        DoctorCheck(
            name="Working directory",
            status="ok",
            detail=str(working),
        )
    )

    repo_root = find_repo_root(working)
    if repo_root is None:
        checks.append(
            DoctorCheck(
                name="Example manifests",
                status="warn",
                detail="Could not locate CanvasForge repo root from working directory",
            )
        )
    else:
        missing = [str(path) for path in _example_manifests(repo_root) if not path.is_file()]
        if missing:
            checks.append(
                DoctorCheck(
                    name="Example manifests",
                    status="warn",
                    detail="Missing: " + ", ".join(missing),
                )
            )
        else:
            checks.append(
                DoctorCheck(
                    name="Example manifests",
                    status="ok",
                    detail="hello-canvasforge and oroom-actions manifests present",
                )
            )

    checks.append(
        DoctorCheck(
            name="Offline mode",
            status="ok",
            detail=(
                "Enabled — no Microsoft 365 / Power Platform / SharePoint checks "
                "are performed in Phase 1"
            ),
        )
    )

    checks.append(
        DoctorCheck(
            name="Network / authentication",
            status="ok",
            detail="Not applicable — Phase 1 performs no network or auth operations",
        )
    )

    return checks


def doctor_passed(checks: list[DoctorCheck]) -> bool:
    return all(check.status != "fail" for check in checks)
