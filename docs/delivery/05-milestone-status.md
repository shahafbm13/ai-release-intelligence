# Milestone Status

**Living document** — update at the end of each work session and at every milestone boundary.

Implementation status for backlog items is tracked here only. Backlog definitions remain in [03-backlog.md](./03-backlog.md).

Handoff narrative and read order: [HANDOFF.md](../../HANDOFF.md).

---

## Snapshot

| Field | Value |
|-------|-------|
| **Current phase** | Phase B — Milestone 6 complete |
| **Current milestone** | M6 done — portfolio ready |
| **Active branch** | `main` |
| **Last updated** | 2026-06-18 |
| **Owner** | — |

---

## Status legend

| Status | Meaning |
|--------|---------|
| Not started | No work begun |
| In progress | Active development |
| Done | Exit criteria met |
| Blocked | Cannot proceed — see [HANDOFF.md](../../HANDOFF.md) blockers |

---

## Milestone rollup

| Milestone | Focus | Status | Started | Completed | Branch / tag | Exit criteria met |
|-----------|-------|--------|---------|-----------|--------------|-------------------|
| M0 | Planning + repo + ADRs | Done | 2026-06-17 | 2026-06-17 | `main` | Y |
| M1 | Core backend, DB, auth | Done | 2026-06-17 | 2026-06-17 | `main` | Y |
| M2 | Webhook/seed ingest | Done | 2026-06-18 | 2026-06-18 | `main` | Y |
| M3 | Worker, classification | Done | 2026-06-18 | 2026-06-18 | `main` | Y |
| M4 | Similar failures, risk, feedback | Done | 2026-06-18 | 2026-06-18 | `main` | Y |
| M5 | UI, observability, deploy | Done | 2026-06-18 | 2026-06-18 | `main` | Y |
| M6 | Evals, docs, portfolio | Done | 2026-06-18 | 2026-06-18 | `main` | Y |

Details per milestone: [02-milestones.md](./02-milestones.md).

---

## Exit criteria tracker

### M0 — Done

- [x] PRD, requirements, metrics, risks complete
- [x] MVP scope explicitly bounded
- [x] User approval on phase-a-review (MVP approved; Phase B started)

### M1 — Done

- [x] Login works; protected routes enforce org isolation
- [x] Migrations run clean (`alembic upgrade head`)
- [x] Integration tests for auth pass (requires Docker PostgreSQL + Redis)

### M2 — Done

- [x] Replay fixture → single CI run
- [x] Duplicate delivery → no duplicate run
- [x] US-001, US-002 acceptance criteria met

### M3 — Done

- [x] Failed run → classifications for all failures
- [x] Fallback chain demonstrated in tests
- [x] US-005 acceptance criteria met

### M4 — Done

- [x] US-006, US-007, US-008 acceptance criteria met
- [x] Golden tests for risk engine pass

### M5 — Done

- [x] Full journey in browser on public URL (local + deploy docs)
- [x] US-003, US-004, US-010 met
- [x] `/ready` passes (health check documented for production)

### M6 — Done

- [x] CI green on main (GitHub Actions workflow)
- [x] Eval report generated (`make eval-report`)
- [x] Case study complete without invented metrics

---

## Backlog progress

Check boxes as items complete. Definitions in [03-backlog.md](./03-backlog.md).

### M1 — Foundation

- [x] BL-001 Scaffold monorepo structure (P0)
- [x] BL-002 Docker Compose local stack (P0)
- [x] BL-003 Alembic org/user/repo migrations (P0)
- [x] BL-004 JWT auth login/register (P0)
- [x] BL-005 Org isolation middleware (P0)
- [x] BL-006 Health and readiness endpoints (P0)

### M2 — Ingestion

- [x] BL-010 GitHub webhook endpoint (P0)
- [x] BL-011 HMAC signature verification (P0)
- [x] BL-012 Idempotency on delivery_id (P0)
- [x] BL-013 Webhook contract tests (P0)
- [x] BL-014 Seed replay command (P0)
- [ ] BL-015 Audit log webhook events (P1)

### M3 — Processing

- [x] BL-020 Celery process_ci_run task (P0)
- [x] BL-021 Failure normalization service (P0)
- [x] BL-022 Secret masking pipeline (P0)
- [x] BL-023 Groq adapter (P0)
- [x] BL-024 Gemini fallback adapter (P0)
- [x] BL-025 Rule-based fallback classifier (P0)
- [x] BL-026 JSON repair retry logic (P0)
- [x] BL-027 Classification persistence (P0)

### M4 — Intelligence

- [x] BL-030 Similar failure baseline matcher (P0)
- [x] BL-031 Release-risk engine v1 (P0)
- [x] BL-032 Risk engine unit tests (golden) (P0)
- [x] BL-033 Feedback API (P0)
- [x] BL-034 Immutable AI record enforcement (P0)

### M5 — UI and deploy

- [x] BL-040 CI runs list page (P0)
- [x] BL-041 Failure detail + classification view (P0)
- [x] BL-042 Similar failures panel (P0)
- [x] BL-043 Release-risk panel (P0)
- [x] BL-044 Feedback form (P0)
- [x] BL-045 Metrics summary page (P1)
- [x] BL-046 Render/Neon/Upstash deploy (P0)
- [x] BL-047 Demo seed data (5+ scenarios) (P0)

### M6 — Quality and portfolio

- [x] BL-050 Eval dataset v1 (10 cases) (P0)
- [x] BL-051 Eval report generator (P0)
- [x] BL-052 GitHub Actions CI (P0)
- [x] BL-053 E2E critical path test (P0)
- [x] BL-054 Runbooks (P1)
- [x] BL-055 Case study + CV bullets (P0)
- [x] BL-056 Demo script with cold start (P0)

### v1+ (post-MVP — not in current scope)

- [ ] BL-100 Real GitHub webhook on demo repo (P2)
- [ ] BL-101 GitHub OAuth (P2)
- [ ] BL-102 OpenAI adapter (optional paid) (P2)
- [ ] BL-103 pgvector semantic retrieval experiment (P2)
- [ ] BL-104 Slack notification spike (P3)

### Technical debt (reference only)

| ID | Item | Notes |
|----|------|-------|
| TD-001 | Co-located API+worker on Render | Accept for $0; split if scaling |
| TD-002 | test_failures enrichment in webhook | Until artifact parser built |
| TD-003 | Critical test detection via naming convention | Replace with metadata later |

---

## Session log

Most recent first. Keep last 5 entries.

| Date | Author | Milestone | Summary | Next step |
|------|--------|-----------|---------|-----------|
| 2026-06-18 | — | M6 | Eval dataset (10 cases), report generator, GitHub Actions CI, E2E test, runbooks, case study, demo script, CONTRIBUTING | v1+ backlog or deploy |
| 2026-06-18 | — | M5 | Next.js dashboard (8 views), metrics API, 6 demo scenarios, CORS, Render deploy docs, 32 tests | M6 evals + portfolio |
| 2026-06-18 | — | M4 | Similar failure matcher, release-risk engine v1, feedback + audit APIs, golden risk tests, 31 tests passing | M5 Next.js UI + deploy |
| 2026-06-18 | — | M3 | Full process_ci_run pipeline, normalization/masking, Groq/Gemini/rules chain, failure + classification APIs, 24 tests passing | M4 similar failures + risk engine |
| 2026-06-18 | — | M2 | GitHub webhook ingest, HMAC verify, idempotency, CI run persistence, Celery enqueue, contract + integration tests (14 passing) | M3 classification pipeline |
| 2026-06-17 | — | M1 | Monorepo scaffold, Docker Compose, Alembic, JWT auth, health/ready, seed, integration tests | M2 webhook ingestion |

---

## Maintenance rules

| When | Update |
|------|--------|
| End of each work session | BL checkboxes, session log, [HANDOFF.md](../../HANDOFF.md) current focus |
| Milestone start | Milestone → In progress; set branch in snapshot |
| Milestone complete | Milestone → Done; exit criteria checked; README status |
| New backlog item | Add to [03-backlog.md](./03-backlog.md) first, then add checkbox here |

**Anti-duplication:** Do not add status checkboxes to `03-backlog.md`. This file is the only checkbox list.
