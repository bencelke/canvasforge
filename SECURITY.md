# Security Policy

## Current phase (offline-first App Factory)

CanvasForge is designed to run **fully offline** as a local App Factory. Connected Microsoft tooling is a future optional adapter, not the core architecture.

It must **not**:

- Connect to Microsoft 365, Power Platform, SharePoint, Dataverse, or any tenant
- Request, store, or process passwords, CAC PINs, certificates, cookies, or tokens
- Publish, share, or overwrite Power Apps
- Import remote manifests or URLs
- Execute code from manifests
- Emit telemetry
- Embed tenant IDs, environment IDs, internal URLs, or real operational data in outputs

If you observe any network, authentication, or secret-handling behavior in the current offline phases, treat it as a security bug.

## Reporting a vulnerability

Please open a private security advisory on GitHub if available, or contact the repository maintainers.

Do **not** include:

- Real credentials, tokens, or certificates
- Tenant IDs or internal URLs
- Government, military, or production operational data
- Personal identifiable information

Use fictional reproductions only.

## Hard rules for contributors and agents

1. Never commit secrets, `.env` files, CAC material, cookies, or auth exports.
2. Never commit real unit names, EDIPI, UICs, military emails, or operational records.
3. Never commit exported `.msapp` packages, solution ZIPs, Deployment Kits with sensitive content, or tenant screenshots.
4. Use safe YAML loading only (`ruamel.yaml` safe loader / no arbitrary object construction).
5. No `eval`, no dynamic code execution from manifests, no shell execution from manifest fields.
6. No remote includes, URL imports, or environment-variable interpolation in offline phases.
7. Generated output under `generated/`, local preview caches, and `*.cforge.zip` kits are local and gitignored by default.
8. Future connected operations must be explicit, reviewable, and user-approved.
9. Destructive changes (deletes, overwrites, publishes) require explicit approval in future phases.
10. Power Apps Studio remains the final validation authority for generated Canvas artifacts.
11. Local preview is advisory only — never claim Power Apps runtime equivalence.
12. Work-side Runner (future) must remain AI-free, offline, and free of Microsoft credential handling.

## Threat model

See [docs/threat-model.md](docs/threat-model.md) for the full Phase 1 threat model and mitigations.

## Public repository warning

**This repository is public.** Assume anything committed is world-readable.

- Prefer fictional examples only.
- Never push work-environment details, tenant IDs, internal URLs, or credentials.
- Never commit incoming evidence, unsanitized runtime reports, or production documents.
- Review `git status` carefully before every commit.
