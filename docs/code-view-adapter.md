# Code View Adapter

Target name: `code-view`

Location: `src/canvasforge/adapters/code_view/`

## Behavior

1. Accept `AppIR`
2. Resolve logical controls via the registry
3. Reject unknown controls/properties (fail closed)
4. Emit deterministic UTF-8 YAML without anchors/aliases
5. Write a separate generation report
6. Never embed secrets or absolute local paths

## Output status

All adapter YAML is labeled:

**Studio-unvalidated Candidate**

Do not treat it as production Power Apps source. Studio is the final authority.

## Document shape (Candidate)

```yaml
CanvasForgeCandidate: true
Status: Studio-unvalidated
Screen:
  Name: scrDashboard
  Control: Screen
  Properties: { ... }
  Children: [ ... ]
```

This shape is provisional pending a Studio-exported fixture under `evidence/fixtures/`.
