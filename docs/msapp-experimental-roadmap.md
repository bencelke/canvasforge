# Experimental `.msapp` Roadmap

## Status

**Experimental and deferred.** Code View Deployment Kits are the primary initial deployment target. CanvasForge must not fabricate `.msapp` packages from undocumented assumptions.

## Goal (future)

Optionally emit or pack an importable Canvas app package when a **Microsoft-supported**, reproducible toolchain is confirmed.

## Requirements before implementation

1. **Known-good generic starter app** — a minimal, non-tenant-specific app accepted by Studio.
2. **Confirmed supported Microsoft toolchain** — documented pack/unpack or authoring path (no reverse-engineered binary guesses).
3. **Reproducible pack/unpack behavior** — byte-stable or structurally stable across machines.
4. **Studio acceptance tests** — import, open, save, and smoke-navigate in Studio with recorded sanitized evidence.
5. **No package fabrication from undocumented assumptions** — every packing step cites a supported tool or format note.
6. **Clear Experimental label** — CLI, docs, and kit metadata must mark `.msapp` output as experimental.

## Non-goals until gated

- Shipping `.msapp` as the default kit target
- Committing real `.msapp` binaries from production tenants to the public repository
- Claiming Studio import success without recorded acceptance tests

## Evidence and repository policy

- Raw `.msapp` files remain gitignored.
- Only sanitized, approved fixtures may enter `evidence/` under the existing evidence import rules.
- Public repo must never receive tenant-bound packages.

## Phase mapping

This work is **Phase 9**. Earlier phases must deliver reliable Code View kits (Phase 3B) and a Studio Compatibility Laboratory path (Phase 10) for fixture-backed promotion.

## Related documents

- [deployment-kit-architecture.md](deployment-kit-architecture.md)
- [studio-round-trip.md](studio-round-trip.md)
- [evidence-model.md](evidence-model.md)
- [generation-safety.md](generation-safety.md)
