# O-Room Actions — requestor dashboard (reference)

Provisional **reference** manifest for the requestor dashboard only.

This is **not** the CanvasForge product. Domain terminology stays in `examples/`.

## Safety

Mock data is entirely fictional. Do not add:

- Real names
- Military email addresses
- UICs / EDIPI
- Operational data
- Internal URLs / tenant IDs
- Real unit names

## Limitation — Phase 2 generation

The full `app.yaml` includes `search-toolbar` and `action-gallery`, which are **not generatable** in Phase 2.

Use the reduced proof manifest instead:

- [`dashboard-proof.yaml`](dashboard-proof.yaml)
- [`DASHBOARD-PROOF.md`](DASHBOARD-PROOF.md)

## Try it

```bash
uv run canvasforge validate examples/oroom-actions/app.yaml
uv run canvasforge inspect examples/oroom-actions/app.yaml
uv run canvasforge plan examples/oroom-actions/app.yaml
uv run canvasforge validate examples/oroom-actions/dashboard-proof.yaml
uv run canvasforge generate examples/oroom-actions/dashboard-proof.yaml --target code-view
```
