# Handoff Guide

**Start here** if you are new to the project, returning after a break, or taking over from someone else.

Living progress (milestones + backlog checkboxes): [docs/delivery/05-milestone-status.md](./delivery/05-milestone-status.md).

---

## 60-second orientation

**AI Release Intelligence Platform** ingests CI failure signals, classifies failures with a free LLM chain (Groq → Gemini → rules), finds similar historical failures, computes a deterministic release-risk score, and captures human feedback.

| Item | Current state |
|------|---------------|
| Phase | Phase B — M6 complete |
| Milestone | Portfolio package ready |
| Code | Full stack: API + worker + Next.js UI |
| Cost target | $0 (free APIs + free hosting tiers) |

---

## Read order (~15 minutes)

1. [README.md](../README.md) — setup and API endpoints
2. [docs/product/14-phase-a-review.md](./product/14-phase-a-review.md) — MVP scope, stack, non-goals
3. [docs/delivery/05-milestone-status.md](./delivery/05-milestone-status.md) — **where we are now**
4. [docs/delivery/02-milestones.md](./delivery/02-milestones.md) — M4 milestone details
5. [docs/architecture/08-ai-architecture.md](./architecture/08-ai-architecture.md) — classification pipeline
6. [docs/product/11-api-consumer-contract.md](./product/11-api-consumer-contract.md) — webhook contract

---

## Current focus

**Goal:** M6 complete — eval suite, CI, runbooks, portfolio assets.

**Delivered in M6:**

- BL-050 Eval dataset v1 (10 cases) — `tests/evals/data/v1/cases.json`
- BL-051 Eval report generator — `python tests/evals/runner.py`
- BL-052 GitHub Actions CI — `.github/workflows/ci.yml`
- BL-053 E2E critical path — `tests/e2e/test_critical_path.py`
- BL-054 Runbooks — `docs/runbooks/`
- BL-055 Case study + CV bullets — `docs/portfolio/`
- BL-056 Demo script — `docs/portfolio/demo-script.md`

**Optional next (v1+):** BL-100 real GitHub webhook, BL-103 pgvector experiment.

---

## How to run

```bash
cp .env.example .env
docker compose up -d postgres redis
pip install -e ".[dev]"
alembic -c migrations/alembic.ini upgrade head
python -m api.seed
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Worker (second terminal):

```bash
celery -A worker.celery_app worker --loglevel=info
```

**Demo login:** `analyst@demo.example.com` / `demo-pass-1`

**Verify:** `pytest tests/ -v` · `make eval` · `make eval-report`

**M4 quick demo:**

```bash
POST /api/v1/admin/seed/replay                              # ingest run 1
POST /api/v1/admin/seed/replay                              # ingest run 2
GET  /api/v1/failures/{id}/similar                          # similar history
GET  /api/v1/ci-runs/{id}/assessment                        # release risk
POST /api/v1/failures/{id}/feedback                         # accept/correct
```

---

## Environment checklist

Store values locally or in platform dashboards — **never commit secrets**.

| Variable | Required when | Notes |
|----------|---------------|-------|
| `DATABASE_URL` | M1+ | See `.env.example` |
| `REDIS_URL` | M1+ | Local Docker or Upstash |
| `JWT_SECRET` | M1+ | Random string for signing |
| `GROQ_API_KEY` | M3+ | Free tier primary LLM |
| `GEMINI_API_KEY` | M3+ | Free tier fallback LLM |
| `GITHUB_WEBHOOK_SECRET` | M2+ | HMAC verification |
| `RENDER_*` / deploy vars | M5 | Production deploy |

---

## Open questions

| Question | Status | Default |
|----------|--------|---------|
| Repo display name — full or shortened? | Open | Keep descriptive full name |
| GitHub OAuth in MVP or v1.1? | Resolved | Defer to v1.1 |
| Co-locate API + worker on Render free tier? | Resolved | Yes, single service for $0 |

---

## Blockers and risks

### Current blockers

- None for M5.

### Active risks

See [08-risk-register.md](./product/08-risk-register.md). Note for M2: GitHub native webhook lacks test failure details — use `test_failures` enrichment in fixtures (TD-002).

---

## Before you stop working

1. [docs/delivery/05-milestone-status.md](./delivery/05-milestone-status.md) — milestone status, BL checkboxes, session log
2. This file — **Current focus** and **Blockers**
3. [README.md](../README.md) — **Status** if phase/milestone changed
4. Milestone complete: verify exit criteria against [04-definition-of-done.md](./delivery/04-definition-of-done.md)

---

## Handoff to another person

Send them:

1. Link to this file (`docs/HANDOFF.md`)
2. Link to [05-milestone-status.md](./delivery/05-milestone-status.md)
3. Branch name (`main`)
4. Confirm Docker is running for tests
5. Optional: demo login walkthrough at http://localhost:8000/docs

---

## Maintenance rules

| Event | Action |
|-------|--------|
| End of session | Update 05 + HANDOFF current focus + session log |
| Milestone start | Set milestone In progress; note branch in 05 snapshot |
| Milestone done | Mark Done; check exit criteria; update README |
| Blocker appears/resolves | Update Blockers section here |
| New backlog item | Add to 03-backlog.md, then checkbox in 05 |
