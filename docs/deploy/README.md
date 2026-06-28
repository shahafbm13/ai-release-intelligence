# Deployment — Render + Neon + Upstash ($0 tier)

## Architecture

| Component | Platform |
|-----------|----------|
| API + Celery worker | Render free web service |
| PostgreSQL | Neon free tier |
| Redis | Upstash free tier |
| Next.js UI | Render static site or second web service |

## Prerequisites

1. Neon project + connection string (`DATABASE_URL`)
2. Upstash Redis (`REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`)
3. Render account
4. Optional: Groq/Gemini API keys for live LLM classification

## Environment variables (API service)

```
APP_ENV=production
JWT_SECRET=<long-random-string>
DATABASE_URL=<neon-pooled-url>
REDIS_URL=<upstash-url>
CELERY_BROKER_URL=<upstash-url>
CELERY_RESULT_BACKEND=<upstash-url>/1
GITHUB_WEBHOOK_SECRET=<optional>
CORS_ORIGINS=https://your-web.onrender.com
GROQ_API_KEY=
GEMINI_API_KEY=
```

## Environment variables (Web service)

```
NEXT_PUBLIC_API_URL=https://your-api.onrender.com
```

## Render setup

1. Create **Web Service** from repo using `docker/Dockerfile`
2. Start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
3. Add **Background Worker** (or second service) with: `celery -A worker.celery_app worker --loglevel=info`
4. Run release command: `alembic -c migrations/alembic.ini upgrade head && python -m api.seed`
5. Create **Static Site** or Node web service for `apps/web` (`npm run build && npm start`)

See [render.yaml](../../render.yaml) for a starter blueprint.

## Cold start / wake-up

Free Render services spin down after inactivity (~15 min). First request may take **30–60 seconds**.

Demo script:

1. Open web URL → wait for wake-up spinner
2. Login as `analyst@demo.example.com`
3. If empty, admin replays fixtures or re-run seed on deploy

## Health checks

- Liveness: `GET /health`
- Readiness: `GET /ready` (Postgres + Redis)

Configure Render health check path: `/ready`

## Local full stack

```bash
docker compose up -d
pip install -e ".[dev]"
alembic -c migrations/alembic.ini upgrade head
python -m api.seed
cd apps/web && npm install && npm run dev
```

API: http://localhost:8000 · UI: http://localhost:3000
