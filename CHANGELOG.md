# Changelog

All notable changes to CanvasForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Phase 3B: Deployment Kit builder (`canvasforge package` / `inspect` / `verify`).
- Deployment Kit schema 0.1, forbidden-content scanner, deterministic `.cforge.zip`.
- Docs: deployment-kit-format/security/versioning, maker-handoff.

### Added (Phase 3A)

- Phase 3A: offline App Factory architecture docs, restructured roadmap (Phases 3A–11), Windows migration report.
- `.gitattributes` LF normalization for cross-platform checksum/snapshot stability.
- Broader `.gitignore` exclusions for kits, preview caches, solution ZIPs, and local evidence.

### Changed

- Manifest checksum / build ID computation normalizes newlines to LF (Windows `autocrlf` safety).
- README, architecture, product vision, and security docs updated for offline-first product direction.

### Added (Phase 2)

- Phase 2: normalized AppIR, control allowlist, Candidate Code View adapter.
- CLI commands: `generate`, `controls`, `evidence`.
- Hello CanvasForge deterministic Candidate generation + snapshot tests.
- O-Room `dashboard-proof.yaml` reduced proof manifest.
- Studio round-trip and evidence documentation.

## [0.2.0] - Unreleased

Phase 2 Candidate generation foundation (local development; Studio-unvalidated).

## [0.1.0] - Unreleased

Initial foundation release candidate (local development only; not published).
