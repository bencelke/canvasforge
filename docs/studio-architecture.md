# Studio Architecture (Phase 4)

## Overview

CanvasForge Studio is a **local-only** graphical shell over the existing Python engine.

```
Browser (React/Vite)
        │ localhost HTTP JSON
        ▼
FastAPI (127.0.0.1)
        │
        ▼
CanvasForge engine (manifest → IR → preview model / package)
```

## Components

| Layer | Location | Role |
|-------|----------|------|
| CLI | `canvasforge studio` | Starts uvicorn + opens browser |
| API | `src/canvasforge/studio/` | `/api/v1` project/preview/package |
| Preview adapter | `preview_service.py` | AppIR → PreviewNode tree |
| UI | `studio/` | React + TypeScript + Vite |

## Non-goals (Phase 4)

- AI prompting
- Manifest mutation
- Microsoft auth
- Non-loopback binding
- `.msapp` / Runner

## Related

- [preview-rendering-model.md](preview-rendering-model.md)
- [studio-security.md](studio-security.md)
- [studio-user-guide.md](studio-user-guide.md)
