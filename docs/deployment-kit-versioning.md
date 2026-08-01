# Deployment Kit Versioning

## Package schema version

- Current: **0.1**
- Field: `packageSchemaVersion` in `canvasforge-project.json`
- Independent of app `manifestVersion` and CanvasForge package version

## Compatibility policy

| Change type | Rule |
|-------------|------|
| Additive optional fields / members | May remain in `0.x` with documentation |
| Removing/renaming required fields | Bump schema version |
| Unknown major / unsupported version | **Fail closed** on verify |

Supported versions are listed in code as `SUPPORTED_PACKAGE_SCHEMA_VERSIONS`.

## Reproducibility

Default builds are reproducible for identical:

- Source manifest bytes (LF-normalized)
- CanvasForge version
- Compatibility profile
- Build options (`--allow-partial`, `--include-mock-data`, screen selection, target)

`--non-reproducible-metadata` may adjust notes only; it still must not embed machine identity.

## JSON Schema

- Source: `schemas/deployment-kit.schema.json`
- Installed copy: `canvasforge/data/deployment-kit.schema.json`
