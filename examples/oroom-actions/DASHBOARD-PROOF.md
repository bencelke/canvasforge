# O-Room Actions — Phase 2 dashboard proof

Reduced reference manifest for generation proof only.

Contains only generatable section types:

- page-header
- summary-grid
- summary-card (x4)
- empty-state

The full reference manifest `app.yaml` still includes `search-toolbar` and `action-gallery`, which Phase 2 cannot generate.

```bash
uv run canvasforge validate examples/oroom-actions/dashboard-proof.yaml
uv run canvasforge generate examples/oroom-actions/dashboard-proof.yaml --target code-view
```

Fictional data only. Offline. No Microsoft connectivity.
