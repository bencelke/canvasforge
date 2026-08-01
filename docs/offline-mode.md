# Offline Mode

## Default posture

CanvasForge Phase 1 runs in **offline mode only**.

Offline mode means:

- No network calls from the CLI
- No Microsoft service health checks
- No authentication flows
- No remote manifest fetches
- No telemetry

## What works offline

- Loading local YAML manifests
- JSON Schema validation
- Semantic validation
- `inspect` summaries
- Deterministic `plan` output
- `doctor` local environment checks
- Unit tests and local CI jobs (CI runners may download dependencies, but the product itself does not call Microsoft APIs)

## Doctor checks (offline)

`canvasforge doctor` verifies:

- Python version
- Package import/installation
- Working directory
- Presence of example manifests
- Offline mode status

It does **not** check Power Platform, SharePoint, Dataverse, or Microsoft Graph.

## Local artifacts

Inspectable outputs belong under `generated/` (gitignored except `.gitkeep`). Manifests and plans should remain readable plain text for review and diffing.

## Transition to connected mode

Connected features are out of scope until a later phase publishes an explicit opt-in model. See [connected-mode-roadmap.md](connected-mode-roadmap.md).
