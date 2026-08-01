# Development Roadmap

## Phase 0 — Product definition (complete)

- Vision, non-goals, architecture
- Threat model and feasibility plan
- Repository scaffold and safety docs

## Phase 1 — Manifest foundation (complete)

- Manifest v0.1 schema and Pydantic models
- Loader + schema + semantic validation
- CLI: `version`, `doctor`, `validate`, `inspect`, `plan`
- Hello CanvasForge example
- O-Room requestor dashboard example (fictional data)
- Tests, Ruff, mypy, GitHub Actions CI

## Phase 2 — Verified control model and first generation proof (complete in tree; Candidate)

- Normalized AppIR / ControlNode tree
- Control + property allowlist with evidence statuses
- Section expansion for header/grid/card/empty/stacks
- Candidate Code View adapter
- CLI: `generate`, `controls`, `evidence`
- Snapshot tests + Studio round-trip documentation
- O-Room reduced proof manifest
- **No Studio-exported fixtures yet — all YAML remains Candidate**

## Phase 3 — Studio evidence and adapter hardening (next)

- Import real sanitized Studio-exported fixtures
- Promote properties/controls only via explicit evidence
- Tighten Code View serialization against fixtures
- Expand allowlist only after round-trip acceptance
- Still no `.msapp`, MCP, auth, or connected writes

## Phase 4 — Power Fx templates (proposed)

- Deterministic formula templates for navigation, filter, counts
- Formula validation and reference checking
- OnSelect only with Studio-exported evidence

## Phase 5 — Connected authoring (proposed, gated)

- Explicit opt-in connected mode
- Approval UX for writes
- Optional Microsoft Canvas authoring MCP / supported APIs
- Still no secret material in-repo

## Phase 6 — Packaging (only if supported)

- Evaluate verified Microsoft package/source workflows
- Never reverse-engineer unsupported binary formats
