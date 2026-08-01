# Supported Controls Roadmap

## Phase 2 logical allowlist (Candidate)

| Logical | Code View ID | Evidence | Notes |
|---------|--------------|----------|-------|
| Screen | Screen | documented | Studio-unvalidated |
| VerticalContainer | GroupContainer | documented | LayoutDirection=Vertical |
| HorizontalContainer | GroupContainer | documented | LayoutDirection=Horizontal |
| Text | Label | documented | Candidate mapping |
| Button | Button | documented | OnSelect omitted |

## Generatable sections

- page-header
- summary-grid
- summary-card
- empty-state
- vertical-stack
- horizontal-stack

## Not generatable yet

- action-gallery
- search-toolbar
- detail-panel

## Promotion rule

A control or property may be generated only when evidence status is `documented`, `studio-exported`, or `studio-validated`. `inferred` and `unsupported` fail closed.

Studio-exported fixtures should be added under `evidence/fixtures/` via the round-trip workflow before claiming Studio compatibility.
