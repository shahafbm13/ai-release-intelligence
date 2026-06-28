# Runbook: Database outage

## Symptoms

- `/ready` returns 503 or database check fails.
- API errors on login, CI runs, or webhook ingest.
- Alembic migrations fail to connect.

## Quick checks

1. **Local:** `docker compose ps` — Postgres container healthy?
2. **Connection string:** `DATABASE_URL` host, port, user, password, database name.
3. **Neon/serverless:** Cold start or suspend — first request may be slow.

## Resolution steps

1. Restart Postgres: `docker compose up -d postgres`
2. Verify connectivity:
   ```bash
   alembic -c migrations/alembic.ini current
   ```
3. If schema drift: `alembic -c migrations/alembic.ini upgrade head`
4. Integration tests reset schema — do not run test reset against production.

## Data recovery

- MVP has no automated backup on free tier. Export important demo data before destructive operations.
- Re-seed demo: `python -m api.seed`

## Escalation

- Check Neon/Render status pages for managed Postgres.
- Review migration history in `migrations/versions/`.
