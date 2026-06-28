# Next.js dashboard (M5)

Minimal triage UI for the AI Release Intelligence Platform.

## Views

1. **Login** — `/login`
2. **CI runs list** — `/runs` (US-003)
3. **Run detail + release risk** — `/runs/[id]` (US-007)
4. **Failure detail + classification** — `/failures/[id]` (US-004)
5. **Similar failures panel** — section on failure page (US-006)
6. **Feedback form** — section on failure page (US-008)
7. **Metrics summary** — `/metrics` (US-011)
8. **Admin demo replay** — `/admin/replay` (US-010)

## Local development

```bash
# From repo root — API on :8000
uvicorn api.main:app --reload --port 8000

cd apps/web
npm install
npm run dev
```

Open http://localhost:3000 — login with `analyst@demo.example.com` / `demo-pass-1`.

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `apps/web/.env.local` if needed.

## Production

See [docs/deploy/README.md](../../docs/deploy/README.md).
