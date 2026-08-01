# Evidence Model

## Record fields

- `evidenceId`
- `controlType`
- `property` (optional)
- `sourceType`: `official-documentation` | `studio-export` | `studio-round-trip` | `test-fixture`
- `sourceReference` (basename only; no absolute paths)
- `studioAccepted`
- `studioVersion`
- `environmentClass`: `commercial` | `government` | `unknown`
- `notes`
- `recordedOn`
- `checksum` (SHA-256)

## Layout

```
evidence/
  README.md
  fixtures/
  records/
```

## Import safety

- Local files only
- Size limit
- Text extensions only
- Reject binaries
- Reject absolute paths, URLs, and tenant markers in content
- No formula execution
- No network fetches
