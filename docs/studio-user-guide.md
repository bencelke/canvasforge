# Studio User Guide

## Prerequisites

- Python 3.12+ with `uv`
- Node.js 20+ and npm (for UI build / dev)

## Install

```bash
uv sync --all-extras --dev
cd studio
npm ci
npm run build
cd ..
```

## Run (production-style local)

```bash
uv run canvasforge studio --project examples/hello-canvasforge/app.yaml
```

Opens `http://127.0.0.1:<port>/` serving the built UI + API.

## Run (development)

Terminal A:

```bash
uv run canvasforge studio --dev --api-port 8765 --no-open --project examples/hello-canvasforge/app.yaml
```

Terminal B:

```bash
cd studio
npm run dev
```

Open the Vite URL (`http://127.0.0.1:5173`).

## Workflow

1. Open Hello or O-Room Dashboard Proof from the demo list.
2. Inspect screen tree and preview (desktop/tablet/mobile).
3. Click **Validate**.
4. Click **Build Kit** — uses Phase 3B packaging; kit lands under `dist/` and is verified.

## Disclaimer

Local Preview — Power Apps Studio validation required.
