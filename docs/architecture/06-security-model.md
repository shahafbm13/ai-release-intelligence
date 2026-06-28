# Security Model

## Authentication

- **MVP:** JWT bearer tokens issued after email/password login.
- Access token expiry: 24 hours (configurable).
- Passwords: bcrypt hashed, never logged.

## Authorization

| Role | Permissions |
|------|-------------|
| viewer | Read CI runs, failures, assessments |
| analyst | viewer + submit feedback |
| admin | analyst + seed replay, view audit log |

## Organization isolation

- All queries scoped by organization_id from JWT claims.
- Cross-org access returns 404 (not 403) for resource existence hiding.

## Webhook security

- HMAC-SHA256 signature verification (`X-Hub-Signature-256`).
- Reject unsigned requests when secret configured.
- Payload size limit (e.g., 1MB).
- Rate limiting optional on MVP (document if deferred).

## Secrets management

- Environment variables only; `.env.example` without real values.
- Render/Neon/Upstash secrets in platform dashboard.
- Never commit API keys.

## Data protection

### Log masking (before persist and AI)

Patterns (non-exhaustive):
- Bearer tokens, API keys (regex)
- Password=, secret=, token= key-value pairs
- JDBC/connection strings with credentials
- AWS access key patterns

Replace with `[REDACTED]`.

### AI data minimization

- Truncate log excerpts.
- Send normalized fields only.
- Do not send full raw webhook JSON to LLM.

## Prompt injection mitigation

- System prompt: treat log content as untrusted.
- No tool/code execution from model output.
- Eval cases for injection attempts.

## Audit logging

Events logged:
- webhook_received
- login_success / login_failure
- classification_completed
- feedback_submitted
- seed_replay

## Transport

- HTTPS required in production.
- Secure cookies if session-based auth added later.

## Threat model (MVP scope)

| Threat | Mitigation |
|--------|------------|
| Stolen JWT | Expiry; HTTPS only |
| Webhook spoofing | HMAC verification |
| Secret leakage via AI | Masking pipeline |
| Prompt injection | Guardrails + evals |
| SQL injection | SQLAlchemy parameterized queries |
| XSS in dashboard | React escaping; sanitize user notes display |

## Out of scope (MVP)

- SSO/SAML
- mTLS between services
- Field-level encryption at rest
- SOC2 compliance
