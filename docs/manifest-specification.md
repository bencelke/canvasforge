# Manifest Specification (v0.1)

## Purpose

The CanvasForge application manifest is a YAML document that describes a Canvas app's structure for offline validation and deterministic planning. It is **not** a Power Apps package format.

**Manifest version:** `0.1`

## Top-level document

```yaml
app: { ... }
theme: { ... }          # optional but recommended
dataSources: []         # optional
screens: []             # required, min 1
navigation: []          # optional
permissions: []         # optional
breakpoints: { ... }    # optional (defaults applied in models)
metadata: { ... }       # optional
```

## `app`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `key` | string | yes | Stable unique key (`^[A-Za-z][A-Za-z0-9_-]*$`) |
| `name` | string | yes | Display name |
| `description` | string | no | |
| `version` | string | yes | App version (semver-like string) |
| `manifestVersion` | string | yes | Must be `"0.1"` |
| `layout` | string | no | e.g. `responsive-shell` |
| `startScreen` | string | yes | Must match a screen `key` |
| `theme` | string | no | Theme key reference |

## `theme`

| Field | Type | Required |
|-------|------|----------|
| `key` | string | yes |
| `mode` | `light` \| `dark` \| `system` | yes |
| `tokens` | object (string → string) | no |

## `dataSources[]`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `key` | string | yes | Unique |
| `kind` | `collection` \| `mock` \| `connector-deferred` | yes | Phase 1: no live connectors |
| `mode` | `offline-mock` \| `deferred` | yes | |
| `collection` | string | no | e.g. `colActions` |
| `description` | string | no | |

## `screens[]`

| Field | Type | Required |
|-------|------|----------|
| `key` | string | yes |
| `name` | string | yes |
| `title` | string | no |
| `shell` | string | no |
| `permissions` | string[] | no | Must reference `permissions[].key` |
| `sections` | Section[] | yes | Min 1; keys unique within screen |

## Sections

Discriminated by `type`. Common fields:

| Field | Type | Required |
|-------|------|----------|
| `key` | string | yes |
| `type` | enum | yes |
| `title` | string | no |
| `dataSource` | string | no | Must reference `dataSources[].key` when set |
| `layout` | string | no |
| `properties` | object | no |
| `children` | Section[] | no | Allowed for stack types |

### Supported `type` values (Phase 1)

- `page-header`
- `summary-grid`
- `summary-card`
- `action-gallery`
- `search-toolbar`
- `detail-panel`
- `empty-state`
- `vertical-stack`
- `horizontal-stack`

Unsupported types are validation errors. Sections do **not** generate Power Apps controls in Phase 1.

## `navigation[]`

| Field | Type | Required |
|-------|------|----------|
| `key` | string | yes | Unique |
| `label` | string | yes |
| `targetScreen` | string | yes | Must exist |
| `sortOrder` | integer | no | Default 0 |
| `permission` | string | no | Must exist when set |
| `implemented` | boolean | no | Default true |

## `permissions[]`

| Field | Type | Required |
|-------|------|----------|
| `key` | string | yes |
| `description` | string | no |

Permissions are declarative labels for planning. They are **not** authentication.

## `breakpoints`

| Field | Type | Required | Constraint |
|-------|------|----------|------------|
| `mobile` | positive int | no | default 640 |
| `tablet` | positive int | no | default 1024 |
| `desktop` | positive int | no | default 1440 |

Constraint: `mobile < tablet < desktop`.

## `metadata`

| Field | Type | Required |
|-------|------|----------|
| `tags` | string[] | no |
| `owner` | string | no |
| `createdFor` | string | no |
| `notes` | string | no |

## Validation summary

Validators enforce:

- Manifest version `0.1` only
- Unique app/screen/section/navigation/dataSource/permission keys
- Valid start screen and navigation targets
- Valid permission and data source references
- Supported section types only
- Breakpoint ordering
- Required fields and non-empty keys
- File size and nesting limits on load

## Non-goals for the manifest

- Embedding credentials
- Remote `$ref` / URL imports
- Environment variable interpolation
- Executable code blocks
- Direct Power Apps control property dumps (Phase 1)
