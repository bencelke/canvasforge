# Preview Rendering Model

## Principle

The React UI renders a **Preview Model** produced by Python from the same **AppIR** used for Candidate Code View generation. The frontend must not reinterpret raw manifests.

## Disclaimer

Always display:

> Local Preview — Power Apps Studio validation required

## Node types

- `screen`
- `vertical-container` / `horizontal-container`
- `text` / `button`
- `summary-grid` / `summary-card` / `empty-state`
- `unsupported-placeholder`

Unsupported allowlist sections become placeholders with warnings — they do not crash the UI.

## Responsiveness

Preview widths are advisory approximations using manifest breakpoints when available:

| Mode | Typical width |
|------|----------------|
| Desktop | ≤ 1440 |
| Tablet | ≤ 900 |
| Mobile | ≤ 390 |

These do **not** claim Power Apps breakpoint parity.
