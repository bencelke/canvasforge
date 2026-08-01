# Power Fx Strategy

## Phase 1 status

CanvasForge does **not** generate Power Fx in Phase 1.

## Principles for later phases

1. **Allowlist first** — only emit formulas/patterns that are documented and Studio-verified.
2. **No improvisation for deployment** — models may draft candidates; validators decide.
3. **Deterministic templates** — same manifest → same formulas.
4. **Safe by default** — avoid dynamic evaluation constructs that embed untrusted strings unsafely.
5. **Separate data binding from secrets** — never embed credentials, tokens, or tenant secrets in formulas.
6. **Studio authority** — generated formulas must be reviewed and validated in Power Apps Studio.

## Planned formula categories (future)

- Navigation (`Navigate(scrX, ScreenTransition.None)`)
- Simple filter/search over collections
- If/Switch status badge labels
- Count rows for summary cards
- Form reset / submit stubs against mock collections

## Explicitly forbidden (all phases unless safety model changes)

- Executing Power Fx locally as code
- Embedding passwords, tokens, or certificate material
- Generating connector calls that imply live tenant access without connected-mode approval
- Obfuscated or minified formula blobs that hinder review

## Validation vision

Future Power Fx output should pass:

1. Syntax/shape checks against known patterns
2. Reference checks to screens, controls, and collections declared in the plan
3. Human review checklist
4. Studio runtime validation
