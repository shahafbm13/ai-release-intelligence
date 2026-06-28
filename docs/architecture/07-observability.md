# Observability

## Logging

- **Format:** Structured JSON via structlog.
- **Required fields:** timestamp, level, message, correlation_id, service (api|worker).
- **Optional context:** ci_run_id, failure_id, task_id, user_id, provider.

## Correlation IDs

- Generated at webhook/seed ingest.
- Propagated: API → Celery → classification → audit.
- Returned in API responses and errors.

## Metrics (in-app / metrics endpoint)

| Metric | Type | Description |
|--------|------|-------------|
| webhook_ingest_total | counter | Ingest attempts by status |
| worker_task_duration_seconds | histogram | Task processing time |
| classification_duration_seconds | histogram | Per-failure AI time |
| classification_fallback_total | counter | By provider used |
| worker_task_failures_total | counter | Permanent failures |
| feedback_total | counter | accept vs correct |

Expose summary via `/api/v1/metrics/summary` aggregating from DB + in-memory counters.

## Health checks

- `GET /health` — process alive (200).
- `GET /ready` — DB ping + Redis ping (200/503).

## Error tracking

- Sentry optional (paid); MVP uses structured error logs.
- Log level ERROR for permanent task failures.

## AI tracing

Per classification record store:
- provider, model, prompt_version
- input_hash, input_tokens, output_tokens
- duration_ms, trace_id (correlation_id or UUID)

## Cost tracking

- `estimated_cost_usd = 0` for free tier.
- Token counts stored for quota monitoring.

## Dashboards

- MVP: metrics summary page in Next.js + README queries.
- No Grafana in MVP.

## Runbooks

See `docs/runbooks/` (created in Phase B):
- Failed webhook processing
- Worker backlog
- AI provider outage
- Database outage
- Incorrect release-risk result

## Alerting

- MVP: manual monitoring via metrics API and logs.
- No PagerDuty integration.
