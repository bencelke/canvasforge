"""CanvasForge command-line interface."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from canvasforge import __version__
from canvasforge.diagnostics.doctor import doctor_passed, run_doctor
from canvasforge.errors import CanvasForgeError
from canvasforge.manifest.loader import load_manifest_dict
from canvasforge.manifest.models import AppManifest, Section
from canvasforge.manifest.validator import parse_manifest
from canvasforge.planner import build_generation_plan

app = typer.Typer(
    name="canvasforge",
    help=(
        "CanvasForge — local, manifest-driven planning and validation for "
        "Microsoft Power Apps Canvas frontends (offline Phase 1)."
    ),
    no_args_is_help=True,
    add_completion=False,
)
console = Console()
err_console = Console(stderr=True)


def _load_and_parse(manifest_path: Path) -> AppManifest:
    data = load_manifest_dict(manifest_path)
    return parse_manifest(data)


def _print_failure(exc: CanvasForgeError) -> None:
    err_console.print(f"[bold red]Error:[/bold red] {exc.message}")
    for diagnostic in exc.diagnostics:
        color = {"error": "red", "warning": "yellow", "info": "cyan"}.get(
            diagnostic.severity, "red"
        )
        err_console.print(f"  [{color}]{diagnostic.format_terminal()}[/{color}]")


@app.command("version")
def version_command() -> None:
    """Print the CanvasForge package version."""
    console.print(__version__)


@app.command("doctor")
def doctor_command() -> None:
    """Check local environment health (offline only; no Microsoft services)."""
    checks = run_doctor()
    table = Table(title="CanvasForge Doctor (offline)")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Detail")
    for check in checks:
        style = {"ok": "green", "warn": "yellow", "fail": "red"}.get(check.status, "white")
        table.add_row(check.name, Text(check.status.upper(), style=style), check.detail)
    console.print(table)
    if not doctor_passed(checks):
        raise typer.Exit(code=1)


@app.command("validate")
def validate_command(
    manifest_path: Annotated[
        Path,
        typer.Argument(exists=False, dir_okay=False, readable=False, help="Path to app.yaml"),
    ],
) -> None:
    """Validate a manifest (schema + semantic rules)."""
    try:
        manifest = _load_and_parse(manifest_path)
    except CanvasForgeError as exc:
        _print_failure(exc)
        raise typer.Exit(code=1) from exc

    console.print(
        f"[green]Valid[/green] — {manifest.app.name} "
        f"({manifest.app.key}) manifestVersion={manifest.app.manifest_version}"
    )


def _count_sections(sections: list[Section]) -> int:
    total = 0
    for section in sections:
        total += 1
        total += _count_sections(section.children)
    return total


@app.command("inspect")
def inspect_command(
    manifest_path: Annotated[
        Path,
        typer.Argument(exists=False, dir_okay=False, readable=False, help="Path to app.yaml"),
    ],
) -> None:
    """Print a readable summary of a validated manifest."""
    try:
        manifest = _load_and_parse(manifest_path)
    except CanvasForgeError as exc:
        _print_failure(exc)
        raise typer.Exit(code=1) from exc

    console.print(
        Panel.fit(
            f"[bold]{manifest.app.name}[/bold]\n"
            f"key={manifest.app.key}  version={manifest.app.version}  "
            f"manifestVersion={manifest.app.manifest_version}\n"
            f"startScreen={manifest.app.start_screen}  layout={manifest.app.layout or '—'}",
            title="App",
        )
    )

    screens = Table(title="Screens")
    screens.add_column("Key")
    screens.add_column("Name")
    screens.add_column("Title")
    screens.add_column("Sections")
    screens.add_column("Permissions")
    for screen in manifest.screens:
        screens.add_row(
            screen.key,
            screen.name,
            screen.title or "—",
            str(_count_sections(screen.sections)),
            ", ".join(screen.permissions) or "—",
        )
    console.print(screens)

    sections_table = Table(title="Sections (flattened)")
    sections_table.add_column("Screen")
    sections_table.add_column("Key")
    sections_table.add_column("Type")
    sections_table.add_column("Title")
    sections_table.add_column("Data source")

    def _add_sections(screen_key: str, sections: list[Section]) -> None:
        for section in sections:
            sections_table.add_row(
                screen_key,
                section.key,
                section.type,
                section.title or "—",
                section.data_source or "—",
            )
            if section.children:
                _add_sections(screen_key, section.children)

    for screen in manifest.screens:
        _add_sections(screen.key, screen.sections)
    console.print(sections_table)

    sources = Table(title="Data sources")
    sources.add_column("Key")
    sources.add_column("Kind")
    sources.add_column("Mode")
    sources.add_column("Collection")
    if manifest.data_sources:
        for source in manifest.data_sources:
            sources.add_row(
                source.key,
                source.kind,
                source.mode,
                source.collection or "—",
            )
    else:
        sources.add_row("—", "—", "—", "(none)")
    console.print(sources)

    nav = Table(title="Navigation")
    nav.add_column("Key")
    nav.add_column("Label")
    nav.add_column("Target")
    nav.add_column("Order")
    nav.add_column("Permission")
    nav.add_column("Implemented")
    if manifest.navigation:
        for item in sorted(
            manifest.navigation, key=lambda nav_item: (nav_item.sort_order, nav_item.key)
        ):
            nav.add_row(
                item.key,
                item.label,
                item.target_screen,
                str(item.sort_order),
                item.permission or "—",
                str(item.implemented),
            )
    else:
        nav.add_row("—", "—", "—", "—", "—", "(none)")
    console.print(nav)

    perms = Table(title="Permissions")
    perms.add_column("Key")
    perms.add_column("Description")
    if manifest.permissions:
        for permission in manifest.permissions:
            perms.add_row(permission.key, permission.description or "—")
    else:
        perms.add_row("—", "(none)")
    console.print(perms)

    bp = manifest.breakpoints
    console.print(
        Panel.fit(
            f"mobile={bp.mobile}  tablet={bp.tablet}  desktop={bp.desktop}",
            title="Breakpoints",
        )
    )


@app.command("plan")
def plan_command(
    manifest_path: Annotated[
        Path,
        typer.Argument(exists=False, dir_okay=False, readable=False, help="Path to app.yaml"),
    ],
) -> None:
    """Produce a deterministic high-level generation plan (no Power Apps output)."""
    try:
        manifest = _load_and_parse(manifest_path)
    except CanvasForgeError as exc:
        _print_failure(exc)
        raise typer.Exit(code=1) from exc

    plan = build_generation_plan(manifest)
    console.print(plan.render())


def main() -> None:
    """Entrypoint for console_scripts."""
    app()


if __name__ == "__main__":
    main()
