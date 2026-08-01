# Contributing to CanvasForge

Thank you for helping build CanvasForge. This project is early and intentionally constrained (offline App Factory through Phase 3B Deployment Kits).

## Safety first

This repository is **public**. Do not contribute:

- Secrets, tokens, passwords, CAC PINs, certificates, or cookies
- Tenant IDs, internal URLs, or production connector configuration
- Government, military, or operational data
- Real names, EDIPI, UICs, or military email addresses
- Exported `.msapp` packages, Deployment Kits (`.cforge.zip`), or internal screenshots

Use fictional data only. See [SECURITY.md](SECURITY.md) and [docs/deployment-kit-security.md](docs/deployment-kit-security.md).

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

## Scope (current)

In scope:

- Manifest models and validation
- Candidate Code View generation
- Deployment Kit packaging (`canvasforge package`)
- CLI, documentation, examples, tests, CI

Out of scope until a later phase:

- Local graphical preview (Phase 4)
- Work-side Runner (Phase 8)
- Experimental `.msapp` (Phase 9)
- Microsoft authentication / connected APIs
- MCP servers and editor extensions

Do not hard-code O-Room terminology into `src/canvasforge`. Reference apps live under `examples/`.
Never commit generated `dist/*.cforge.zip` kits.

## Pull requests

1. Keep changes focused and documented.
2. Add or update unit tests for validation, generation, and packaging behavior.
3. Ensure `ruff`, `mypy`, and `pytest` pass.
4. Do not add network calls in offline mode.
5. Do not introduce authentication or secret handling.

## Code style

- Typed Python with Pydantic v2 models
- Strict mypy where practical
- Ruff for lint and format
- Deterministic planner and kit output suitable for snapshot tests

## Questions

Open an issue with a clear problem statement. Do not attach sensitive artifacts.
