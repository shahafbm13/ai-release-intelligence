# Phase A Review — MVP Approval Gate

## Status

**MVP approved — Phase B in progress.** Milestone 1 complete.

Draft approved: persona, Option B scope, free-first ($0) constraint, seeded-demo-first, single-org multi-repo.

---

## Final target user

**Primary:** QA Automation Engineer  
**Secondary:** Software Engineer (feedback), Release Manager (release-risk consumer)

## Selected problem

CI failure triage is slow and unstructured; release decisions lack explainable, evidence-backed risk assessment.

## MVP definition

**Option B — Triage + Release Risk MVP**

Single organization, 2–5 repositories, seeded GitHub Actions-shaped events, async processing, AI classification with free LLM chain, deterministic similar-failure retrieval, deterministic release-risk engine, human feedback, minimal Next.js UI, Docker Compose + free-tier cloud deploy.

## Non-goals (confirmed)

Multi-org, incidents, deployments, notifications, auto release gate, pgvector, paid hosting default, Kubernetes, LangGraph/Agents SDK, Temporal.

## Chosen stack

| Layer | Choice |
|-------|--------|
| Backend | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic |
| Worker | Celery + Redis (Upstash free) |
| Database | PostgreSQL (Neon free) |
| AI | Groq → Gemini → rule fallback; Ollama local |
| Frontend | Next.js + TypeScript (minimal) |
| Hosting | Render free tier |
| Cost | **$0/month target** |

## Main architectural decisions

1. Modular monolith + separate worker process (not microservices).
2. Celery over Temporal for MVP.
3. Direct provider adapters (no LangGraph) for single-step classification.
4. No pgvector until baseline retrieval validated.
5. Release-risk fully deterministic — LLM excluded from scoring.
6. JWT + seeded users for demo auth.
7. Immutable AI classifications; feedback stored separately.

See `docs/architecture/decisions/` for ADRs.

## Key risks

- Free-tier LLM rate limits and weaker JSON adherence (mitigated: failover + rule fallback + pre-seeded demo).
- AI misclassification (mitigated: evidence grounding, human feedback, evals).
- Render cold starts (mitigated: demo wake-up script, pre-seeded classifications).
- Scope creep (mitigated: MoSCoW, milestone gates).

## Metrics (instrument at launch)

- **North-star:** median ingest → classification time
- Acceptance / correction rate
- AI fallback rate
- Worker success rate
- Eval pass rate

## Milestones

| # | Focus |
|---|-------|
| M0 | Planning + repo + ADRs |
| M1 | Core backend, DB, auth, org/repo |
| M2 | Webhook/seed ingest, idempotency |
| M3 | Worker, normalization, classification |
| M4 | Similar failures, release-risk, feedback |
| M5 | UI, observability, free-tier deploy |
| M6 | AI evals, docs, case study, portfolio assets |

## Open questions

1. **Repo display name** — keep full "AI Release Intelligence Platform" or shorten for GitHub?
2. **GitHub OAuth** — defer to v1.1 (recommended) or include in MVP?
3. **Co-located worker on Render free tier** — single service running API + Celery worker (recommended for $0) vs separate worker service?

## Recommended first implementation task (M1)

Scaffold monorepo at `ai-release-intelligence/`:

- `apps/api`, `apps/worker`, `apps/web`
- `packages/domain`, `packages/shared`
- Docker Compose: Postgres, Redis, API, worker
- Alembic migration: Organization, User, Repository
- `/health`, `/ready`
- Seed command skeleton
- `.env.example`, README setup section

---

## Approval checklist

- [x] Primary persona and use case approved
- [x] MVP scope (Option B) approved
- [x] Non-goals approved
- [x] Free-first stack approved
- [x] Milestones approved
- [x] Open questions resolved or accepted with defaults

**Approver:** Shahaf  
**Date:** 2026-06-17

---

## Next step after approval

**M6 complete.** MVP delivery finished — eval suite, CI, runbooks, and portfolio assets in `docs/portfolio/`.

Track progress in [docs/delivery/05-milestone-status.md](../delivery/05-milestone-status.md). New contributors: [docs/HANDOFF.md](../HANDOFF.md).
