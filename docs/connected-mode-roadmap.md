# Connected Mode Roadmap

Connected mode is **not implemented** and must remain disabled until safety and Microsoft-supported tooling requirements are met.

## Principles

1. Explicit opt-in only
2. Human review before any write
3. No password/CAC/cookie/secret handling inside CanvasForge
4. Prefer Microsoft-supported authoring APIs/tools over reverse engineering
5. Destructive operations require additional confirmation
6. Full audit log of intended actions before execution

## Candidate future capabilities

| Capability | Requirement |
|------------|-------------|
| Read app structure via supported tooling | Official API/MCP availability |
| Apply approved screen patches | Diff + approval UX |
| Emit Code View blocks for paste | Studio-compatible output |
| Package import | Verified Microsoft-supported path only |

## Forbidden until redesigned

- Storing tenant credentials
- Silent publishing
- Silent overwrites
- Bulk deletes without confirmation
- Scraping Studio with browser cookies
- Using personal accounts against production government tenants from this tool's default workflows

## Phase gate

Connected mode may begin design only after:

1. Offline generation adapters produce Studio-validated samples.
2. A supported authentication approach exists that does not require CanvasForge to handle raw secrets.
3. Approval and rollback semantics are specified.
4. Threat model is updated and accepted.
