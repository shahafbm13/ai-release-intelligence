# Runbook: Worker backlog

## Symptoms

- CI runs show `processing_status: pending` for more than a few minutes.
- Failure list empty; release assessment unavailable.
- Celery queue depth growing (Redis `LLEN` on broker keys).

## Quick checks

1. **Worker running:** Local dev requires a second terminal:
   `celery -A worker.celery_app worker --loglevel=info`
2. **Redis reachable:** Worker and API share `CELERY_BROKER_URL`.
3. **Admin replay:** Since M6, admin replay processes synchronously; webhook ingest still enqueues Celery.

## Resolution steps

1. Start or restart the Celery worker.
2. Process stuck runs without worker:
   ```bash
   cd apps/api
   python -m api.process_pending
   ```
3. On Render free tier (TD-001): API and worker may co-locate — confirm worker process is in start command or use synchronous processing for demo.
4. Verify runs transition to `completed` and failures appear:
   `GET /api/v1/ci-runs/{id}`

## Prevention

- Include worker in production deploy or document synchronous backfill for demos.
- Monitor `processing_status=pending` count via metrics summary API.
