# Backlog

**Implementation status (checkboxes) tracked in [05-milestone-status.md](./05-milestone-status.md).** This file defines backlog items; do not duplicate checkboxes here.

## Priority legend

- **P0** — MVP must-have
- **P1** — MVP should-have
- **P2** — Could-have / v1
- **P3** — Future

## Epic: Foundation (M1)

| ID | Story | Priority | Milestone |
|----|-------|----------|-----------|
| BL-001 | Scaffold monorepo structure | P0 | M1 |
| BL-002 | Docker Compose local stack | P0 | M1 |
| BL-003 | Alembic org/user/repo migrations | P0 | M1 |
| BL-004 | JWT auth login/register | P0 | M1 |
| BL-005 | Org isolation middleware | P0 | M1 |
| BL-006 | Health and readiness endpoints | P0 | M1 |

## Epic: Ingestion (M2)

| ID | Story | Priority | Milestone |
|----|-------|----------|-----------|
| BL-010 | GitHub webhook endpoint | P0 | M2 |
| BL-011 | HMAC signature verification | P0 | M2 |
| BL-012 | Idempotency on delivery_id | P0 | M2 |
| BL-013 | Webhook contract tests | P0 | M2 |
| BL-014 | Seed replay command | P0 | M2 |
| BL-015 | Audit log webhook events | P1 | M2 |

## Epic: Processing (M3)

| ID | Story | Priority | Milestone |
|----|-------|----------|-----------|
| BL-020 | Celery process_ci_run task | P0 | M3 |
| BL-021 | Failure normalization service | P0 | M3 |
| BL-022 | Secret masking pipeline | P0 | M3 |
| BL-023 | Groq adapter | P0 | M3 |
| BL-024 | Gemini fallback adapter | P0 | M3 |
| BL-025 | Rule-based fallback classifier | P0 | M3 |
| BL-026 | JSON repair retry logic | P0 | M3 |
| BL-027 | Classification persistence | P0 | M3 |

## Epic: Intelligence (M4)

| ID | Story | Priority | Milestone |
|----|-------|----------|-----------|
| BL-030 | Similar failure baseline matcher | P0 | M4 |
| BL-031 | Release-risk engine v1 | P0 | M4 |
| BL-032 | Risk engine unit tests (golden) | P0 | M4 |
| BL-033 | Feedback API | P0 | M4 |
| BL-034 | Immutable AI record enforcement | P0 | M4 |

## Epic: UI and deploy (M5)

| ID | Story | Priority | Milestone |
|----|-------|----------|-----------|
| BL-040 | CI runs list page | P0 | M5 |
| BL-041 | Failure detail + classification view | P0 | M5 |
| BL-042 | Similar failures panel | P0 | M5 |
| BL-043 | Release-risk panel | P0 | M5 |
| BL-044 | Feedback form | P0 | M5 |
| BL-045 | Metrics summary page | P1 | M5 |
| BL-046 | Render/Neon/Upstash deploy | P0 | M5 |
| BL-047 | Demo seed data (5+ scenarios) | P0 | M5 |

## Epic: Quality and portfolio (M6)

| ID | Story | Priority | Milestone |
|----|-------|----------|-----------|
| BL-050 | Eval dataset v1 (10 cases) | P0 | M6 |
| BL-051 | Eval report generator | P0 | M6 |
| BL-052 | GitHub Actions CI | P0 | M6 |
| BL-053 | E2E critical path test | P0 | M6 |
| BL-054 | Runbooks | P1 | M6 |
| BL-055 | Case study + CV bullets | P0 | M6 |
| BL-056 | Demo script with cold start | P0 | M6 |

## Epic: v1 (post-MVP)

| ID | Story | Priority | Milestone |
|----|-------|----------|-----------|
| BL-100 | Real GitHub webhook on demo repo | P2 | v1 |
| BL-101 | GitHub OAuth | P2 | v1 |
| BL-102 | OpenAI adapter (optional paid) | P2 | v1 |
| BL-103 | pgvector semantic retrieval experiment | P2 | v1 |
| BL-104 | Slack notification spike | P3 | v2 |

## Technical debt register

| ID | Item | Notes |
|----|------|-------|
| TD-001 | Co-located API+worker on Render | Accept for $0; split if scaling |
| TD-002 | test_failures enrichment in webhook | Until artifact parser built |
| TD-003 | Critical test detection via naming convention | Replace with metadata later |
