# Milestones

**Live status (dates, checkboxes, session log):** [05-milestone-status.md](./05-milestone-status.md)

## Milestone 0: Product planning and repository setup

**Goal:** Complete Phase A artifacts and architecture decisions.

**Deliverables:**
- All docs under `docs/product/`, `docs/architecture/`, `docs/delivery/`
- 10 ADRs
- Phase A review document

**Dependencies:** None

**Risks:** Scope creep in documentation

**Exit criteria:**
- PRD, requirements, metrics, risks complete
- MVP scope explicitly bounded
- User approval on phase-a-review

**Demo scenario:** Walk through documentation and architecture diagrams.

---

## Milestone 1: Core backend, database, authentication

**Goal:** Runnable API with org/user/repo model and auth.

**Deliverables:**
- Monorepo scaffold
- Docker Compose (Postgres, Redis, API, worker)
- Alembic migrations for core entities
- JWT auth endpoints
- `/health`, `/ready`
- Seed command skeleton

**Dependencies:** M0 approval

**Risks:** Over-engineering auth

**Exit criteria:**
- Login works; protected routes enforce org isolation
- Migrations run clean
- Integration tests for auth pass

**Demo scenario:** Create org and repos via API; login as demo user.

---

## Milestone 2: Webhook ingestion and CI-run persistence

**Goal:** Secure, idempotent event ingest.

**Deliverables:**
- POST `/api/v1/webhooks/github`
- Signature verification
- Idempotency via delivery_id
- IngestedEvent + CIRun persistence
- Celery enqueue
- Contract tests with fixtures

**Dependencies:** M1

**Risks:** GitHub payload lacks test details — use enrichment field

**Exit criteria:**
- Replay fixture → single CI run
- Duplicate delivery → no duplicate run
- US-001, US-002 acceptance criteria met

**Demo scenario:** Replay seed fixture; show CI run in DB/API.

---

## Milestone 3: Background processing and classification

**Goal:** Failed runs processed; failures classified.

**Deliverables:**
- `process_ci_run` Celery task
- Normalization + secret masking
- Groq/Gemini/rule adapter chain
- Classification persistence
- Worker integration tests

**Dependencies:** M2, Groq/Gemini API keys

**Risks:** Free LLM JSON reliability

**Exit criteria:**
- Failed run → classifications for all failures
- Fallback chain demonstrated in tests
- US-005 acceptance criteria met

**Demo scenario:** Process failed run; show classifications via API.

---

## Milestone 4: Similar failures, release-risk, feedback

**Goal:** Complete intelligence loop.

**Deliverables:**
- Deterministic similar-failure retrieval
- Release-risk engine with tests
- Feedback API with immutable AI records
- Audit events for feedback

**Dependencies:** M3

**Risks:** Risk formula tuning

**Exit criteria:**
- US-006, US-007, US-008 acceptance criteria met
- Golden tests for risk engine pass

**Demo scenario:** Review similar failures and release-risk; submit correction.

---

## Milestone 5: Minimal dashboard, observability, deployment

**Goal:** Public demo URL with UI.

**Deliverables:**
- Next.js screens (7 core views)
- Metrics summary API + UI
- Structured logging + correlation IDs
- Render + Neon + Upstash deploy
- Demo wake-up documentation

**Dependencies:** M4

**Risks:** Render cold start; free tier limits

**Exit criteria:**
- Full journey in browser on public URL
- US-003, US-004, US-010 met
- `/ready` passes in production

**Demo scenario:** Wake URL → login → triage failed run → feedback.

---

## Milestone 6: AI evaluation, documentation, portfolio assets

**Goal:** Portfolio-ready package.

**Deliverables:**
- 10-case eval dataset + report generator
- README, CONTRIBUTING, runbooks
- Case study, CV bullets, interview stories, demo script
- GitHub Actions CI pipeline

**Dependencies:** M5

**Risks:** Eval pass rate below target on free models

**Exit criteria:**
- CI green on main
- Eval report generated
- Case study complete without invented metrics

**Demo scenario:** Run eval report; present portfolio narrative.
