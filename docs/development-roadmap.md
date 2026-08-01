# Development Roadmap

CanvasForge is an offline-first App Factory. Connected Microsoft tooling is optional and deferred. Code View Deployment Kits are the primary near-term deployment path; `.msapp` is experimental.

See also: [offline-app-factory.md](offline-app-factory.md).

---

## Completed foundation

### Phase 0 — Product definition (complete)

- Vision, non-goals, architecture, threat model
- Repository scaffold and safety docs

### Phase 1 — Manifest foundation (complete)

- Manifest v0.1 schema and Pydantic models
- Loader + schema + semantic validation
- CLI: `version`, `doctor`, `validate`, `inspect`, `plan`
- Hello CanvasForge + O-Room example manifests
- Tests, Ruff, mypy, GitHub Actions CI

### Phase 2 — Verified control model and first generation proof (complete)

- Normalized AppIR / ControlNode tree
- Control + property allowlist with evidence statuses
- Section expansion for header/grid/card/empty/stacks
- Candidate Code View adapter
- CLI: `generate`, `controls`, `evidence`
- Snapshot tests + Studio round-trip documentation
- O-Room reduced proof manifest
- **No Studio-exported fixtures yet — YAML remains Candidate**

---

## Phase 3A — PC migration and offline architecture pivot (current)

### Goals

- Run the Phase 2 baseline cleanly on Windows
- Document the offline App Factory, Deployment Kit, local preview, Runner, experimental `.msapp`, and O-Room reference strategy
- Restructure phases around tenant-neutral local development
- Preserve compiler behavior; no GUI or kit builder yet

### Non-goals

- Implementing Deployment Kit packaging code
- Implementing React preview
- Adding Microsoft authentication or APIs
- Weakening lint, types, or tests

### Deliverables

- Windows development environment verified
- Architecture docs listed in [offline-app-factory.md](offline-app-factory.md)
- [windows-migration-report.md](windows-migration-report.md)
- Updated README and roadmap

### Dependencies

- Phase 2 baseline commit available on `main`

### Risks

- Line-ending / autocrlf checksum drift on Windows
- Python 3.12 not on system PATH (uv-managed interpreters)

### Acceptance criteria

- Repo clones on Windows; origin and `main` correct
- `pytest`, Ruff, mypy, and CLI examples pass
- Offline architecture docs exist
- No commit/push required for completion; no Microsoft connection added

---

## Phase 3B — Portable Deployment Kit specification and builder (complete)

### Goals

- Finalize `.cforge.zip` schema 0.1 and builder CLI
- Emit Code View kits with checksums, reports, and maker checklists

### Deliverables

- `canvasforge package` / `inspect` / `verify`
- `schemas/deployment-kit.schema.json`
- Forbidden-content scanner and deterministic ZIP
- Docs: format, security, versioning, maker handoff

### Acceptance

- Hello + O-Room proof kits build and verify
- Byte-identical ZIPs for identical inputs
- Mock records excluded by default
- No Microsoft auth/GUI/Runner/`.msapp`

---

## Phase 4 — Local graphical preview ✅

### Goals

- React + TypeScript + Vite advisory preview over the Python engine
- Same manifest/IR as Code View generation
- Persistent Studio-validation disclaimer

### Non-goals

- Runtime parity with Power Apps
- Cloud-hosted preview
- Auth
- Manifest mutation / AI prompting

### Deliverables

- `canvasforge studio` CLI (loopback FastAPI + built UI)
- Preview Model adapter from AppIR (`src/canvasforge/studio/`)
- React Studio shell (`studio/`) with screen tree, inspector, diagnostics, Build Kit
- Desktop / tablet / mobile advisory widths
- Docs: studio-architecture, preview-rendering-model, studio-security, studio-user-guide

### Dependencies

- Stable IR and generation reports
- Phase 3B Deployment Kit builder

### Risks

- Divergent preview models; UI scope creep

### Acceptance criteria

- Preview renders Hello + O-Room proof from IR
- Disclaimer always visible
- No Microsoft network calls
- Build Kit from GUI verifies via existing Python engine

---

## Phase 5 — Prompt-driven manifest editing and change planning

### Goals

- Structured prompt → manifest patch proposals
- Deterministic change plans and diffs before apply

### Non-goals

- Autonomous tenant writes
- Unreviewed silent manifest mutation in CI

### Deliverables

- Prompt/patch IR
- Plan + diff UX (CLI and/or preview prompt panel)
- Safety rules for AI-assisted edits

### Dependencies

- Phase 4 preview helpful but not strictly required for CLI-first

### Risks

- Unconstrained AI output bypassing schema

### Acceptance criteria

- Patches validate before apply
- Plans are deterministic and reviewable

---

## Phase 6 — Expanded Canvas control and Power Fx generation

### Goals

- Grow allowlisted controls/properties with evidence
- Deterministic Power Fx templates (nav, filter, counts, etc.)

### Non-goals

- Inventing unsupported formulas
- OnSelect without evidence policy compliance

### Deliverables

- Expanded registry + tests
- Formula template library
- Docs updates for Power Fx strategy

### Dependencies

- Evidence model; Studio Compatibility Laboratory inputs when available

### Risks

- Premature “inferred” evidence promotions

### Acceptance criteria

- New controls gated by evidence status
- Snapshots and diagnostics remain strict

---

## Phase 7 — O-Room reference implementation

### Goals

- Generate the ten O-Room frontend surfaces listed in [oroom-reference-strategy.md](oroom-reference-strategy.md)
- Drive reusable platform features from reference gaps

### Non-goals

- Hard-coding O-Room domain into core packages
- Real operational data

### Deliverables

- Expanded `examples/oroom-actions/` manifests
- Kits for reference builds
- Gap → feature tracking notes

### Dependencies

- Phases 3B, 6 (and ideally 4)

### Risks

- One-off reference hacks

### Acceptance criteria

- Each surface has a manifest path and Candidate output or explicit deferred gap
- Fictional data only

---

## Phase 8 — Offline work-side CanvasForge Runner

### Goals

- Windows offline app to open `.cforge.zip`, verify checksums, guide makers

### Non-goals

- AI, internet, CAC, publishing, auto data connect

### Deliverables

- Runner application
- Checksum verification UX
- Sanitized validation result capture

### Dependencies

- Phase 3B kits

### Risks

- Scope creep into ALM/publishing

### Acceptance criteria

- Opens Hello kit offline
- Rejects tampered checksums
- No credential storage

---

## Phase 9 — Experimental `.msapp` generation

### Goals

- Evaluate Microsoft-supported pack/unpack only after gates in [msapp-experimental-roadmap.md](msapp-experimental-roadmap.md)

### Non-goals

- Defaulting kits to `.msapp`
- Undocumented binary fabrication

### Deliverables

- Experimental adapter behind explicit flags
- Studio acceptance evidence requirements

### Dependencies

- Known-good starter app + supported toolchain

### Risks

- Format fragility; public-repo leakage of tenant packages

### Acceptance criteria

- Experimental labeling everywhere
- Reproducible pack/unpack documented
- `.msapp` remains gitignored by default

---

## Phase 10 — Studio compatibility laboratory

### Goals

- Reclassify and continue Phase 3-style evidence / fixture work as a **Studio Compatibility Laboratory**
- Import sanitized Studio-exported fixtures; promote controls/properties only via evidence
- Tighten Code View serialization against fixtures

### Non-goals

- Requiring live tenant access from the public engineering repo
- Committing unsanitized exports

### Deliverables

- Fixture import workflow (existing evidence commands + docs)
- Promotion records
- Round-trip acceptance notes

### Dependencies

- Access to sanitized exports via approved channels
- Preserve any prior Phase 3 evidence work if/when it lands on a branch

### Risks

- Fixture staleness across Studio versions

### Acceptance criteria

- Documented evidence statuses for promoted items
- No secrets in fixtures

**Note:** Do not remove Phase 3 evidence/compatibility work if it exists locally or arrives later via branch — fold it into this laboratory track.

---

## Phase 11 — Reusable administrative app templates

### Goals

- Template packs for common admin app shells (dashboard, request/approve, workspace, admin config)

### Non-goals

- Marketplace SaaS hosting in-tree
- Tenant-specific templates with real data

### Deliverables

- Template manifests + kit recipes
- Docs for composing templates

### Dependencies

- Phases 6–7 patterns proven

### Risks

- Template sprawl without tests

### Acceptance criteria

- At least two templates build deterministic kits
- Fully fictional samples

---

## Deferred / optional

### Connected Microsoft adapter (optional)

See [connected-mode-roadmap.md](connected-mode-roadmap.md). Explicit opt-in only; never core architecture. Not scheduled ahead of kits, preview, and laboratory hardening.
