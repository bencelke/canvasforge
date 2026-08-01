"""Expand manifest sections into a normalized control tree."""

from __future__ import annotations

import re

from canvasforge.controls.builtins import (
    GENERATABLE_SECTION_TYPES,
    NON_GENERATABLE_SECTION_TYPES,
)
from canvasforge.errors import Diagnostic, GenerationError
from canvasforge.generate.naming import NameAllocator
from canvasforge.ir.ids import make_node_id
from canvasforge.ir.models import (
    AppIR,
    ControlNode,
    FormulaValue,
    LayoutValue,
    PropertyValue,
    ScreenIR,
    SourceReference,
)
from canvasforge.manifest.models import AppManifest, Screen, Section


def _hex_to_rgba_formula(hex_color: str) -> str:
    value = hex_color.strip().lstrip("#")
    if len(value) != 6:
        return "RGBA(0, 0, 0, 1)"
    red = int(value[0:2], 16)
    green = int(value[2:4], 16)
    blue = int(value[4:6], 16)
    return f"RGBA({red}, {green}, {blue}, 1)"


def _literal_text_formula(text: str) -> str:
    escaped = text.replace('"', '""')
    return f'="{escaped}"'


def _prop(name: str, value: str | int | float | bool, *, kind: str = "literal") -> PropertyValue:
    return PropertyValue(
        name=name,
        kind=kind,  # type: ignore[arg-type]
        value=value,
        evidence_status="documented",
    )


def _formula(name: str, expression: str) -> FormulaValue:
    return FormulaValue(name=name, expression=expression, evidence_status="documented")


def _pascal_from_key(key: str) -> str:
    trimmed = key
    for prefix in ("card", "sec", "hdr", "grid"):
        if trimmed.lower().startswith(prefix) and len(trimmed) > len(prefix):
            trimmed = trimmed[len(prefix) :]
            break
    parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])|\d+", trimmed)
    if not parts:
        return trimmed[:1].upper() + trimmed[1:]
    return "".join(part[:1].upper() + part[1:] for part in parts)


class SectionExpander:
    """Expand supported sections for a single screen into ControlNode trees."""

    def __init__(
        self,
        *,
        app_key: str,
        theme_tokens: dict[str, str],
        names: NameAllocator,
        allow_partial: bool = False,
    ) -> None:
        self.app_key = app_key
        self.theme_tokens = theme_tokens
        self.names = names
        self.allow_partial = allow_partial
        self.diagnostics: list[Diagnostic] = []
        self.omitted_sections: list[str] = []
        self.expanded_sections: list[str] = []

    def expand_screen(self, screen: Screen, screen_index: int) -> ScreenIR:
        source_path = f"$.screens.{screen_index}"
        screen_name = self.names.allocate(
            "Screen",
            screen.key,
            source_path=source_path,
            preferred=screen.key,
        )
        screen_id = make_node_id(self.app_key, screen.key, "screen")
        fill = self.theme_tokens.get("surface", "#FFFFFF")
        fill_expr = f"={_hex_to_rgba_formula(fill)}"

        root_name = self.names.allocate(
            "VerticalContainer",
            "ScreenRoot",
            source_path=f"{source_path}.sections",
            preferred="conScreenRoot",
        )

        pending_grid: ControlNode | None = None
        section_nodes: list[ControlNode] = []

        for section_index, section in enumerate(screen.sections):
            section_path = f"{source_path}.sections.{section_index}"
            if (
                section.type in NON_GENERATABLE_SECTION_TYPES
                or section.type not in GENERATABLE_SECTION_TYPES
            ):
                self._handle_unsupported(section, section_path)
                continue

            if section.type == "summary-card" and pending_grid is not None:
                card = self._expand_summary_card(screen.key, section, section_path)
                pending_grid.children.append(card)
                card.parent_id = pending_grid.id
                self.expanded_sections.append(section.key)
                continue

            if section.type == "summary-grid":
                pending_grid = self._expand_summary_grid(screen.key, section, section_path)
                section_nodes.append(pending_grid)
                self.expanded_sections.append(section.key)
                continue

            pending_grid = None
            node = self._expand_section(screen.key, section, section_path)
            if isinstance(node, ControlNode):
                section_nodes.append(node)
                self.expanded_sections.append(section.key)

        blocking = [d for d in self.diagnostics if d.severity == "error"]
        if blocking and not self.allow_partial:
            raise GenerationError(
                "Screen contains sections that cannot be generated",
                diagnostics=blocking,
            )

        root = ControlNode(
            id=make_node_id(self.app_key, screen.key, "root"),
            name=root_name,
            control_type="VerticalContainer",
            parent_id=screen_id,
            children=section_nodes,
            properties=[
                _prop("Width", "=Parent.Width", kind="formula"),
                _prop("Height", "=Parent.Height", kind="formula"),
                _prop("LayoutDirection", "Vertical"),
                _prop("LayoutGap", 16),
                _prop("PaddingTop", 24),
                _prop("PaddingRight", 24),
                _prop("PaddingBottom", 24),
                _prop("PaddingLeft", 24),
            ],
            formulas=[
                _formula("Width", "=Parent.Width"),
                _formula("Height", "=Parent.Height"),
            ],
            layout=LayoutValue(direction="vertical", gap=16, padding=(24, 24, 24, 24)),
            source=SourceReference(
                path=f"{source_path}.sections",
                app_key=self.app_key,
                screen_key=screen.key,
                role="screen-root",
            ),
        )
        for child in root.children:
            child.parent_id = root.id

        screen_node = ControlNode(
            id=screen_id,
            name=screen_name,
            control_type="Screen",
            parent_id=None,
            children=[root],
            properties=[_prop("Fill", fill_expr, kind="formula")],
            formulas=[_formula("Fill", fill_expr)],
            source=SourceReference(
                path=source_path,
                app_key=self.app_key,
                screen_key=screen.key,
                role="screen",
            ),
        )
        root.parent_id = screen_node.id

        return ScreenIR(
            key=screen.key,
            name=screen.name,
            title=screen.title,
            source_path=source_path,
            root=screen_node,
        )

    def _handle_unsupported(self, section: Section, path: str) -> None:
        self.omitted_sections.append(section.key)
        self.diagnostics.append(
            Diagnostic(
                code="SECTION_NOT_GENERATABLE",
                message=(
                    f"Section type '{section.type}' is recognized but not generatable in Phase 2"
                ),
                path=path,
                severity="error" if not self.allow_partial else "warning",
                hint=(
                    "Remove the section, use a reduced proof manifest, or pass "
                    "--allow-partial to omit explicitly"
                ),
                details={"sectionKey": section.key, "sectionType": section.type},
            )
        )

    def _expand_section(self, screen_key: str, section: Section, path: str) -> ControlNode | None:
        if section.type == "page-header":
            return self._expand_page_header(screen_key, section, path)
        if section.type == "empty-state":
            return self._expand_empty_state(screen_key, section, path)
        if section.type == "vertical-stack":
            return self._expand_stack(screen_key, section, path, direction="vertical")
        if section.type == "horizontal-stack":
            return self._expand_stack(screen_key, section, path, direction="horizontal")
        if section.type == "summary-card":
            return self._expand_summary_card(screen_key, section, path)
        if section.type == "summary-grid":
            return self._expand_summary_grid(screen_key, section, path)
        return None

    def _expand_page_header(self, screen_key: str, section: Section, path: str) -> ControlNode:
        name = self.names.allocate("Text", "PageTitle", source_path=path, preferred="lblPageTitle")
        title = section.title or "Untitled"
        text_color = self.theme_tokens.get("text", "#1B1B1B")
        color_expr = f"={_hex_to_rgba_formula(text_color)}"
        return ControlNode(
            id=make_node_id(self.app_key, screen_key, section.key, "title"),
            name=name,
            control_type="Text",
            properties=[
                _prop("Text", _literal_text_formula(title), kind="formula"),
                _prop("Size", 28),
                _prop("FontWeight", "Bold"),
                _prop("Color", color_expr, kind="formula"),
                _prop("Align", "Left"),
                _prop("Wrap", True),
                _prop("AccessibleLabel", title),
                _prop("Width", "=Parent.Width", kind="formula"),
            ],
            formulas=[
                _formula("Text", _literal_text_formula(title)),
                _formula("Color", color_expr),
                _formula("Width", "=Parent.Width"),
            ],
            source=SourceReference(
                path=path,
                app_key=self.app_key,
                screen_key=screen_key,
                section_key=section.key,
                role="page-title",
            ),
        )

    def _expand_summary_grid(self, screen_key: str, section: Section, path: str) -> ControlNode:
        name = self.names.allocate(
            "HorizontalContainer",
            "SummaryRow",
            source_path=path,
            preferred="conSummaryRow",
        )
        return ControlNode(
            id=make_node_id(self.app_key, screen_key, section.key, "grid"),
            name=name,
            control_type="HorizontalContainer",
            children=[],
            properties=[
                _prop("Width", "=Parent.Width", kind="formula"),
                _prop("LayoutDirection", "Horizontal"),
                _prop("LayoutGap", 12),
                _prop("FillPortions", 1),
            ],
            formulas=[_formula("Width", "=Parent.Width")],
            layout=LayoutValue(direction="horizontal", gap=12, fill_portions=1),
            source=SourceReference(
                path=path,
                app_key=self.app_key,
                screen_key=screen_key,
                section_key=section.key,
                role="summary-grid",
            ),
        )

    def _expand_summary_card(self, screen_key: str, section: Section, path: str) -> ControlNode:
        role = _pascal_from_key(section.key)
        preferred_card = f"conCard{role}"
        preferred_value = f"lblCard{role}Value"
        preferred_label = f"lblCard{role}Label"
        # Vertical-slice aliases for the Hello proof cards
        aliases = {
            "cardReady": ("conCardOpen", "lblCardOpenValue", "lblCardOpenLabel"),
            "cardPending": (
                "conCardCompleted",
                "lblCardCompletedValue",
                "lblCardCompletedLabel",
            ),
            "cardOpen": ("conCardOpen", "lblCardOpenValue", "lblCardOpenLabel"),
            "cardCompleted": (
                "conCardCompleted",
                "lblCardCompletedValue",
                "lblCardCompletedLabel",
            ),
        }
        if section.key in aliases:
            preferred_card, preferred_value, preferred_label = aliases[section.key]

        card_name = self.names.allocate(
            "VerticalContainer",
            f"Card{role}",
            source_path=path,
            preferred=preferred_card,
        )
        value_name = self.names.allocate(
            "Text",
            f"Card{role}Value",
            source_path=f"{path}.value",
            preferred=preferred_value,
        )
        label_name = self.names.allocate(
            "Text",
            f"Card{role}Label",
            source_path=f"{path}.label",
            preferred=preferred_label,
        )

        props = section.properties or {}
        value = str(props.get("value", "0"))
        title = section.title or role
        text_color = self.theme_tokens.get("text", "#1B1B1B")
        surface = self.theme_tokens.get("surface", "#FFFFFF")
        color_expr = f"={_hex_to_rgba_formula(text_color)}"
        fill_expr = f"={_hex_to_rgba_formula(surface)}"

        value_node = ControlNode(
            id=make_node_id(self.app_key, screen_key, section.key, "value-label"),
            name=value_name,
            control_type="Text",
            properties=[
                _prop("Text", _literal_text_formula(value), kind="formula"),
                _prop("Size", 24),
                _prop("FontWeight", "Semibold"),
                _prop("Color", color_expr, kind="formula"),
                _prop("AccessibleLabel", f"{title} value"),
            ],
            formulas=[
                _formula("Text", _literal_text_formula(value)),
                _formula("Color", color_expr),
            ],
            source=SourceReference(
                path=path,
                app_key=self.app_key,
                screen_key=screen_key,
                section_key=section.key,
                role="value-label",
            ),
        )
        label_node = ControlNode(
            id=make_node_id(self.app_key, screen_key, section.key, "title-label"),
            name=label_name,
            control_type="Text",
            properties=[
                _prop("Text", _literal_text_formula(title), kind="formula"),
                _prop("Size", 12),
                _prop("FontWeight", "Normal"),
                _prop("Color", color_expr, kind="formula"),
                _prop("AccessibleLabel", title),
            ],
            formulas=[
                _formula("Text", _literal_text_formula(title)),
                _formula("Color", color_expr),
            ],
            source=SourceReference(
                path=path,
                app_key=self.app_key,
                screen_key=screen_key,
                section_key=section.key,
                role="title-label",
            ),
        )
        card = ControlNode(
            id=make_node_id(self.app_key, screen_key, section.key, "card"),
            name=card_name,
            control_type="VerticalContainer",
            children=[value_node, label_node],
            properties=[
                _prop("LayoutDirection", "Vertical"),
                _prop("LayoutGap", 4),
                _prop("PaddingTop", 12),
                _prop("PaddingRight", 12),
                _prop("PaddingBottom", 12),
                _prop("PaddingLeft", 12),
                _prop("FillPortions", 1),
                _prop("Fill", fill_expr, kind="formula"),
            ],
            formulas=[_formula("Fill", fill_expr)],
            layout=LayoutValue(
                direction="vertical", gap=4, padding=(12, 12, 12, 12), fill_portions=1
            ),
            source=SourceReference(
                path=path,
                app_key=self.app_key,
                screen_key=screen_key,
                section_key=section.key,
                role="summary-card",
            ),
        )
        for child in card.children:
            child.parent_id = card.id
        return card

    def _expand_empty_state(self, screen_key: str, section: Section, path: str) -> ControlNode:
        con_name = self.names.allocate(
            "VerticalContainer",
            "EmptyState",
            source_path=path,
            preferred="conEmptyState",
        )
        title_name = self.names.allocate(
            "Text",
            "EmptyStateTitle",
            source_path=f"{path}.title",
            preferred="lblEmptyStateTitle",
        )
        body_name = self.names.allocate(
            "Text",
            "EmptyStateBody",
            source_path=f"{path}.body",
            preferred="lblEmptyStateBody",
        )
        btn_name = self.names.allocate(
            "Button",
            "EmptyStateAction",
            source_path=f"{path}.action",
            preferred="btnEmptyStateAction",
        )

        title = section.title or "Nothing here"
        props = section.properties or {}
        body = str(props.get("message", "No items to display."))
        action_label = str(props.get("actionLabel", "Get started"))
        text_color = self.theme_tokens.get("text", "#1B1B1B")
        color_expr = f"={_hex_to_rgba_formula(text_color)}"

        title_node = ControlNode(
            id=make_node_id(self.app_key, screen_key, section.key, "empty-title"),
            name=title_name,
            control_type="Text",
            properties=[
                _prop("Text", _literal_text_formula(title), kind="formula"),
                _prop("Size", 18),
                _prop("FontWeight", "Semibold"),
                _prop("Color", color_expr, kind="formula"),
                _prop("AccessibleLabel", title),
            ],
            formulas=[
                _formula("Text", _literal_text_formula(title)),
                _formula("Color", color_expr),
            ],
            source=SourceReference(
                path=path,
                app_key=self.app_key,
                screen_key=screen_key,
                section_key=section.key,
                role="empty-title",
            ),
        )
        body_node = ControlNode(
            id=make_node_id(self.app_key, screen_key, section.key, "empty-body"),
            name=body_name,
            control_type="Text",
            properties=[
                _prop("Text", _literal_text_formula(body), kind="formula"),
                _prop("Size", 14),
                _prop("Wrap", True),
                _prop("Color", color_expr, kind="formula"),
                _prop("AccessibleLabel", body),
            ],
            formulas=[
                _formula("Text", _literal_text_formula(body)),
                _formula("Color", color_expr),
            ],
            source=SourceReference(
                path=path,
                app_key=self.app_key,
                screen_key=screen_key,
                section_key=section.key,
                role="empty-body",
            ),
        )
        button_node = ControlNode(
            id=make_node_id(self.app_key, screen_key, section.key, "empty-action"),
            name=btn_name,
            control_type="Button",
            properties=[
                _prop("Text", _literal_text_formula(action_label), kind="formula"),
                _prop("AccessibleLabel", action_label),
                _prop("DisplayMode", "=DisplayMode.Edit", kind="formula"),
            ],
            formulas=[
                _formula("Text", _literal_text_formula(action_label)),
                _formula("DisplayMode", "=DisplayMode.Edit"),
            ],
            source=SourceReference(
                path=path,
                app_key=self.app_key,
                screen_key=screen_key,
                section_key=section.key,
                role="empty-action",
            ),
            notes="OnSelect omitted until Studio-exported evidence exists.",
        )
        container = ControlNode(
            id=make_node_id(self.app_key, screen_key, section.key, "empty-state"),
            name=con_name,
            control_type="VerticalContainer",
            children=[title_node, body_node, button_node],
            properties=[
                _prop("LayoutDirection", "Vertical"),
                _prop("LayoutGap", 8),
                _prop("Width", "=Parent.Width", kind="formula"),
            ],
            formulas=[_formula("Width", "=Parent.Width")],
            layout=LayoutValue(direction="vertical", gap=8),
            source=SourceReference(
                path=path,
                app_key=self.app_key,
                screen_key=screen_key,
                section_key=section.key,
                role="empty-state",
            ),
        )
        for child in container.children:
            child.parent_id = container.id
        return container

    def _expand_stack(
        self,
        screen_key: str,
        section: Section,
        path: str,
        *,
        direction: str,
    ) -> ControlNode:
        control_type = "VerticalContainer" if direction == "vertical" else "HorizontalContainer"
        name = self.names.allocate(control_type, section.key, source_path=path)
        children: list[ControlNode] = []
        for index, child in enumerate(section.children):
            child_path = f"{path}.children.{index}"
            if child.type in NON_GENERATABLE_SECTION_TYPES:
                self._handle_unsupported(child, child_path)
                continue
            if child.type not in GENERATABLE_SECTION_TYPES:
                self._handle_unsupported(child, child_path)
                continue
            node = self._expand_section(screen_key, child, child_path)
            if isinstance(node, ControlNode):
                children.append(node)
                self.expanded_sections.append(child.key)
        container = ControlNode(
            id=make_node_id(self.app_key, screen_key, section.key, "stack"),
            name=name,
            control_type=control_type,
            children=children,
            properties=[
                _prop(
                    "LayoutDirection",
                    "Vertical" if direction == "vertical" else "Horizontal",
                ),
                _prop("LayoutGap", 8),
                _prop("Width", "=Parent.Width", kind="formula"),
            ],
            formulas=[_formula("Width", "=Parent.Width")],
            layout=LayoutValue(
                direction="vertical" if direction == "vertical" else "horizontal",
                gap=8,
            ),
            source=SourceReference(
                path=path,
                app_key=self.app_key,
                screen_key=screen_key,
                section_key=section.key,
                role=f"{direction}-stack",
            ),
        )
        for child_node in container.children:
            child_node.parent_id = container.id
        return container


def build_app_ir(
    manifest: AppManifest,
    *,
    screen_keys: list[str] | None = None,
    allow_partial: bool = False,
) -> tuple[AppIR, list[Diagnostic], list[str], list[str]]:
    """Build AppIR from a validated manifest."""
    names = NameAllocator()
    theme_tokens = dict(manifest.theme.tokens) if manifest.theme else {}
    screens: list[ScreenIR] = []
    all_diagnostics: list[Diagnostic] = []
    expanded: list[str] = []
    omitted: list[str] = []

    selected = screen_keys or [manifest.app.start_screen]
    screens_by_key = {screen.key: (idx, screen) for idx, screen in enumerate(manifest.screens)}

    for key in selected:
        if key not in screens_by_key:
            raise GenerationError(
                f"Screen '{key}' not found in manifest",
                diagnostics=[
                    Diagnostic(
                        code="UNKNOWN_SCREEN",
                        message=f"Requested screen '{key}' does not exist",
                        path="$.screens",
                    )
                ],
            )
        index, screen = screens_by_key[key]
        expander = SectionExpander(
            app_key=manifest.app.key,
            theme_tokens=theme_tokens,
            names=names,
            allow_partial=allow_partial,
        )
        screen_ir = expander.expand_screen(screen, index)
        screens.append(screen_ir)
        all_diagnostics.extend(expander.diagnostics)
        expanded.extend(expander.expanded_sections)
        omitted.extend(expander.omitted_sections)

    ir = AppIR(
        app_key=manifest.app.key,
        app_name=manifest.app.name,
        app_version=manifest.app.version,
        manifest_version=manifest.app.manifest_version,
        screens=screens,
        theme_tokens=theme_tokens,
        metadata={
            "startScreen": manifest.app.start_screen,
            "layout": manifest.app.layout,
        },
    )
    return ir, all_diagnostics, expanded, omitted
