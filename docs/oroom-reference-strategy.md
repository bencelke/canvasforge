# O-Room Reference Strategy

## Role

**O-Room Actions** is the first **medium-complexity reference implementation** for CanvasForge. It is not hard-coded core product functionality.

Reference materials live under `examples/oroom-actions/` and use **fictional mock data only**.

## Principle

Every missing O-Room frontend capability should become a **reusable CanvasForge feature** (section type, control pattern, formula template, layout primitive, or kit report) rather than an O-Room-only hack.

## Target frontend surfaces (eventually)

CanvasForge should eventually generate layouts and Candidate artifacts sufficient to author:

1. Responsive app shell
2. Requestor Dashboard
3. Submit Action
4. My Actions
5. Action Details
6. O-Room Workspace
7. Leadership Workspace
8. S1 Workspace
9. Admin screens
10. Workflow and route-management visuals

Phase 2 already includes a reduced **dashboard proof** manifest. Full coverage is **Phase 7**.

## Mapping gaps to platform features

| O-Room need (example) | Prefer reusable CanvasForge capability |
|-----------------------|----------------------------------------|
| Role-aware navigation | Shell + nav model + permission keys in manifest |
| Status summary cards | `summary-card` / `summary-grid` section types |
| Action galleries | Allowlisted gallery patterns + evidence |
| Detail + timeline layouts | Section composition + formula templates |
| Workspace variants | Screen templates parameterized by role |
| Admin configuration UI | Generic admin form/list patterns (Phase 11) |

## Data and safety

- Mock lists and columns only
- No real unit names, EDIPI, UICs, or operational records
- No tenant connection strings in examples or kits
- SharePoint and Automate wiring remain maker-side Studio steps documented in kit checklists

## Delivery sequence

1. Expand allowlisted controls and section types as O-Room proofs demand them.
2. Keep proofs under `examples/oroom-actions/`.
3. Promote patterns into core only when generic and tested.
4. Package O-Room reference builds as Deployment Kits once Phase 3B exists.
5. Use Studio Compatibility Laboratory (Phase 10) for sanitized round-trip evidence.

## Related documents

- [offline-app-factory.md](offline-app-factory.md)
- [supported-controls-roadmap.md](supported-controls-roadmap.md)
- [development-roadmap.md](development-roadmap.md)
- [non-goals.md](non-goals.md)
