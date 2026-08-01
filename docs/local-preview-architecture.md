# Local Preview Architecture

## Purpose

The local graphical preview is an **advisory** visual shell for CanvasForge Studio. It helps makers and AI-assisted workflows inspect layouts, screens, validation, and build diffs **without** claiming Power Apps runtime fidelity.

**Required on-screen disclaimer (always visible in preview chrome):**

> Local Preview — Power Apps Studio validation required

## Technology plan

| Layer | Choice |
|-------|--------|
| UI | React + TypeScript |
| Bundler / dev server | Vite |
| Engine | Existing Python CanvasForge package |
| Bridge | Local-only API or process bridge (HTTP localhost or stdio); no cloud |

The preview consumes the **same manifest and normalized AppIR** as the Canvas Code View generator. Divergent preview models are forbidden.

## Non-goals for preview

- Exact Power Apps rendering or formula evaluation parity
- Microsoft authentication
- Tenant data access
- Publishing or sharing apps
- Replacing Studio acceptance testing

## Planned UI surfaces

| Surface | Role |
|---------|------|
| Prompt panel | Capture NL / Cursor-oriented instructions (Phase 5) |
| Project browser | Local projects and manifests |
| Screen tree | Screens, sections, controls from IR |
| Visual canvas | Layout approximation from IR |
| Properties panel | Selected control properties (allowlisted) |
| Device modes | Desktop / tablet / mobile breakpoints from manifest |
| Validation panel | Schema + semantic diagnostics |
| Build diff | Compare generation reports / IR trees |
| Deployment Kit action | Trigger kit packaging (Phase 3B+) |

## Data flow

```
Manifest YAML
    │
    ├──────────────────────┐
    ▼                      ▼
Python validation      Python IR expand
    │                      │
    ▼                      ▼
Diagnostics            AppIR (+ generation plan)
    │                      │
    └──────────┬───────────┘
               ▼
     Local preview process bridge
               │
               ▼
         React preview UI
```

Candidate Code View emission and Deployment Kit packaging remain Python-side responsibilities; the UI orchestrates them.

## Mock data

Preview uses fictional mock records derived from `mock-schema/` or example fixtures. Never load real operational data into the preview.

## Implementation phase

Local graphical preview is **Phase 4**. Phase 3A documents the architecture only — no React app, Vite project, or GUI code is added yet.

## Related documents

- [offline-app-factory.md](offline-app-factory.md)
- [internal-representation.md](internal-representation.md)
- [deployment-kit-architecture.md](deployment-kit-architecture.md)
- [development-roadmap.md](development-roadmap.md)
