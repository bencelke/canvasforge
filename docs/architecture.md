# Architecture

CanvasForge is an **offline-first App Factory**: a local, manifest-driven compiler and (future) visual builder for tenant-neutral Microsoft Power Apps Canvas frontends.

It does not require AVD, Power Apps login, Microsoft authentication, or tenant API access. Power Apps Studio remains the final compatibility and rendering authority. Local preview is advisory only.

```
Natural-language prompt or Cursor instruction
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
        ├──► Local visual preview (advisory; future)
        │
        ▼
Control tree expansion + generation plan
        │
        ▼
Power Apps target adapter (Code View — Candidate)
        │
        ▼
Portable Deployment Kit (.cforge.zip; future builder)
        │
        ▼
Approved transfer → work-side Runner (future) / maker paste
        │
        ▼
Studio validation + data/Automate wiring (human)
```

## Product surfaces

| Surface | Role |
|---------|------|
| **CanvasForge Studio** | Home/local authoring: CLI today; preview + kits later |
| **Compiler core** | Manifest → IR → adapters → reports (Python) |
| **Deployment Kit** | Portable `.cforge.zip` for Code View–first transfer |
| **CanvasForge Runner** | Offline work-side kit inspector (AI-free; future) |
| **Studio Compatibility Laboratory** | Fixture-backed evidence and round-trip hardening |
| **Connected adapter** | Optional future; not core |

Details: [offline-app-factory.md](offline-app-factory.md), [deployment-kit-architecture.md](deployment-kit-architecture.md), [local-preview-architecture.md](local-preview-architecture.md), [work-side-runner.md](work-side-runner.md).

## Phase 2 components (preserved)

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

1. **Code View YAML** — Candidate paste blocks (primary; Phase 2 done)
2. **Deployment Kit packager** — `.cforge.zip` (Phase 3B)
3. **Experimental `.msapp`** — only with supported toolchain (Phase 9)
4. **Microsoft Canvas authoring MCP / APIs** — optional connected adapter (later)
5. **Documentation-only fallback** — human checklist when automation is unsafe

Adapters must never invent unsupported controls, properties, formulas, or packaging formats.

## Determinism

Given the same manifest content:

- Validation results are stable.
- Plan step ordering is stable.
- Candidate YAML and control trees are byte-stable for snapshot tests (build IDs exclude wall-clock time).
- Manifest checksums normalize newlines to LF so Windows CRLF checkouts do not change build IDs.

## Separation of concerns

- **Generic design** lives in the manifest.
- **Tenant-specific data** stays out of CanvasForge outputs.
- **Reference apps** (e.g., O-Room Actions) live under `examples/`, not core packages.
- **Mock schemas** guide makers; they are not production connectors.

## Offline boundary

The product makes **no Microsoft service calls** in current phases. Doctor checks do not probe Microsoft services. Connected mode remains disabled. See [offline-mode.md](offline-mode.md) and [connected-mode-roadmap.md](connected-mode-roadmap.md).

## Security boundary (public repository)

Never commit credentials, tenant IDs, environment IDs, internal URLs, CAC material, real operational data, `.msapp` binaries, or Deployment Kits containing sensitive content. See [SECURITY.md](../SECURITY.md) and [threat-model.md](threat-model.md).
