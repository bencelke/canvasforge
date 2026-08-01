# Deployment Kit Architecture

## Purpose

A **CanvasForge Deployment Kit** is a portable, tenant-neutral package that carries validated frontend artifacts from a local Studio build to a work environment for manual Studio import or Code View paste.

Primary initial deployment target: **Code View Deployment Kits**.

Importable `.msapp` generation is **experimental and deferred** (see [msapp-experimental-roadmap.md](msapp-experimental-roadmap.md)).

## Package identity

- File name pattern: `project-name.cforge.zip`
- Extension `.cforge.zip` signals a CanvasForge kit (ZIP container)
- Must be checksum-verifiable and inspectable without Power Apps login

## Proposed structure

```
project-name.cforge.zip
├── canvasforge-project.json
├── app.manifest.yaml
├── theme/
├── formulas/
├── mock-schema/
├── generated/
│   └── code-view/
├── deployment/
│   ├── install-order.md
│   └── power-apps-checklist.md
├── compatibility/
│   └── profile.json
├── reports/
│   ├── build-report.json
│   └── validation-report.json
└── checksums.sha256
```

### File roles

| Path | Role |
|------|------|
| `canvasforge-project.json` | Kit metadata: app key, CanvasForge version, kit schema version, generation target, timestamps omitted or build-id based |
| `app.manifest.yaml` | Source manifest used for the build (tenant-neutral) |
| `theme/` | Theme tokens / notes for Studio recreation |
| `formulas/` | Extracted or templated Power Fx candidates |
| `mock-schema/` | Fictional list/column shapes for maker wiring guidance |
| `generated/code-view/` | Candidate Code View YAML blocks per screen |
| `deployment/install-order.md` | Ordered human steps for Studio paste/import |
| `deployment/power-apps-checklist.md` | Maker checklist (connections, permissions, publish) |
| `compatibility/profile.json` | Declared control/property evidence profile for the build |
| `reports/build-report.json` | Deterministic generation report |
| `reports/validation-report.json` | Manifest validation summary |
| `checksums.sha256` | Digests for every package member |

## Forbidden package contents

The kit **must not** contain:

- Tenant connections or environment bindings
- Credentials, tokens, certificates, or CAC material
- Real operational or military data
- Production documents
- User identities or PII
- Internal URLs or tenant IDs
- Unpublished secrets from local `.env` files

## Trust model

1. Built offline on a home/local machine.
2. Transferred through an **approved** organizational channel.
3. Opened by **CanvasForge Runner** (future) or inspected manually.
4. Applied in Studio only by an authorized maker.
5. Studio validation and publishing remain human-owned.

## Builder (Phase 3B — implemented)

```bash
uv run canvasforge package path/to/app.yaml --output dist/App.cforge.zip
uv run canvasforge package inspect dist/App.cforge.zip
uv run canvasforge package verify dist/App.cforge.zip
```

See [deployment-kit-format.md](deployment-kit-format.md).

## Consumer (future — Phase 8)

See [work-side-runner.md](work-side-runner.md). The Runner opens kits offline, verifies checksums, and surfaces Code View blocks and checklists. It does not publish apps.

## Versioning

- Kit schema version is independent of app manifest version.
- Kits declare the CanvasForge version that produced them.
- Older Runners may reject newer kit schemas with a clear error.

## Related documents

- [offline-app-factory.md](offline-app-factory.md)
- [work-side-runner.md](work-side-runner.md)
- [code-view-adapter.md](code-view-adapter.md)
- [generation-safety.md](generation-safety.md)
