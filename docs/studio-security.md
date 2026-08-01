# Studio Security (Phase 4)

## Loopback only

Default bind host is `127.0.0.1`. Non-loopback hosts are refused.

## Path sandbox

Manifest open and kit output paths must resolve under configured workspace roots (repository root + `examples/`) or the local `dist/` directory. Path traversal and absolute foreign paths are rejected.

## Hardening

- No arbitrary filesystem browsing
- No execution of project content
- No raw HTML from manifests (text escaped via React)
- Manifest size limits
- No secret/env exposure
- No telemetry
- No remote CDNs / remote fonts
- CORS limited to local frontend origins
- Offline by default; no Microsoft login

## Packaging

Studio calls the existing Deployment Kit builder/verifier. It does not reimplement packaging in TypeScript.
