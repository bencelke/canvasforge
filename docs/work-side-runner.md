# Work-Side Runner

## Purpose

**CanvasForge Runner** is a future offline Windows application used on the work side of an approved transfer boundary. It opens Deployment Kits, verifies integrity, and helps authorized makers apply frontend artifacts in Power Apps Studio.

Runner is **deterministic, offline, and AI-free**.

## Must

| Capability | Notes |
|------------|-------|
| Open `.cforge.zip` | Local filesystem only |
| Verify checksums | Compare members to `checksums.sha256` |
| Show package contents | Tree and file previews for text artifacts |
| Display deployment order | From `deployment/install-order.md` |
| Expose Code View blocks | From `generated/code-view/` for copy/paste |
| Display formulas | From `formulas/` |
| Record Studio validation results | Manual maker input → sanitized local report |
| Produce sanitized compatibility reports | No tenant secrets; fictional or redacted fields only |

## Must not

- Contain AI models, prompts, or agent loops
- Require internet access
- Handle CAC, passwords, cookies, or Microsoft credentials
- Publish, share, or overwrite Power Apps
- Bypass maker permissions
- Automatically connect production data
- Embed military/operational content

## Relationship to Studio

Runner assists transfer and review. **Power Apps Studio** remains the only system that validates runtime behavior and publishes apps.

## Trust and transfer

1. Kit built on CanvasForge Studio (home/local).
2. Approved organizational transfer into the work environment.
3. Runner verifies checksums before displaying apply steps.
4. Maker pastes or imports under their own credentials in Studio.
5. Optional sanitized compatibility notes may flow back to the public engineering process **without** tenant identifiers.

## Implementation phase

Runner is **Phase 8**. No Runner application code is implemented in Phase 3A.

## Related documents

- [deployment-kit-architecture.md](deployment-kit-architecture.md)
- [offline-app-factory.md](offline-app-factory.md)
- [threat-model.md](threat-model.md)
- [development-roadmap.md](development-roadmap.md)
