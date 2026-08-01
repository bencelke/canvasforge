# Control Registry

The Phase 2 allowlist lives under `src/canvasforge/controls/`.

## Logical controls (bootstrap)

| Logical | Code View ID (Candidate) | Evidence |
|---------|--------------------------|----------|
| Screen | Screen | documented |
| VerticalContainer | GroupContainer | documented |
| HorizontalContainer | GroupContainer | documented |
| Text | Label | documented |
| Button | Button | documented |

## Evidence policy

| Status | Generation |
|--------|------------|
| studio-validated | allowed |
| studio-exported | allowed as Candidate |
| documented | allowed as Candidate |
| inferred | blocked |
| unsupported | blocked |

No Studio-exported fixtures exist in-repo yet. Bootstrap entries are **documented** only. Exact YAML shape remains **Studio-unvalidated Candidate**.

## Section expansion

Generatable: `page-header`, `summary-grid`, `summary-card`, `empty-state`, `vertical-stack`, `horizontal-stack`.

Not generatable (fail closed): `action-gallery`, `search-toolbar`, `detail-panel`.
