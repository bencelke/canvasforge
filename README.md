# CanvasForge

**Local AI-assisted, manifest-driven frontend compiler and visual app builder for Microsoft Power Apps Canvas applications.**

CanvasForge generates **tenant-neutral** frontend structures, Power Fx candidates, local previews, and portable **Deployment Kits**. An authorized maker later pastes or imports into Power Apps Studio and connects SharePoint Lists and Power Automate.

It must remain useful **without** AVD, Power Apps login, military tenant access, Microsoft authentication, Environment Maker rights, or direct Microsoft API access.

> **Current baseline:** Phase 3B Deployment Kit builder (``.cforge.zip``). Candidate Code View YAML — **Studio-unvalidated**. No GUI preview yet, no `.msapp` packaging, no Microsoft connectivity, no authentication.

**Public repository warning:** Assume anything committed is world-readable. Never commit secrets, tenant identifiers, credentials, CAC material, real operational data, or unsanitized Studio exports.

## Problem

Building responsive administrative Canvas apps in Studio is repetitive. Unconstrained AI improvisation risks unsupported controls, invalid formulas, and unsafe packaging. CanvasForge inserts a typed, reviewable manifest between intent and Studio, then packages portable frontend artifacts for approved transfer.

## Architecture (text)

```
Natural-language prompt or Cursor instruction
  → CanvasForge manifest (YAML)
  → Schema + semantic validation
  → Normalized IR (AppIR)
  → Local visual preview (advisory; future)
  → Candidate Code View output
  → Portable Deployment Kit (.cforge.zip; future)
  → Approved transfer → maker paste/import in Studio
  → Connect SharePoint / Automate → Studio validate & publish
```

Power Apps Studio remains the final rendering and validation authority. Local preview must never be claimed as an exact Power Apps runtime.

## Current status

| Area | Status |
|------|--------|
| Manifest v0.1 models + JSON Schema | Done |
| CLI: version / doctor / validate / inspect / plan | Done |
| CLI: generate / controls / evidence | Done (Phase 2) |
| Control allowlist + evidence model | Done (documented bootstrap) |
| Hello Candidate Code View generation | Done (Studio-unvalidated) |
| O-Room reduced proof manifest | Done |
| Offline App Factory architecture docs | Done (Phase 3A) |
| Deployment Kit builder (`.cforge.zip`) | Done (Phase 3B) |
| Local graphical preview | Not started (Phase 4) |
| Work-side Runner | Not started (Phase 8) |
| Experimental `.msapp` | Deferred (Phase 9) |
| Studio Compatibility Laboratory | Planned (Phase 10; preserve prior evidence work) |
| Microsoft connected mode | Optional future adapter — not core |

**O-Room Actions** is the first reference implementation (`examples/oroom-actions/`). It is not the product core.

**CanvasForge does not connect to military or production systems.**

## Installation (uv)

Requires Python 3.12+. On Windows, `uv` can install CPython 3.12 if the system interpreter is older:

```bash
uv python install 3.12
uv sync --all-extras --dev
uv run canvasforge doctor
```

## Quick start

```bash
uv run canvasforge validate examples/hello-canvasforge/app.yaml
uv run canvasforge inspect examples/hello-canvasforge/app.yaml
uv run canvasforge plan examples/hello-canvasforge/app.yaml
uv run canvasforge generate examples/hello-canvasforge/app.yaml --target code-view
uv run canvasforge controls
uv run canvasforge evidence list

uv run canvasforge validate examples/oroom-actions/app.yaml
uv run canvasforge validate examples/oroom-actions/dashboard-proof.yaml
uv run canvasforge generate examples/oroom-actions/dashboard-proof.yaml --target code-view

uv run canvasforge package examples/hello-canvasforge/app.yaml --output dist/Hello-CanvasForge.cforge.zip
uv run canvasforge package examples/oroom-actions/dashboard-proof.yaml --output dist/O-Room-Dashboard-Proof.cforge.zip
uv run canvasforge package verify dist/Hello-CanvasForge.cforge.zip
uv run canvasforge package inspect dist/Hello-CanvasForge.cforge.zip
```

## Deployment Kits (`.cforge.zip`)

A **CanvasForge Deployment Kit** is a portable, tenant-neutral ZIP for approved handoff to an authorized Power Apps maker.

**It is:** Candidate Code View blocks, manifests, mock schema, maker checklists, checksums, and compatibility reports.

**It is not:** a `.msapp`, a Power Platform solution, an executable, an auth package, or a production-data package.

```bash
uv run canvasforge package path/to/app.yaml --output dist/MyApp.cforge.zip
uv run canvasforge package inspect dist/MyApp.cforge.zip
uv run canvasforge package verify dist/MyApp.cforge.zip
```

Work-side handoff: [docs/maker-handoff.md](docs/maker-handoff.md).
Format and security: [docs/deployment-kit-format.md](docs/deployment-kit-format.md), [docs/deployment-kit-security.md](docs/deployment-kit-security.md).

**Warnings:** Do not commit generated kits. Never include production data or credentials. Output remains Candidate until Studio-validated.

## CLI examples

```bash
uv run canvasforge version
uv run canvasforge doctor
uv run canvasforge validate path/to/app.yaml
uv run canvasforge inspect path/to/app.yaml
uv run canvasforge plan path/to/app.yaml
uv run canvasforge generate path/to/app.yaml --target code-view
uv run canvasforge generate path/to/app.yaml --dry-run
uv run canvasforge generate path/to/app.yaml --allow-partial
uv run canvasforge controls
uv run canvasforge controls --json
uv run canvasforge evidence list
```

### Candidate output disclaimer

Generated Code View YAML under `generated/` is a **Studio-unvalidated Candidate**. Do not edit generated files. Do not treat them as production source. Follow [docs/studio-round-trip.md](docs/studio-round-trip.md) before trusting any paste into Studio.

## Example manifest excerpt

```yaml
app:
  key: helloCanvasForge
  name: Hello CanvasForge
  version: 0.1.0
  manifestVersion: "0.1"
  startScreen: scrDashboard

screens:
  - key: scrDashboard
    name: Dashboard
    sections:
      - key: hdrDashboard
        type: page-header
        title: Welcome to CanvasForge
      - key: cardReady
        type: summary-card
        title: Ready Screens
```

## Safety model

- Offline by default; no Microsoft service calls in current phases
- Safe YAML loading only; no `eval`, no remote includes, no URL imports
- No passwords, CAC PINs, certificates, cookies, or tokens
- Fictional examples only; no government/operational data in-repo
- Generated Canvas output must be validated in Power Apps Studio
- Deployment Kits must not embed tenant connections or credentials

See [SECURITY.md](SECURITY.md) and [docs/threat-model.md](docs/threat-model.md).

## Documentation map

| Doc | Topic |
|-----|-------|
| [docs/offline-app-factory.md](docs/offline-app-factory.md) | Product definition / Studio responsibilities |
| [docs/deployment-kit-format.md](docs/deployment-kit-format.md) | `.cforge.zip` layout and checksums |
| [docs/deployment-kit-security.md](docs/deployment-kit-security.md) | Forbidden-content scan and archive limits |
| [docs/maker-handoff.md](docs/maker-handoff.md) | Work-side handoff concept |
| [docs/deployment-kit-architecture.md](docs/deployment-kit-architecture.md) | Kit architecture |
| [docs/local-preview-architecture.md](docs/local-preview-architecture.md) | Future React preview |
| [docs/work-side-runner.md](docs/work-side-runner.md) | Offline work-side Runner |
| [docs/msapp-experimental-roadmap.md](docs/msapp-experimental-roadmap.md) | Deferred `.msapp` gates |
| [docs/oroom-reference-strategy.md](docs/oroom-reference-strategy.md) | O-Room reference approach |
| [docs/development-roadmap.md](docs/development-roadmap.md) | Phases 3A–11 |
| [docs/architecture.md](docs/architecture.md) | Compiler + product surfaces |
| [docs/windows-migration-report.md](docs/windows-migration-report.md) | Windows Phase 3A report |

## Development

```bash
uv sync --all-extras --dev
uv run pytest
uv run ruff check .
uv run ruff format .
uv run mypy src tests
```

## Roadmap (summary)

| Phase | Focus |
|-------|--------|
| 1–2 | Manifest + Candidate Code View (done) |
| 3A | Windows migration + offline architecture pivot (done) |
| 3B | Deployment Kit builder (done) |
| 4 | Local graphical preview |
| 5 | Prompt-driven manifest editing |
| 6 | Expanded controls + Power Fx |
| 7 | O-Room reference implementation |
| 8 | Work-side Runner |
| 9 | Experimental `.msapp` |
| 10 | Studio Compatibility Laboratory |
| 11 | Reusable admin templates |

Details: [docs/development-roadmap.md](docs/development-roadmap.md)

## Disclaimer

Generated Canvas artifacts must be reviewed and validated in **Microsoft Power Apps Studio**. CanvasForge does not replace Studio, does not publish apps, and does not guarantee support for every Canvas control. Local preview is advisory only.

## License

MIT — see [LICENSE](LICENSE).
