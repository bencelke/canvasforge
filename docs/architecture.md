# Architecture

## Overview

CanvasForge is a local Python CLI that loads an application manifest, validates it, and produces deterministic planning output. Later phases introduce target adapters for Power Apps authoring surfaces.

```
Natural-language prompt
        │
        ▼
CanvasForge manifest (YAML)
        │
        ▼
Schema validation (JSON Schema)
        │
        ▼
Semantic validation (typed rules)
        │
        ▼
Normalized internal representation (Pydantic)
        │
        ▼
Generation plan (deterministic)
        │
        ▼
Power Apps target adapter  ←── not implemented in Phase 1
        │
        ▼
Studio validation (human + Studio)
        │
        ▼
Human polishing / data connection
```

## Phase 1 components

| Component | Responsibility |
|-----------|----------------|
| `manifest.loader` | Safe YAML load with size/nesting limits |
| `manifest.schema` | JSON Schema validation |
| `manifest.models` | Pydantic v2 typed models |
| `manifest.validator` | Semantic uniqueness and reference checks |
| `planner` | Deterministic high-level generation plan |
| `diagnostics.doctor` | Offline environment health checks |
| `cli` | Typer entrypoints |

## Package layout

```
src/canvasforge/
  cli.py                 # Typer application
  errors.py              # Structured error types
  manifest/
    models.py            # AppManifest and section discriminators
    loader.py            # Safe YAML loading
    schema.py            # JSON Schema access/validation
    validator.py         # Semantic validation
  planner/
    models.py            # Plan step models + planner
  diagnostics/
    doctor.py            # Offline doctor checks
```

## Future target adapters (not implemented)

1. **Code View YAML** — paste-ready Studio blocks
2. **Microsoft Canvas authoring MCP** — if available and supported
3. **Verified source/package workflow** — only with a validated Microsoft path
4. **Documentation-only fallback** — human checklist when automation is unsafe

Adapters must never invent unsupported controls, properties, formulas, or packaging formats.

## Determinism

Given the same manifest content:

- Validation results are stable.
- Plan step ordering is stable.
- Future generation output must be diffable and reproducible.

## Separation of concerns

- **Generic design** lives in the manifest (screens, sections, navigation, theme).
- **Tenant-specific data** (connectors, SharePoint lists, environments) is out of Phase 1 and must remain separable later.
- **Reference apps** (e.g., O-Room Actions) live under `examples/`, not core packages.

## Offline boundary

Phase 1 makes **no network calls**. Doctor checks do not probe Microsoft services. Connected mode is documented separately and disabled by default.
