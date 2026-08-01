# Contributing to CanvasForge

Thank you for helping build CanvasForge. This project is early (Phase 0/1) and intentionally constrained.

## Safety first

This repository is **public**. Do not contribute:

- Secrets, tokens, passwords, CAC PINs, certificates, or cookies
- Tenant IDs, internal URLs, or production connector configuration
- Government, military, or operational data
- Real names, EDIPI, UICs, or military email addresses
- Exported `.msapp` packages or internal screenshots

Use fictional data only. See [SECURITY.md](SECURITY.md).

## Development setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --all-extras --dev
uv run pre-commit install
uv run canvasforge doctor
uv run pytest
uv run ruff check .
uv run mypy src tests
```

## Scope for Phase 1

In scope:

- Manifest models and validation
- CLI (`version`, `doctor`, `validate`, `inspect`, `plan`)
- Documentation and examples
- Tests and CI

Out of scope until a later phase:

- Power Apps YAML / Code View generation
- `.msapp` packaging
- Microsoft Graph / Power Platform connectivity
- MCP servers
- VS Code / Cursor extensions
- React preview apps

Do not hard-code O-Room terminology into `src/canvasforge`. Reference apps live under `examples/`.

## Pull requests

1. Keep changes focused and documented.
2. Add or update unit tests for validation and CLI behavior.
3. Ensure `ruff`, `mypy`, and `pytest` pass.
4. Do not add network calls in offline mode.
5. Do not introduce authentication or secret handling.

## Code style

- Typed Python with Pydantic v2 models
- Strict mypy where practical
- Ruff for lint and format
- Deterministic planner output suitable for snapshot tests

## Questions

Open an issue with a clear problem statement. Do not attach sensitive artifacts.
