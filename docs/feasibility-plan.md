# Feasibility Plan

## Goal

Determine what CanvasForge can safely and usefully automate for Power Apps Canvas frontend construction without fabricating unsupported Microsoft formats or connecting to tenants in Phase 1.

## Feasible now (Phase 0/1)

| Capability | Feasibility | Notes |
|------------|-------------|-------|
| Structured app manifest | High | Fully under our control |
| JSON Schema + semantic validation | High | Implemented |
| Deterministic planning | High | Implemented |
| Offline CLI / docs / examples | High | Implemented |
| Administrative layout modeling | High | Section types as planning primitives |
| Diffable artifacts | High | YAML + plan text |

## Feasible later (with validation)

| Capability | Feasibility | Dependency |
|------------|-------------|------------|
| Paste-ready Code View blocks | Medium–High | Must match Studio-supported YAML/control shapes |
| Power Fx snippet generation | Medium | Allowlists + Studio validation |
| Responsive shell patterns | Medium | Pattern library + Studio verification |
| Connected authoring updates | Unknown–Medium | Requires supported Microsoft tooling and explicit approval UX |
| Importable packages | Unknown | Only if a verified Microsoft-supported package/source path exists |

## Not feasible / not allowed now

| Capability | Reason |
|------------|--------|
| Reverse-engineered `.msapp` writing | Unsupported / fragile / unsafe |
| Tenant auth / CAC / secrets | Explicitly forbidden |
| Publishing/sharing apps | Explicitly forbidden in Phase 1 |
| Guaranteeing Studio parity without Studio | Studio is authority |
| AI improvising deployment packages | Must pass validation gates |

## Reference app path

O-Room Actions will be used to pressure-test:

1. Manifest expressiveness for admin workflows
2. Section composition (header, summary grid, gallery, empty state)
3. Role-aware navigation modeling (permissions as data, not auth)
4. Mock collection planning without real SharePoint connectors

## Success metrics for Phase 1

- Hello and O-Room manifests validate offline
- Invalid manifests fail with actionable, path-associated errors
- `plan` output is deterministic
- CI enforces lint, types, and tests
- No network or Microsoft authentication surface exists

## Exit criteria to Phase 2 (generation)

Phase 2 should start only when:

1. A small allowlist of Studio-verified controls/properties is documented.
2. A Code View or equivalent adapter can emit inspectable output.
3. Round-trip checks in Studio are defined for at least one sample screen.
4. Unsupported constructs fail closed with clear errors.
