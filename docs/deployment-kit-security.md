# Deployment Kit Security

## Threat posture

Kits move across trust boundaries. CanvasForge must never embed credentials, tenant identifiers, production data, or machine identity. Verification must fail closed on tampering and unsafe archives.

## Forbidden-content scan

Before ZIP creation, text members are scanned.

**Blocking (cannot be bypassed):**

- Private key / certificate PEM markers
- Bearer tokens
- `api_key` / `access_token` / `client_secret` assignments
- CAC/PIV PIN material references
- Forbidden binary suffixes (`.msapp`, `.pem`, `.pfx`, …)

**Warnings (recorded, usually non-blocking):**

- Email addresses
- URLs (allowlisted hosts suppressed)
- GUID-like identifiers
- Tenant/environment term labels
- Absolute personal paths
- Military email domains / EDIPI / UIC / SSN labels
- Explicit production-data markers

Findings never echo full secrets—only redacted excerpts.

Report path: `reports/forbidden-content-report.json`.

## Archive defenses

| Control | Limit (Phase 3B) |
|---------|------------------|
| Archive size | 50 MiB |
| Per-member size | 5 MiB |
| Uncompressed total | 80 MiB |
| Compression ratio | 100:1 (for members &gt; 1 MiB) |
| Member count | 500 |
| Path traversal / absolute paths | Rejected |
| Duplicate members | Rejected |

## Checksum algorithm (canonical)

1. Store every text member as UTF-8 with LF newlines.
2. Compute `SHA-256` for each member path (POSIX `/` separators).
3. `packageContentChecksum` = SHA-256 of the concatenation, for each path in sorted order excluding `canvasforge-project.json` and `checksums.sha256`:

   ```
   {path}\n{hex_digest}\n
   ```

4. Embed `packageContentChecksum` in `canvasforge-project.json`.
5. Write `checksums.sha256` covering every member **except itself**, lines sorted by path:

   ```
   {hex_digest}  {path}\n
   ```

6. `canvasforge package verify` recomputes steps 2–5 and compares.

## Declarations

`canvasforge-project.json` always declares for Phase 3B kits:

- `securityClassification = fictional-development`
- `containsProductionData = false`
- `containsCredentials = false`
- `containsTenantIdentifiers = false`
- `packageCreatedBy = CanvasForge`

No username, hostname, absolute path, or token fields are permitted.

## Mock data

Default kits include schema only. `--include-mock-data` may add **fictional** records, scanned like all other members, classified as `fictional-records`.
