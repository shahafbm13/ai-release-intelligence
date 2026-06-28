# Functional Requirements

## FR-001 Webhook ingestion

- System SHALL expose POST `/api/v1/webhooks/github`.
- System SHALL verify GitHub HMAC-SHA256 signature when secret configured.
- System SHALL validate payload against versioned Pydantic schema.
- System SHALL persist raw event before enqueueing work.
- System SHALL respond within 10 seconds (GitHub webhook timeout).
- System SHALL support `workflow_run` completed events for MVP.

## FR-002 Idempotency and deduplication

- System SHALL derive idempotency key from GitHub delivery ID and/or workflow run ID.
- System SHALL enforce uniqueness at database level.
- System SHALL return existing resource on duplicate ingest.

## FR-003 CI run management

- System SHALL store CI run: repository, workflow, branch, commit SHA, conclusion, status URL, timestamps.
- System SHALL track processing status: `pending`, `processing`, `completed`, `failed`, `failed_permanent`.
- System SHALL expose paginated list and detail APIs.

## FR-004 Failure normalization

- System SHALL extract per-failure: test_name, suite_name, error_type, error_message, stack_trace, log_excerpt, retry_number.
- System SHALL mask secrets (API keys, tokens, passwords, connection strings) before persistence and AI calls.
- System SHALL compute deterministic normalized fingerprint per failure.

## FR-005 AI classification

- System SHALL produce structured classification per failure (see schema in architecture docs).
- System SHALL use provider adapter with failover: Groq → Gemini → rule-based.
- System SHALL validate output with Pydantic; retry JSON repair up to 2 times.
- System SHALL store full AI metadata and never overwrite original output.
- System SHALL set `insufficient_information=true` when context inadequate.

## FR-006 Similar failure retrieval

- System SHALL implement deterministic matching baseline before any embedding approach.
- System SHALL match on: normalized error message similarity, exact test name, error type, repository filter.
- System SHALL store match method and score per result.

## FR-007 Release-risk engine

- System SHALL compute risk deterministically from documented factors.
- System SHALL NOT use LLM output as risk score.
- System SHALL return risk_level, numeric score, contributing_factors, missing_info, recommendation, explanation.
- System SHALL treat recommendation as advisory only.

## FR-008 Human feedback

- System SHALL allow accept, category correction, component correction, note, resolved flag, cluster link.
- System SHALL preserve original AI classification immutably.
- System SHALL store feedback for evaluation export.

## FR-009 Authentication and authorization

- System SHALL require authentication for all data APIs except health, ready, and webhook (webhook uses signature).
- System SHALL isolate data by organization.
- System SHALL support roles: `viewer`, `analyst`, `admin` (MVP minimum: viewer + analyst).

## FR-010 Dashboard (frontend)

- System SHALL provide UI for: CI runs list, failed run detail, classification/evidence, similar failures, release-risk, feedback form, basic metrics.
- UI SHALL call versioned REST API only.

## FR-011 Seed and demo

- System SHALL provide seed command with demo users, org, repos, CI runs, failures.
- System SHALL document demo credentials and wake-up procedure for free-tier hosting.

## FR-012 Audit logging

- System SHOULD record audit events for webhook ingest, classification completion, feedback submission.

## FR-013 Metrics API

- System SHOULD expose `/api/v1/metrics/summary` with computed operational and AI quality metrics.

## Classification categories (MVP)

- product_defect
- test_defect
- environment_issue
- infrastructure_issue
- authentication_issue
- data_issue
- timeout
- network_issue
- flaky_intermittent
- unknown

## API versioning

- All public REST routes SHALL be under `/api/v1/`.
- Breaking changes SHALL increment version.

## Out of scope (MVP)

- Multi-org provisioning UI
- Slack notifications
- Deployment/incident ingestion
- Automatic release blocking
- pgvector semantic search
