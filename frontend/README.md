# Via Rail Performance Dashboard — Frontend

## Quick start

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
```

Backend must be running on port 8000 (Vite proxies /api/* to it):

```bash
cd backend && uvicorn app.main:app --reload
```

## Storybook

```bash
npm run storybook    # http://localhost:6006
```

## Build

```bash
npm run build        # outputs to frontend/dist/
```

## Tech stack

| Concern        | Library                    |
|----------------|----------------------------|
| Framework      | Vue 3 + TypeScript + Vite  |
| State          | Pinia                      |
| Data fetching  | @tanstack/vue-query v5     |
| Charts         | ECharts + vue-echarts      |
| Fuzzy search   | Fuse.js                    |
| Storybook      | @storybook/vue3-vite v8    |

## Environment

Copy `.env.example` to `.env.local` and adjust if your backend runs on a
different origin (only needed for production builds — the dev server proxies
all `/api` requests automatically).

```
VITE_API_BASE=
```

## Design tokens

All colours, spacing, radii, and motion values live in
`src/styles/tokens.css`. The palette mirrors Via Rail's brand:

- `--via-yellow: #FFD200` — single sharp accent colour
- `--surface-0..4` — dark navy/charcoal surface ramp
- `--status-good/med/bad` — delay status colours
