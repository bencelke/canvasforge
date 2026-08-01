# Supported Controls Roadmap

Phase 1 models **section types**, not Power Apps controls. Control generation is deferred until Studio-verified allowlists exist.

## Phase 1 section primitives

| Section type | Intended future control mapping (provisional) |
|--------------|-----------------------------------------------|
| `page-header` | Label / HTML text / header container |
| `summary-grid` | Responsive container of summary cards |
| `summary-card` | Container + labels (count/status) |
| `action-gallery` | Gallery bound to a collection |
| `search-toolbar` | Text input + filter icons/buttons |
| `detail-panel` | Form / display container |
| `empty-state` | Labels + optional icon |
| `vertical-stack` | Vertical container |
| `horizontal-stack` | Horizontal container |

These mappings are **planning hints only** and are not emitted as Studio YAML yet.

## Candidate Phase 2 control allowlist (to verify in Studio)

- Screen
- Container (vertical / horizontal / responsive)
- Label
- Text input
- Button
- Gallery (vertical)
- Icon (limited set)
- Rectangle / separator (if needed for layout)

## Explicitly deferred / high-risk

- Custom components with unverified contracts
- Experimental controls
- Components requiring premium connectors
- Controls that need tenant-specific media
- Any control/property not documented by Microsoft for Code View or supported authoring APIs

## Promotion rule

A control or property may be generated only when:

1. It is documented as supported for the chosen target adapter.
2. At least one Studio round-trip sample exists in this repo's test evidence (future).
3. Unsupported fields fail closed with a clear diagnostic.

## O-Room note

O-Room Actions may need additional patterns later (workflow progress, role shells). Those patterns will be expressed as reusable section recipes in examples or libraries—not as unchecked control invention in core.
