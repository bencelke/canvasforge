# Hello CanvasForge

Minimal valid CanvasForge manifest for offline validation, inspection, and planning.

## Contents

- One screen: `scrDashboard`
- Page header, two summary cards, empty state
- Single navigation item
- No external data sources

## Try it

```bash
uv run canvasforge validate examples/hello-canvasforge/app.yaml
uv run canvasforge inspect examples/hello-canvasforge/app.yaml
uv run canvasforge plan examples/hello-canvasforge/app.yaml
```

This example is fictional and offline-only. It does not connect to Microsoft services.
