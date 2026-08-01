"""Deterministic generation planning (no Power Apps output in Phase 1)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from canvasforge.manifest.models import AppManifest, Section


class PlanStep(BaseModel):
    """A single deterministic planning step."""

    model_config = ConfigDict(extra="forbid")

    index: int = Field(ge=1)
    action: str
    target: str
    detail: str


class GenerationPlan(BaseModel):
    """High-level generation plan derived from a manifest."""

    model_config = ConfigDict(extra="forbid")

    app_key: str
    app_name: str
    manifest_version: str
    steps: list[PlanStep]

    def render(self) -> str:
        """Stable text rendering for CLI and snapshot tests."""
        lines = [
            f"Generation plan for {self.app_name} ({self.app_key})",
            f"Manifest version: {self.manifest_version}",
            f"Steps: {len(self.steps)}",
            "",
        ]
        for step in self.steps:
            lines.append(f"{step.index}. {step.action}: {step.target} — {step.detail}")
        lines.append("")
        lines.append("Note: Phase 1 does not generate Power Apps YAML or packages.")
        return "\n".join(lines)


def _section_steps(screen_key: str, sections: list[Section], steps: list[PlanStep]) -> None:
    for section in sections:
        steps.append(
            PlanStep(
                index=len(steps) + 1,
                action="Add section",
                target=f"{screen_key}/{section.key}",
                detail=f"type={section.type}"
                + (f", title={section.title}" if section.title else "")
                + (f", dataSource={section.data_source}" if section.data_source else ""),
            )
        )
        if section.children:
            _section_steps(screen_key, section.children, steps)


def build_generation_plan(manifest: AppManifest) -> GenerationPlan:
    """Build a deterministic high-level plan from a validated manifest."""
    steps: list[PlanStep] = []

    if manifest.theme is not None:
        steps.append(
            PlanStep(
                index=len(steps) + 1,
                action="Initialize theme",
                target=manifest.theme.key,
                detail=f"mode={manifest.theme.mode}",
            )
        )
    elif manifest.app.theme is not None:
        steps.append(
            PlanStep(
                index=len(steps) + 1,
                action="Initialize theme",
                target=manifest.app.theme,
                detail="theme reference only (no theme block tokens)",
            )
        )

    for source in sorted(manifest.data_sources, key=lambda item: item.key):
        collection = source.collection or "(none)"
        steps.append(
            PlanStep(
                index=len(steps) + 1,
                action="Initialize mock collection",
                target=source.key,
                detail=f"kind={source.kind}, mode={source.mode}, collection={collection}",
            )
        )

    # Stable screen order: start screen first, then remaining by key.
    screens_by_key = {screen.key: screen for screen in manifest.screens}
    ordered_keys = [
        manifest.app.start_screen,
        *sorted(key for key in screens_by_key if key != manifest.app.start_screen),
    ]

    for screen_key in ordered_keys:
        screen = screens_by_key[screen_key]
        steps.append(
            PlanStep(
                index=len(steps) + 1,
                action="Create screen",
                target=screen.key,
                detail=f"name={screen.name}"
                + (f", title={screen.title}" if screen.title else "")
                + (f", shell={screen.shell}" if screen.shell else ""),
            )
        )
        _section_steps(screen.key, screen.sections, steps)

    for item in sorted(manifest.navigation, key=lambda nav: (nav.sort_order, nav.key)):
        steps.append(
            PlanStep(
                index=len(steps) + 1,
                action="Register navigation",
                target=item.key,
                detail=(
                    f"label={item.label}, targetScreen={item.target_screen}, "
                    f"implemented={item.implemented}"
                ),
            )
        )

    steps.append(
        PlanStep(
            index=len(steps) + 1,
            action="Set start screen",
            target=manifest.app.start_screen,
            detail="Studio remains the final validation authority",
        )
    )

    return GenerationPlan(
        app_key=manifest.app.key,
        app_name=manifest.app.name,
        manifest_version=manifest.app.manifest_version,
        steps=steps,
    )
