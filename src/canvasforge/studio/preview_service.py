"""Preview Model adapter — maps AppIR ControlNode trees to frontend-neutral nodes."""

from __future__ import annotations

from typing import Any, Literal

from canvasforge.ir.models import AppIR, ControlNode, ScreenIR
from canvasforge.studio.models import (
    PreviewApp,
    PreviewDiagnostic,
    PreviewNode,
    PreviewScreen,
    PreviewStyle,
)

CONTROL_TO_PREVIEW: dict[str, str] = {
    "Screen": "screen",
    "VerticalContainer": "vertical-container",
    "HorizontalContainer": "horizontal-container",
    "Text": "text",
    "Button": "button",
    "Label": "text",
}

SECTIONISH_HINTS: dict[str, str] = {
    "summary": "summary-card",
    "grid": "summary-grid",
    "empty": "empty-state",
    "card": "summary-card",
}


def build_preview_app(
    ir: AppIR,
    *,
    breakpoints: dict[str, int],
    unsupported_by_screen: dict[str, list[str]] | None = None,
    diagnostics: list[dict[str, Any]] | None = None,
) -> PreviewApp:
    unsupported_by_screen = unsupported_by_screen or {}
    screens: list[PreviewScreen] = []
    for screen in ir.screens:
        screens.append(
            _screen_to_preview(
                screen,
                theme=ir.theme_tokens,
                unsupported=unsupported_by_screen.get(screen.key, []),
                diagnostics=diagnostics or [],
            )
        )
    return PreviewApp(
        appKey=ir.app_key,
        appName=ir.app_name,
        themeTokens=dict(ir.theme_tokens),
        breakpoints=breakpoints,
        screens=screens,
    )


def _screen_to_preview(
    screen: ScreenIR,
    *,
    theme: dict[str, str],
    unsupported: list[str],
    diagnostics: list[dict[str, Any]],
) -> PreviewScreen:
    related = [
        PreviewDiagnostic(
            code=str(item.get("code", "DIAG")),
            message=str(item.get("message", "")),
            severity=_severity(item.get("severity")),
            path=str(item.get("path", "$")),
        )
        for item in diagnostics
        if screen.key in str(item.get("path", ""))
    ]
    root = _node_to_preview(screen.root, theme=theme)
    for key in unsupported:
        root.children.append(
            PreviewNode(
                id=f"{screen.root.id}/unsupported/{key}",
                name=f"unsupported:{key}",
                type="unsupported-placeholder",
                sourcePath=f"$.screens[?(@.key=='{screen.key}')].sections",
                text=f"Section '{key}' is not generatable in the current allowlist",
                maturity="unsupported",
                expectedControl=None,
                diagnostics=[
                    PreviewDiagnostic(
                        code="SECTION_NOT_GENERATABLE",
                        message=f"Unsupported section '{key}' shown as placeholder",
                        severity="warning",
                        path=f"$.screens.{screen.key}.sections.{key}",
                    )
                ],
                styles=PreviewStyle(
                    fill="#FFF4E5",
                    color="#8A5A00",
                    border="1px dashed #D9993B",
                    padding="12px",
                    borderRadius=6,
                ),
            )
        )
    return PreviewScreen(
        key=screen.key,
        name=screen.name,
        title=screen.title,
        root=root,
        unsupportedSections=unsupported,
        diagnostics=related,
    )


def _node_to_preview(node: ControlNode, *, theme: dict[str, str]) -> PreviewNode:
    preview_type = CONTROL_TO_PREVIEW.get(node.control_type, "unsupported-placeholder")
    # Heuristic enrichment from control name for section-like containers
    lower_name = node.name.lower()
    for hint, mapped in SECTIONISH_HINTS.items():
        if hint in lower_name and preview_type in {"vertical-container", "horizontal-container"}:
            preview_type = mapped
            break

    props = {prop.name: prop.value for prop in node.properties}
    text = None
    for key in ("Text", "Content", "Label"):
        if key in props:
            text = str(props[key])
            break
    # Strip Power Fx quoting if present
    if isinstance(text, str) and text.startswith('="') and text.endswith('"'):
        text = text[2:-1].replace('""', '"')

    styles = PreviewStyle(
        fill=_theme_or(theme, "surface", props.get("Fill")),
        color=_theme_or(theme, "text", None),
        fontSize=14 if preview_type == "text" else None,
        fontWeight="600" if "Title" in node.name or "Header" in node.name else None,
        padding="8px" if preview_type.endswith("container") or preview_type == "screen" else "4px",
        gap=node.layout.gap if node.layout and node.layout.gap is not None else 8,
        flexDirection=(
            "row"
            if (node.layout and node.layout.direction == "horizontal")
            or preview_type == "horizontal-container"
            else "column"
        ),
        borderRadius=8 if "card" in lower_name else 4,
        border="1px solid #D7DEE8"
        if "card" in lower_name or preview_type == "summary-card"
        else None,
    )

    children = [_node_to_preview(child, theme=theme) for child in node.children]
    maturity: str = node.generation_status
    if preview_type == "unsupported-placeholder":
        maturity = "unsupported"

    return PreviewNode(
        id=node.id,
        name=node.name,
        type=preview_type,
        sourcePath=node.source.path,
        children=children,
        text=text,
        styles=styles,
        layout={
            "direction": node.layout.direction if node.layout else None,
            "gap": node.layout.gap if node.layout else None,
        },
        accessibility={"label": text or node.name},
        bindingSummary=None,
        maturity=maturity,
        expectedControl=node.control_type,
        diagnostics=[],
    )


def _theme_or(theme: dict[str, str], key: str, raw: Any) -> str | None:
    if isinstance(raw, str) and raw.startswith("#"):
        return raw
    token = theme.get(key)
    if token:
        return token
    if key == "surface":
        return "#F7F9FC"
    if key == "text":
        return "#1B2430"
    return None


def _severity(raw: Any) -> Literal["error", "warning", "info"]:
    if raw == "error":
        return "error"
    if raw == "info":
        return "info"
    return "warning"
