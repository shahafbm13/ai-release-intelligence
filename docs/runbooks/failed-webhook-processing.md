# Runbook: Failed webhook processing

## Symptoms

- GitHub (or seed replay) delivery succeeds but no CI run appears in the dashboard.
- `POST /api/v1/webhooks/github` returns 401, 400, or 500.
- `ingested_events` table has no recent rows.

## Quick checks

1. **Signature:** Verify `GITHUB_WEBHOOK_SECRET` matches the sender. Local fixtures use `test-webhook-secret` in tests; production must match GitHub webhook settings.
2. **Payload shape:** Handler expects `workflow_run` events with optional `test_failures` enrichment (see TD-002). Malformed JSON returns 400.
3. **API logs:** Search for `webhook_signature_invalid`, `webhook_payload_invalid`, or `ingest_failed`.
4. **Database:** Confirm `/ready` returns 200. Ingest requires PostgreSQL.

## Resolution steps

1. Replay a known-good fixture via admin replay (requires admin JWT):
   `POST /api/v1/admin/seed/replay?fixture_name=failed_run.json`
2. If replay works but live webhooks fail, compare HMAC secret and delivery headers (`X-GitHub-Delivery`, `X-Hub-Signature-256`).
3. Check idempotency: duplicate `X-GitHub-Delivery` returns 200 with existing run — not a failure.
4. Restart API service after env var changes.

## Escalation

- Review contract tests: `pytest tests/contract -v`
- Inspect payload against [API consumer contract](../product/11-api-consumer-contract.md)
