# Threat Model (Phase 1)

## Scope

This threat model covers the offline CanvasForge CLI, local manifest files, generated planning output, documentation, and CI. It does **not** cover Microsoft tenant operations (those are future, explicit, and disabled here).

## Assets

- Local source code and manifests
- Developer workstation integrity
- Public repository reputation (no leaked secrets/data)
- Future generated Power Apps artifacts (integrity and reviewability)

## Actors

- Benign developer / AI coding agent
- Malicious or compromised project files
- Accidental contributor of sensitive data
- Supply-chain attacker via dependencies

## Threats and mitigations

| Threat | Risk | Mitigation in Phase 1 |
|--------|------|------------------------|
| Prompt injection from project files | Medium | Manifest is structured data; no instruction-following from free-form remote content; no remote includes |
| Unsafe generated formulas | High (future) | No Power Fx generation yet; future generators must validate against allowlists |
| Credential leakage | High | No auth handling; secrets gitignored; SECURITY.md warnings |
| Tenant identifier leakage | High | No tenant connectivity; fictional examples only |
| Destructive changes | High (future) | No publish/delete/overwrite operations exist |
| Unapproved publishing | High (future) | Connected operations require explicit approval later |
| Accidental app overwrite | High (future) | No connected write path in Phase 1 |
| Generated unsupported properties | Medium (future) | No control generation yet; schema limits section types |
| Government data in public repo | Critical | CONTRIBUTING/SECURITY bans; fictional mock data only |
| Sensitive logs | Medium | No telemetry; errors avoid dumping secrets; offline mode |
| Malicious manifest content | Medium | Schema + semantic validation; size/nesting limits |
| Path traversal | Medium | Manifest paths resolved as files; no include directives |
| YAML parser safety | Medium | Safe loader only (`ruamel.yaml` safe); no arbitrary object construction |
| Arbitrary code execution | High | No eval; no shell from manifest; no code fields executed |
| Dependency supply-chain risk | Medium | Pinned lockfile (`uv.lock`); CI on known tools; minimal deps |

## Security rules (enforced by design)

- Safe YAML loader only
- No `eval`
- No arbitrary code execution
- No shell execution from manifest
- No remote includes
- No URL imports
- No environment-variable interpolation in Phase 1
- No authentication handling
- No telemetry
- No network calls in offline mode
- Generated and secret files excluded from Git
- Explicit file-size limits
- Explicit manifest nesting limits

## Residual risks / open questions

- Exact Microsoft-supported paths for Code View and packaging remain to be validated.
- Future connected adapters will need a stronger approval and audit model.
- AI agents editing manifests may still introduce sensitive content; process controls are required.

## Incident response (lightweight)

1. Rotate any exposed secrets outside this repo.
2. Remove sensitive commits via coordinated disclosure (do not push secrets "fixed" in a follow-up commit alone if already public).
3. Document the issue without reproducing sensitive payloads.
