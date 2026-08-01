# Architecture

CanvasForge is a local Python CLI that loads an application manifest, validates it, expands a normalized control tree, and emits Candidate Code View artifacts for manual Studio validation.

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
Normalized internal representation (AppIR)
        │
        ▼
Control tree expansion + generation plan
        │
        ▼
Power Apps target adapter (Code View — Candidate)
        │
        ▼
Studio validation (human + Studio)
        │
        ▼
Human polishing / data connection
```

## Phase 2 components

| Component | Responsibility |
|-----------|----------------|
| `manifest.*` | Safe load + schema + semantic validation |
| `ir.*` | Normalized AppIR / ControlNode models |
| `controls.*` | Allowlist registry + evidence policy |
| `generate.*` | Section expansion, naming, pipeline, reports |
| `adapters.code_view` | Candidate Code View YAML adapter |
| `evidence.*` | Offline evidence list/import helpers |
| `planner` | High-level Phase 1 planning output |
| `diagnostics.doctor` | Offline environment health checks |
| `cli` | Typer entrypoints |

## Package layout

```
src/canvasforge/
  cli.py
  errors.py
  manifest/
  ir/
  controls/
  generate/
  adapters/code_view/
  evidence/
  planner/
  diagnostics/
```

## Target adapters

1. **Code View YAML** — Candidate paste blocks (Phase 2)
2. **Microsoft Canvas authoring MCP** — if available and supported (later)
3. **Verified source/package workflow** — only with a validated Microsoft path
4. **Documentation-only fallback** — human checklist when automation is unsafe

Adapters must never invent unsupported controls, properties, formulas, or packaging formats.

## Determinism

Given the same manifest content:

- Validation results are stable.
- Plan step ordering is stable.
- Candidate YAML and control trees are byte-stable for snapshot tests (build IDs exclude wall-clock time).

## Separation of concerns

- **Generic design** lives in the manifest.
- **Tenant-specific data** remains out of Phase 2.
- **Reference apps** (e.g., O-Room Actions) live under `examples/`, not core packages.

## Offline boundary

Phase 2 makes **no network calls**. Doctor checks do not probe Microsoft services. Connected mode remains disabled.
