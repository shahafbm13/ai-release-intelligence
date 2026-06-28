# Non-Functional Requirements

## NFR-001 Performance

| Requirement | Target |
|-------------|--------|
| Webhook ACK latency | < 2s p95 (warm); cold start excluded |
| Worker: ingest to classified | < 60s p95 for 3 failures (free LLM) |
| API read endpoints | < 500ms p95 (warm) |
| Dashboard initial load | < 3s on broadband (warm) |

## NFR-002 Availability

- MVP targets **best-effort** on free tier; no SLA claimed.
- Health (`/health`) and readiness (`/ready`) endpoints required.
- System SHALL degrade gracefully: rule-based classification when LLM unavailable.

## NFR-003 Scalability

- MVP designed for 1 org, 5 repos, ~100 CI runs/month.
- Architecture SHALL support horizontal worker scaling without code redesign.
- No requirement for multi-region in MVP.

## NFR-004 Security

- Secrets SHALL NOT be stored in source control.
- CI log content SHALL be masked before AI transmission.
- Webhook signatures SHALL be verified in production.
- JWT tokens SHALL expire (e.g., 24h access token).
- Passwords SHALL be bcrypt-hashed.
- All user input SHALL be validated server-side.
- Logs treated as untrusted (prompt injection mitigation).

## NFR-005 Reliability

- Worker tasks SHALL be idempotent.
- Failed tasks SHALL retry with exponential backoff (max 3 retries).
- Permanent failures SHALL move to `failed_permanent` with error recorded.
- Database migrations SHALL be reversible where practical.

## NFR-006 Observability

- Structured JSON logging required.
- Correlation ID propagated: webhook → task → classification.
- Metrics: ingest count, processing duration, AI latency, fallback rate, error rate.
- AI calls logged with provider, model, tokens, duration (cost=0 for free tier).

## NFR-007 Maintainability

- Modular monolith with separated layers (routes, services, domain, repositories).
- Business logic SHALL NOT live in route handlers.
- ADRs for major decisions.
- Test coverage on domain rules, risk engine, normalization, auth.

## NFR-008 Cost

- **Hard constraint:** $0 monthly operating cost for MVP demo stack.
- Free-tier limits documented in README and demo script.

## NFR-009 Compatibility

- Python 3.12+
- PostgreSQL 15+
- Redis 7+ (Upstash compatible)
- Modern evergreen browsers for dashboard

## NFR-010 Data retention

- MVP: retain all seeded and ingested data indefinitely within free-tier DB limits.
- Soft delete not required for MVP entities.

## NFR-011 Accessibility

- Dashboard: semantic HTML, keyboard-navigable forms (basic, not WCAG audit target for MVP).

## NFR-012 Compliance

- No PII beyond user email/name for demo accounts.
- README documents that CI logs may contain sensitive data and masking is best-effort.

## NFR-013 Testing

- Unit tests for domain and risk engine.
- Integration tests for API + DB + worker.
- Contract tests for webhook fixtures and AI response schema.
- E2E test for critical flow.
- AI eval suite with 10 synthetic cases (mocked in CI; optional live run manual).

## NFR-014 Documentation

- README with setup, architecture summary, demo instructions.
- OpenAPI spec auto-generated from FastAPI.
- Runbooks for common failures.
