# Maker Handoff

## Concept

1. Build a Deployment Kit on a local/home machine with CanvasForge Studio (CLI).
2. Transfer the `.cforge.zip` through an **approved** organizational channel.
3. On the work side, verify the kit (`canvasforge package verify` or future Runner).
4. An authorized maker pastes Candidate Code View into Power Apps Studio.
5. Connect SharePoint Lists / Automate manually.
6. Validate and publish only after approval.

CanvasForge does not authenticate to Microsoft services and does not publish apps.

## Commands

```bash
uv run canvasforge package examples/hello-canvasforge/app.yaml \
  --output dist/Hello-CanvasForge.cforge.zip

uv run canvasforge package examples/oroom-actions/dashboard-proof.yaml \
  --output dist/O-Room-Dashboard-Proof.cforge.zip

uv run canvasforge package verify dist/Hello-CanvasForge.cforge.zip
uv run canvasforge package inspect dist/Hello-CanvasForge.cforge.zip
```

## Warnings

- Kits contain **Candidate** output — Studio validation required.
- Never place production data, credentials, or tenant IDs in kits.
- Do not commit generated ZIPs to the public repository.
- Lists are **not** created automatically (see `deployment/data-connection-checklist.md` inside the kit).
