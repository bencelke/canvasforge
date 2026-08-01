# Development Roadmap

## Phase 0 — Product definition (complete in this foundation)

- Vision, non-goals, architecture
- Threat model and feasibility plan
- Repository scaffold and safety docs

## Phase 1 — Manifest foundation (this release)

- Manifest v0.1 schema and Pydantic models
- Loader + schema + semantic validation
- CLI: `version`, `doctor`, `validate`, `inspect`, `plan`
- Hello CanvasForge example
- O-Room requestor dashboard example (fictional data)
- Tests, Ruff, mypy, GitHub Actions CI

## Phase 2 — Generation planning depth

- Richer plan metadata (control hints, layout recipes)
- Snapshot tests for plans
- Expanded section properties with strict validation
- Begin Studio-verified control allowlist documentation

## Phase 3 — Code View adapter (proposed)

- Emit paste-ready YAML/blocks for allowlisted controls only
- Fail closed on unsupported constructs
- Human review checklist output
- Round-trip evidence in docs (no fabricated `.msapp`)

## Phase 4 — Power Fx templates (proposed)

- Deterministic formula templates for navigation, filter, counts
- Formula validation and reference checking

## Phase 5 — Connected authoring (proposed, gated)

- Explicit opt-in connected mode
- Approval UX for writes
- Optional Microsoft Canvas authoring MCP / supported APIs
- Still no secret material in-repo

## Phase 6 — Packaging (only if supported)

- Evaluate verified Microsoft package/source workflows
- Never reverse-engineer unsupported binary formats

## Parallel non-goals until gated

- MCP server productization
- VS Code / Cursor extension
- React preview app
- Live SharePoint / Automate provisioning
