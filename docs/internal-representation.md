# Internal Representation

Phase 2 introduces a normalized **AppIR** between validated manifests and target adapters.

```
Manifest → Schema/Semantic validation → AppIR / ControlNode tree → Adapter → Candidate artifacts
```

## Core models

| Model | Purpose |
|-------|---------|
| `AppIR` | App-level IR |
| `ScreenIR` | One screen with a root `ControlNode` |
| `ControlNode` | Typed control with children, properties, formulas, source path |
| `PropertyValue` / `FormulaValue` / `LayoutValue` | Typed assignments |
| `SourceReference` | Manifest path + app/screen/section/role traceability |
| `GenerationPlan` / `GenerationArtifact` / `GenerationDiagnostic` | Build metadata |

## Stable IDs vs Power Apps names

- **Internal ID**: deterministic slash path, e.g. `hellocanvasforge/scrdashboard/cardready/value-label`
- **Control name**: Power Apps-facing, e.g. `lblCardOpenValue`

IDs never use random UUIDs.

## Generation status

Nodes start as `candidate`. Studio validation state on reports starts as `unvalidated` and changes only through explicit evidence recording.
