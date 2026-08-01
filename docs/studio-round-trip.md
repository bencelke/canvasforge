# Studio Round-Trip Workflow

## Purpose

Promote Candidate generation to Studio-exported / Studio-validated evidence **without** connecting CanvasForge to Microsoft tenants.

## Steps

1. Create a blank Canvas app in Power Apps Studio (sandbox only).
2. Insert a known-good screen/container/label/button structure manually.
3. Open **Code View** for the selected control tree.
4. Copy the YAML text.
5. Sanitize: remove tenant IDs, environment URLs, real app names, user identities, military/operational data.
6. Save under `evidence/fixtures/` (text only: `.yaml` / `.yml` / `.json` / `.md` / `.txt`).
7. Import:
   ```bash
   uv run canvasforge evidence import evidence/fixtures/your-fixture.yaml --control-type VerticalContainer
   ```
8. Generate a CanvasForge Candidate:
   ```bash
   uv run canvasforge generate examples/hello-canvasforge/app.yaml --target code-view
   ```
9. Paste the Candidate into Studio carefully and record:
   - Accepted
   - Accepted with modifications
   - Rejected
   - Error text
   - Studio version notes (no tenant IDs)
10. Add/update a reviewed JSON record under `evidence/records/`.
11. Evidence status is **never** auto-promoted.

## Public repository rules

Do not commit tenant IDs, environment URLs, real app names, user identities, screenshots with internal info, or military data.
