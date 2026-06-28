# API Consumer Contract

## Purpose

Describe the external event input and public API expectations without binding internal implementation.

## Webhook: GitHub Actions workflow run

### Endpoint

`POST /api/v1/webhooks/github`

### Authentication

- Header: `X-Hub-Signature-256: sha256=<hex>`
- HMAC-SHA256 of raw body using configured webhook secret.
- Header: `X-GitHub-Delivery: <uuid>` (used for idempotency)

### Supported events (MVP)

- `workflow_run` with action `completed`

### Expected payload shape (simplified)

```json
{
  "action": "completed",
  "workflow_run": {
    "id": 123456789,
    "name": "CI",
    "head_branch": "main",
    "head_sha": "abc123def456",
    "conclusion": "failure",
    "html_url": "https://github.com/org/repo/actions/runs/123456789",
    "repository": {
      "full_name": "org/checkout-service"
    },
    "created_at": "2026-06-17T10:00:00Z",
    "updated_at": "2026-06-17T10:12:00Z"
  },
  "repository": {
    "full_name": "org/checkout-service"
  },
  "test_failures": [
    {
      "test_name": "test_checkout_applies_discount",
      "suite_name": "tests.e2e.checkout",
      "error_type": "AssertionError",
      "error_message": "Expected total 90.0 but got 100.0",
      "stack_trace": "...",
      "log_excerpt": "...",
      "retry_number": 0
    }
  ]
}
```

**Note:** `test_failures` may be supplied via platform-specific enrichment (seed fixture or future artifact parser). GitHub native webhook does not include test details — document enrichment path.

### Responses

| Status | Meaning |
|--------|---------|
| 202 | Accepted; processing enqueued |
| 200 | Duplicate; existing run returned |
| 401 | Invalid signature |
| 422 | Schema validation failed |
| 500 | Internal error (retry by sender) |

### Response body (202)

```json
{
  "ci_run_id": "uuid",
  "correlation_id": "uuid",
  "status": "accepted"
}
```

---

## Seed ingest (demo)

### Endpoint

`POST /api/v1/admin/seed/replay` (authenticated admin, MVP demo only)

Replays fixture file through same pipeline as webhook. Not required for production GitHub integration.

---

## Public read APIs (authenticated)

### CI runs

- `GET /api/v1/ci-runs?page=1&page_size=20&conclusion=failure&repository_id=`
- `GET /api/v1/ci-runs/{id}`

### Failures

- `GET /api/v1/failures?ci_run_id=`
- `GET /api/v1/failures/{id}`

### Classification trigger (optional manual re-run)

- `POST /api/v1/failures/{id}/classify`

### Feedback

- `POST /api/v1/failures/{id}/feedback`

```json
{
  "action": "correct",
  "corrected_category": "test_defect",
  "corrected_component": "page-objects",
  "note": "Selector changed in PR #42",
  "resolved": false,
  "cluster_id": null
}
```

### Release assessment

- `GET /api/v1/ci-runs/{id}/assessment`

### Metrics

- `GET /api/v1/metrics/summary`

---

## Error format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human readable message",
    "details": []
  },
  "correlation_id": "uuid"
}
```

---

## Pagination

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 100
}
```

---

## Versioning

- Base path `/api/v1/`
- Breaking changes increment major version

---

## Consumer obligations

- GitHub webhook must use HTTPS in production.
- Consumers must not include secrets in test failure messages when avoidable.
- Demo consumers should tolerate 30–60s cold start on free hosting.
