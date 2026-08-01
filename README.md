# CanvasForge

**Local, manifest-driven compiler and validation tool for AI-assisted Microsoft Power Apps Canvas frontend generation.**

CanvasForge helps AI coding agents and developers describe administrative Canvas apps as structured manifests, validate them offline, and produce deterministic generation plans. Power Apps Studio remains the final rendering and validation authority.

> **Phase 1 status:** Offline foundation only. No Power Apps YAML generation, no `.msapp` packaging, no Microsoft connectivity, no authentication.

## Problem

Building responsive administrative Canvas apps in Studio is repetitive. Unconstrained AI improvisation risks unsupported controls, invalid formulas, and unsafe packaging. CanvasForge inserts a typed, reviewable manifest between intent and Studio.

## Architecture (text)

```
Natural-language prompt
  → CanvasForge manifest (YAML)
  → Schema validation
  → Semantic validation
  → Normalized internal representation
  → Generation plan
  → Power Apps target adapter (future)
  → Studio validation
  → Human polishing
```

## Current status

| Area | Status |
|------|--------|
| Manifest v0.1 models + JSON Schema | Done |
| CLI: version / doctor / validate / inspect / plan | Done |
| Hello + O-Room requestor dashboard examples | Done |
| Power Apps YAML / Code View output | Not started |
| Microsoft connected mode | Not started |
| MCP / editor extensions / React preview | Out of scope for now |

**O-Room Actions** is the first reference implementation and lives under `examples/oroom-actions/`. It is not the product core.

**CanvasForge does not connect to military or production systems in its current phase.**

## Installation (uv)

Requires Python 3.12+.

```bash
# From the repository root
uv sync --all-extras --dev
uv run canvasforge doctor
```

## Quick start

```bash
uv run canvasforge validate examples/hello-canvasforge/app.yaml
uv run canvasforge inspect examples/hello-canvasforge/app.yaml
uv run canvasforge plan examples/hello-canvasforge/app.yaml

uv run canvasforge validate examples/oroom-actions/app.yaml
```

## CLI examples

```bash
uv run canvasforge version
uv run canvasforge doctor
uv run canvasforge validate path/to/app.yaml
uv run canvasforge inspect path/to/app.yaml
uv run canvasforge plan path/to/app.yaml
```

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

- Offline by default; no Microsoft service calls in Phase 1
- Safe YAML loading only; no `eval`, no remote includes, no URL imports
- No passwords, CAC PINs, certificates, cookies, or tokens
- Fictional examples only; no government/operational data in-repo
- Generated Canvas output (future) must be validated in Power Apps Studio

See [SECURITY.md](SECURITY.md) and [docs/threat-model.md](docs/threat-model.md).

## Development

```bash
uv sync --all-extras --dev
uv run pytest
uv run ruff check .
uv run ruff format .
uv run mypy src tests
```

## Roadmap

1. Phase 1 (now): manifest validation + planning
2. Phase 2+: Studio-verified control allowlists and Code View adapters
3. Later: optional connected authoring with explicit human approval
4. Only if supported: verified package/source workflows

Details: [docs/development-roadmap.md](docs/development-roadmap.md)

## Disclaimer

Generated Canvas artifacts must be reviewed and validated in **Microsoft Power Apps Studio**. CanvasForge does not replace Studio, does not publish apps, and does not guarantee support for every Canvas control.

## License

MIT — see [LICENSE](LICENSE).
