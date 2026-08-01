# Windows Migration Report

**Date:** 2026-08-01
**OS:** Windows 10 (build 22631)
**Task:** Phase 3A — PC migration and offline architecture pivot

This report intentionally omits usernames, home-directory paths, and machine-identifying information.

## Toolchain

| Tool | Version / notes |
|------|-----------------|
| Python (system default) | 3.10.9 on PATH (below project requirement) |
| Python (project) | CPython **3.12.9** via `uv python install 3.12` |
| uv | 0.7.19 |
| Git | 2.55.0.windows.3 |
| Repository commit (baseline) | `14adf64d2db50de474d96411d0b4e5d58fbc67d8` (Phase 2) |
| Branch | `main` |
| Origin | `https://github.com/bencelke/canvasforge.git` |

## Repository setup

- Local folder was empty; repository cloned into the workspace root.
- `main` checked out and matched the expected Phase 2 baseline commit.
- Working tree was clean immediately after clone.

## Dependency setup

```text
uv python install 3.12
uv sync --all-extras --dev
```

- Virtual environment created at `.venv` using CPython 3.12.9.
- 44 packages installed successfully.
- uv warned that hardlinking failed and fell back to full copy (likely cross-filesystem cache). Optional mitigation: `UV_LINK_MODE=copy`.

## Quality gate results

| Check | Result |
|-------|--------|
| `uv run canvasforge version` | Pass (`0.2.0`) |
| `uv run canvasforge doctor` | Pass (all offline checks OK) |
| `uv run canvasforge validate examples/hello-canvasforge/app.yaml` | Pass |
| `uv run canvasforge validate examples/oroom-actions/app.yaml` | Pass |
| `uv run canvasforge plan examples/hello-canvasforge/app.yaml` | Pass |
| `uv run pytest` | Pass — **39** tests (38 prior + 1 newline checksum test) |
| Coverage | ~**82%** statement coverage (pytest-cov; not intentionally reduced) |
| `uv run ruff check .` | Pass |
| `uv run ruff format --check .` | Pass (after LF renormalization) |
| `uv run mypy src tests` | Pass — no issues in 40 source files |

## Windows-specific problems

1. **Python 3.12 not on system PATH** — only 3.10 was installed system-wide. Resolved with `uv python install 3.12` (no system Python installer required for development).
2. **`core.autocrlf=true`** — Git checked out text files as CRLF. Effects:
   - Manifest `read_bytes()` checksums differed from Linux/macOS → Candidate `buildId` snapshot mismatches.
   - `ruff format --check` reported widespread “reformat” noise (EOL-only).
3. **uv hardlink warning** — cache/target on different filesystems; copy fallback works; performance only.
4. **Console encoding** — doctor table may show mojibake for Unicode dashes in some Windows terminals; functional output unaffected.

## Code changes required for Windows compatibility

| Change | Justification |
|--------|----------------|
| `compute_manifest_checksum` normalizes `\r\n` / `\r` → `\n` before hashing | Keeps build IDs platform-stable under autocrlf |
| `.gitattributes` with `eol=lf` for text sources | Prevents recurring CRLF checkout drift |
| Working-tree LF renormalization | Restores Ruff format check and file consistency |
| Unit test `test_manifest_checksum_normalizes_newlines` | Locks the checksum contract |

No Phase 1/2 behavioral features were redesigned. No Deployment Kit builder, GUI preview, Microsoft auth, or network client was added.

## Documentation delivered (architecture pivot)

- `docs/offline-app-factory.md`
- `docs/deployment-kit-architecture.md`
- `docs/local-preview-architecture.md`
- `docs/work-side-runner.md`
- `docs/msapp-experimental-roadmap.md`
- `docs/oroom-reference-strategy.md`
- `docs/development-roadmap.md` (Phases 3A–11)
- `docs/architecture.md`
- `docs/windows-migration-report.md` (this file)
- Updates: `README.md`, `SECURITY.md`, `CHANGELOG.md`, `docs/product-vision.md`, `docs/offline-mode.md`, `docs/connected-mode-roadmap.md`

## Security verification

| Control | Status |
|---------|--------|
| `.gitignore` covers `.env`, credentials, certs, `.msapp`, ZIPs/solutions, kits, evidence incoming/runtime, generated output, preview caches, screenshots | Present |
| Public-repo warnings in README / SECURITY | Present / strengthened |
| No work-environment details, tenant IDs, or credentials added | Confirmed for this migration |
| Offline posture preserved (no Microsoft connection/auth) | Confirmed |

## Recommended next implementation phase

**Phase 3B — Portable Deployment Kit specification and builder**

Implement the `.cforge.zip` packager and contracts described in `docs/deployment-kit-architecture.md`, with forbidden-content checks and golden tests for Hello + O-Room proof manifests. Do not start the React preview (Phase 4) until kit packaging is specified and tested.
