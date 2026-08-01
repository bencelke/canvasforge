# Deployment Kit Format (schema 0.1)

## What a `.cforge.zip` is

A **CanvasForge Deployment Kit** is a deterministic ZIP archive that carries:

- The source manifest
- Candidate Code View YAML
- Control tree and generation plan
- Mock schema (and optional fictional records)
- Maker deployment checklists
- Compatibility/evidence summaries
- SHA-256 checksums

It is intended for approved transfer to a work environment where an authorized maker pastes or imports frontend artifacts into Power Apps Studio.

## What it is not

- Not a Power Apps `.msapp`
- Not a Power Platform solution
- Not an executable or installer
- Not an authentication package
- Not a production-data package
- Not a substitute for maker permissions or Studio validation

## File layout

```
project-name.cforge.zip
├── canvasforge-project.json
├── app.manifest.yaml
├── theme/theme.json
├── formulas/
│   ├── README.md
│   ├── app-onstart.powerfx          # placeholder when not generated
│   └── screen-formulas/README.md
├── mock-schema/
│   ├── README.md
│   ├── data-contract.json
│   ├── collections.json
│   └── records/                     # only with --include-mock-data
├── generated/
│   ├── code-view/<screen>.yaml
│   ├── control-tree.json
│   └── generation-plan.json
├── deployment/
│   ├── install-order.md
│   ├── power-apps-checklist.md
│   ├── data-connection-checklist.md
│   ├── validation-record-template.json
│   └── known-limitations.md
├── compatibility/
│   ├── profile.json
│   └── evidence-summary.json
├── reports/
│   ├── build-report.json
│   ├── validation-report.json
│   ├── forbidden-content-report.json
│   └── package-manifest.json
└── checksums.sha256
```

## Checksum algorithm

See [deployment-kit-security.md](deployment-kit-security.md). Summary:

1. Normalize text member bytes to LF.
2. `packageContentChecksum` hashes all members except `canvasforge-project.json` and `checksums.sha256`.
3. Write that digest into `canvasforge-project.json`.
4. `checksums.sha256` lists digests for every member except itself (`sha256sum` style, paths sorted).

## CLI

```bash
uv run canvasforge package examples/hello-canvasforge/app.yaml \
  --output dist/Hello-CanvasForge.cforge.zip

uv run canvasforge package inspect dist/Hello-CanvasForge.cforge.zip
uv run canvasforge package verify dist/Hello-CanvasForge.cforge.zip
```

`canvasforge package <manifest.yaml>` is shorthand for `canvasforge package build <manifest.yaml>`.

## Extraction

`package extract` is **deferred**. Use `inspect` and `verify` plus a trusted ZIP tool after verification. ZIP Slip-safe extraction may arrive with the work-side Runner (Phase 8).

## Related

- [deployment-kit-architecture.md](deployment-kit-architecture.md)
- [deployment-kit-security.md](deployment-kit-security.md)
- [deployment-kit-versioning.md](deployment-kit-versioning.md)
- [maker-handoff.md](maker-handoff.md)
