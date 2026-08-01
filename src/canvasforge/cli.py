"""CanvasForge command-line interface."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from typer.core import TyperGroup

from canvasforge import __version__
from canvasforge.controls.registry import default_registry
from canvasforge.deployment_kit import (
    build_deployment_kit,
    inspect_deployment_kit,
    verify_deployment_kit,
)
from canvasforge.diagnostics.doctor import doctor_passed, run_doctor
from canvasforge.errors import CanvasForgeError
from canvasforge.evidence.store import (
    import_evidence_fixture,
    list_evidence_records,
    records_as_dicts,
)
from canvasforge.generate.pipeline import run_generation
from canvasforge.manifest.loader import load_manifest_dict
from canvasforge.manifest.models import AppManifest, Section
from canvasforge.manifest.validator import parse_manifest
from canvasforge.planner import build_generation_plan


class _PackageTyperGroup(TyperGroup):
    """Treat ``package <manifest.yaml> ...`` as ``package build <manifest.yaml> ...``."""

    def resolve_command(self, ctx: Any, args: list[str]) -> tuple[str | None, Any, list[str]]:
        if args:
            first = args[0]
            if first not in self.commands and first.endswith((".yaml", ".yml")):
                args = ["build", *args]
        return super().resolve_command(ctx, args)


app = typer.Typer(
    name="canvasforge",
    help=(
        "CanvasForge — local, manifest-driven planning, Candidate Code View "
        "generation, and Deployment Kit packaging for Microsoft Power Apps "
        "Canvas frontends (offline)."
    ),
    no_args_is_help=True,
    add_completion=False,
)
evidence_app = typer.Typer(
    name="evidence",
    help="Inspect and import offline Studio evidence records.",
    no_args_is_help=True,
)
package_app = typer.Typer(
    name="package",
    help="Build, inspect, and verify portable Deployment Kits (.cforge.zip).",
    no_args_is_help=True,
    cls=_PackageTyperGroup,
)
app.add_typer(evidence_app, name="evidence")
app.add_typer(package_app, name="package")
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


@app.command("controls")
def controls_command(
    as_json: Annotated[
        bool,
        typer.Option("--json", help="Emit machine-readable JSON"),
    ] = False,
) -> None:
    """List supported logical controls, properties, and evidence status."""
    registry = default_registry()
    controls = registry.list_controls()
    if as_json:
        payload = [control.model_dump(mode="json") for control in controls]
        console.print_json(data=payload)
        return

    table = Table(title="CanvasForge control allowlist (Phase 2)")
    table.add_column("Logical")
    table.add_column("Code View ID")
    table.add_column("Evidence")
    table.add_column("Properties")
    table.add_column("Notes")
    for control in controls:
        props = ", ".join(prop.name for prop in control.properties)
        table.add_row(
            control.logical_name,
            control.code_view_identifier,
            control.evidence_status,
            props,
            control.notes or "—",
        )
    console.print(table)
    console.print(
        "[yellow]All generated output is Candidate until Studio-validated evidence exists.[/yellow]"
    )


@app.command("generate")
def generate_command(
    manifest_path: Annotated[
        Path,
        typer.Argument(exists=False, dir_okay=False, readable=False, help="Path to app.yaml"),
    ],
    target: Annotated[
        str,
        typer.Option("--target", help="Target adapter (Phase 2: code-view)"),
    ] = "code-view",
    output: Annotated[
        Path | None,
        typer.Option("--output", help="Output directory (default: generated/<app-key>)"),
    ] = None,
    screen: Annotated[
        str | None,
        typer.Option("--screen", help="Generate a single screen key"),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Build artifacts in memory without writing files"),
    ] = False,
    allow_partial: Annotated[
        bool,
        typer.Option(
            "--allow-partial",
            help="Omit unsupported sections with warnings instead of failing",
        ),
    ] = False,
    as_json: Annotated[
        bool,
        typer.Option("--json", help="Emit machine-readable summary JSON"),
    ] = False,
) -> None:
    """Generate Candidate Code View YAML and reports from a manifest."""
    try:
        result = run_generation(
            manifest_path,
            target=target,
            output_dir=output,
            screen=screen,
            dry_run=dry_run,
            allow_partial=allow_partial,
        )
    except CanvasForgeError as exc:
        _print_failure(exc)
        raise typer.Exit(code=1) from exc

    if as_json:
        console.print_json(
            data={
                "buildId": result.build_id,
                "outputDir": str(result.output_dir) if result.output_dir else None,
                "screens": list(result.yaml_by_screen.keys()),
                "report": result.report,
                "diagnostics": [d.to_dict() for d in result.diagnostics],
            }
        )
        return

    console.print(
        Panel.fit(
            f"[bold]Candidate generation complete[/bold]\n"
            f"buildId={result.build_id}\n"
            f"status=Studio-unvalidated Candidate\n"
            f"screens={', '.join(result.yaml_by_screen.keys())}",
            title="generate",
        )
    )
    if result.output_dir is not None:
        console.print(f"Output: {result.output_dir}")
        for artifact in result.artifacts:
            console.print(f"  - {artifact.relative_path}")
    else:
        console.print("[cyan]Dry run — no files written[/cyan]")
    for diagnostic in result.diagnostics:
        if diagnostic.severity == "warning":
            console.print(f"[yellow]{diagnostic.format_terminal()}[/yellow]")


@evidence_app.command("list")
def evidence_list_command(
    as_json: Annotated[
        bool,
        typer.Option("--json", help="Emit JSON"),
    ] = False,
) -> None:
    """List bootstrap and local evidence records."""
    records = list_evidence_records()
    if as_json:
        console.print_json(data=records_as_dicts(records))
        return
    table = Table(title="Evidence records")
    table.add_column("ID")
    table.add_column("Control")
    table.add_column("Property")
    table.add_column("Source")
    table.add_column("Env")
    table.add_column("Notes")
    for record in records:
        table.add_row(
            record.evidence_id,
            record.control_type,
            record.property or "—",
            record.source_type,
            record.environment_class,
            (record.notes or "—")[:60],
        )
    console.print(table)
    console.print(
        "[yellow]No automatic promotion. Studio validation remains manual and explicit.[/yellow]"
    )


@evidence_app.command("import")
def evidence_import_command(
    file_path: Annotated[
        Path,
        typer.Argument(exists=False, dir_okay=False, readable=False, help="Local fixture file"),
    ],
    control_type: Annotated[
        str,
        typer.Option("--control-type", help="Logical or Code View control type label"),
    ] = "Unknown",
    property_name: Annotated[
        str | None,
        typer.Option("--property", help="Optional property name"),
    ] = None,
) -> None:
    """Import a local Studio-exported text fixture (offline, size-limited)."""
    try:
        record = import_evidence_fixture(
            file_path,
            control_type=control_type,
            property_name=property_name,
        )
    except CanvasForgeError as exc:
        _print_failure(exc)
        raise typer.Exit(code=1) from exc
    console.print(
        f"[green]Imported[/green] {record.evidence_id} "
        f"(checksum={record.checksum[:12]}…, sourceType={record.source_type})"
    )
    console.print(
        "[yellow]Evidence status is studio-exported Candidate — not auto-validated.[/yellow]"
    )


@evidence_app.command("record-validation")
def evidence_record_validation_command() -> None:
    """Describe how to record Studio validation outcomes."""
    console.print(
        Panel.fit(
            "Studio validation is manual.\n\n"
            "1. Paste Candidate YAML in a sandbox Canvas app.\n"
            "2. Note Accepted / Accepted with modifications / Rejected.\n"
            "3. Store a sanitized fixture under evidence/fixtures/.\n"
            "4. Add a reviewed JSON record under evidence/records/.\n"
            "5. Never commit tenant IDs, URLs, or personal/military data.\n\n"
            "See docs/studio-round-trip.md",
            title="evidence record-validation",
        )
    )


@package_app.command("build")
def package_build_command(
    manifest_path: Annotated[
        Path,
        typer.Argument(help="Path to app.yaml"),
    ],
    output: Annotated[
        Path | None,
        typer.Option("--output", help="Output .cforge.zip path"),
    ] = None,
    project_name: Annotated[
        str | None,
        typer.Option("--project-name", help="Override project display/file name"),
    ] = None,
    target: Annotated[
        str,
        typer.Option("--target", help="Target adapter (Phase 3B: code-view)"),
    ] = "code-view",
    screen: Annotated[
        str | None,
        typer.Option("--screen", help="Package a single screen key"),
    ] = None,
    compatibility_profile: Annotated[
        str,
        typer.Option("--compatibility-profile", help="Compatibility profile id"),
    ] = "documented-bootstrap",
    allow_partial: Annotated[
        bool,
        typer.Option("--allow-partial", help="Allow partial generation"),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Plan package without writing a ZIP"),
    ] = False,
    overwrite: Annotated[
        bool,
        typer.Option("--overwrite", help="Overwrite an existing output ZIP"),
    ] = False,
    as_json: Annotated[
        bool,
        typer.Option("--json", help="Emit machine-readable JSON"),
    ] = False,
    include_mock_data: Annotated[
        bool,
        typer.Option("--include-mock-data", help="Include fictional mock records"),
    ] = False,
    non_reproducible_metadata: Annotated[
        bool,
        typer.Option(
            "--non-reproducible-metadata",
            help="Allow non-reproducible notes (still no machine identity)",
        ),
    ] = False,
) -> None:
    """Build a portable Deployment Kit (``.cforge.zip``).

    ``canvasforge package <manifest.yaml>`` is accepted as shorthand for
    ``canvasforge package build <manifest.yaml>``.
    """
    try:
        result = build_deployment_kit(
            manifest_path,
            output=output,
            project_name=project_name,
            target=target,
            screen=screen,
            compatibility_profile=compatibility_profile,
            allow_partial=allow_partial,
            dry_run=dry_run,
            overwrite=overwrite,
            include_mock_data=include_mock_data,
            non_reproducible_metadata=non_reproducible_metadata,
        )
    except CanvasForgeError as exc:
        _print_failure(exc)
        raise typer.Exit(code=1) from exc

    if as_json:
        console.print_json(
            data={
                "buildId": result.build_id,
                "output": str(result.output_path) if result.output_path else None,
                "dryRun": result.dry_run,
                "expectedSize": result.expected_size,
                "securityStatus": result.security_status,
                "project": result.project,
                "members": sorted(result.members.keys()),
                "omitted": result.omitted,
                "diagnostics": [d.to_dict() for d in result.diagnostics],
            }
        )
        return

    if dry_run:
        console.print(
            Panel.fit(
                f"[bold]Dry run — no ZIP written[/bold]\n"
                f"source={manifest_path.name}\n"
                f"targetOutput={(output.name if output else '(default dist/)')}\n"
                f"buildId={result.build_id}\n"
                f"maturity={result.project.get('buildMaturity')}\n"
                f"security={result.security_status}\n"
                f"expectedSize={result.expected_size} bytes\n"
                f"members={len(result.members)}\n"
                f"omitted={len(result.omitted)}",
                title="package",
            )
        )
        for name in sorted(result.members.keys()):
            console.print(f"  include: {name}")
        for item in result.omitted:
            console.print(f"  omit: {item['path']} — {item['reason']}")
        for diagnostic in result.diagnostics:
            if diagnostic.severity == "warning":
                console.print(f"[yellow]{diagnostic.format_terminal()}[/yellow]")
        return

    console.print(
        Panel.fit(
            f"[bold]Deployment Kit built[/bold]\n"
            f"output={result.output_path}\n"
            f"buildId={result.build_id}\n"
            f"maturity={result.project.get('buildMaturity')}\n"
            f"security={result.security_status}\n"
            f"size={result.expected_size} bytes\n"
            f"status=Studio-unvalidated Candidate",
            title="package",
        )
    )


@package_app.command("inspect")
def package_inspect_command(
    kit_path: Annotated[
        Path,
        typer.Argument(exists=False, dir_okay=False, readable=False, help="Path to .cforge.zip"),
    ],
    as_json: Annotated[
        bool,
        typer.Option("--json", help="Emit JSON"),
    ] = False,
) -> None:
    """Inspect a Deployment Kit without extracting it."""
    try:
        payload = inspect_deployment_kit(kit_path)
    except CanvasForgeError as exc:
        _print_failure(exc)
        raise typer.Exit(code=1) from exc

    if as_json:
        console.print_json(data=payload)
        return

    console.print(
        Panel.fit(
            f"[bold]{payload.get('projectName')}[/bold] ({payload.get('projectKey')})\n"
            f"schema={payload.get('packageSchemaVersion')}\n"
            f"canvasforge={payload.get('canvasforgeVersion')}\n"
            f"buildId={payload.get('buildId')}\n"
            f"maturity={payload.get('buildMaturity')}\n"
            f"profile={payload.get('compatibilityProfileId')}@"
            f"{payload.get('compatibilityProfileVersion')}\n"
            f"checksumStatus={payload.get('checksumStatus')}\n"
            f"security={payload.get('securityClassification')}\n"
            f"mockData={payload.get('mockDataClassification')}\n"
            f"members={payload.get('memberCount')}",
            title="package inspect",
        )
    )
    console.print("[bold]Deployment steps[/bold]")
    for step in payload.get("deploymentSteps", []):
        console.print(f"  {step}")
    if payload.get("omitted"):
        console.print("[bold]Omitted[/bold]")
        for item in payload["omitted"]:
            console.print(f"  - {item.get('path')}: {item.get('reason')}")


@package_app.command("verify")
def package_verify_command(
    kit_path: Annotated[
        Path,
        typer.Argument(exists=False, dir_okay=False, readable=False, help="Path to .cforge.zip"),
    ],
    as_json: Annotated[
        bool,
        typer.Option("--json", help="Emit JSON"),
    ] = False,
) -> None:
    """Verify Deployment Kit structure, checksums, and safety limits."""
    try:
        payload = verify_deployment_kit(kit_path)
    except CanvasForgeError as exc:
        _print_failure(exc)
        raise typer.Exit(code=1) from exc

    if as_json:
        console.print_json(data=payload)
        return

    console.print(
        f"[green]Verified[/green] buildId={payload.get('buildId')} "
        f"members={payload.get('memberCount')} "
        f"contentChecksum={str(payload.get('packageContentChecksum', ''))[:12]}…"
    )


def main() -> None:
    """Entrypoint for console_scripts."""
    app()


if __name__ == "__main__":
    main()
