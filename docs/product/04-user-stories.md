# User Stories

## Story index

| ID | Title | Priority |
|----|-------|----------|
| US-001 | Ingest CI failure event | Must |
| US-002 | Idempotent webhook handling | Must |
| US-003 | View CI runs | Must |
| US-004 | View failure details | Must |
| US-005 | AI classify failure | Must |
| US-006 | View similar failures | Must |
| US-007 | View release-risk assessment | Must |
| US-008 | Submit classification feedback | Must |
| US-009 | Authenticate and isolate org data | Must |
| US-010 | Replay seed demo data | Must |
| US-011 | View operational metrics | Should |
| US-012 | Audit important actions | Should |

---

## US-001: Ingest CI failure event

**Persona:** System (GitHub Actions / seed script)  
**Story:** As the platform, I want to accept a CI workflow failure payload so that failed runs enter the processing pipeline.

**Business value:** Entry point for all downstream intelligence.

**Priority:** Must  
**Dependencies:** None

**Acceptance criteria:**
- POST `/api/v1/webhooks/github` accepts valid GitHub-shaped payload.
- Valid payload returns 202 with `correlation_id` and `ci_run_id`.
- Invalid schema returns 422 with structured error body.
- Invalid signature returns 401.
- Processing task enqueued within 500ms of request (excluding cold start).

**Edge cases:**
- Unknown event type → 202 with status `ignored` and audit note.
- Payload missing test failures → run stored with zero failures; assessment reflects missing data.

**Metric:** Webhook ingest success rate.

---

## US-002: Idempotent webhook handling

**Persona:** Platform operator  
**Story:** As an operator, I want duplicate webhook deliveries deduplicated so that the same run is not processed twice.

**Business value:** Prevents duplicate classifications and inflated costs/quota usage.

**Priority:** Must  
**Dependencies:** US-001

**Acceptance criteria:**
- Same delivery ID processed once only.
- Replay returns 200/202 with same `ci_run_id`.
- Idempotency enforced at DB unique constraint level.

**Edge cases:**
- Concurrent duplicate requests → one wins; other returns existing record.

**Metric:** Duplicate ingest rate.

---

## US-003: View CI runs

**Persona:** QA Automation Engineer  
**Story:** As a QA engineer, I want to list CI runs with filters so that I can find failed runs quickly.

**Business value:** Primary navigation for triage workflow.

**Priority:** Must  
**Dependencies:** US-001, US-009

**Acceptance criteria:**
- GET `/api/v1/ci-runs` supports pagination, filter by repo, branch, status, date range.
- Each item shows run ID, repo, branch, conclusion, processed status, failure count, created_at.
- Unauthenticated request returns 401.

**Edge cases:**
- Empty result set returns 200 with empty array.

**Metric:** Time to locate target failed run (efficiency).

---

## US-004: View failure details

**Persona:** QA Automation Engineer  
**Story:** As a QA engineer, I want to see normalized failure details and raw evidence so that I can validate AI output.

**Business value:** Trust through transparency.

**Priority:** Must  
**Dependencies:** US-003

**Acceptance criteria:**
- GET `/api/v1/failures/{id}` returns normalized fields, masked logs, linked CI run, classification if present.
- Evidence references in classification map to fields in response.

**Edge cases:**
- Failure not yet classified → classification section null with status `pending`.

**Metric:** Classification review completion rate.

---

## US-005: AI classify failure

**Persona:** System  
**Story:** As the platform, I want to classify each failure with structured AI output so that triage starts with a suggested category and action.

**Business value:** Core AI value proposition.

**Priority:** Must  
**Dependencies:** US-004 processing pipeline

**Acceptance criteria:**
- Classification includes: category, subcategory, suspected_component, summary, likely_cause, suggested_action, confidence, evidence_refs, insufficient_information flag.
- Output validated by Pydantic schema.
- Provider failure triggers fallback chain; ultimate fallback is rule-based.
- AI metadata stored: provider, model, prompt_version, input_hash, tokens, duration, trace_id.
- AI output never overwritten by feedback.

**Edge cases:**
- All providers fail → rule-based classification with low confidence and insufficient_information=true where applicable.
- Prompt injection in logs → classification does not execute tool instructions; eval case covers this.

**Metric:** Median time from ingest to classification; fallback rate.

---

## US-006: View similar failures

**Persona:** QA Automation Engineer  
**Story:** As a QA engineer, I want to see historically similar failures so that I can tell if this is a known issue.

**Business value:** Reduces repeated investigation.

**Priority:** Must  
**Dependencies:** US-005

**Acceptance criteria:**
- Similar failures returned with match method, score, date, prior classification summary.
- Search scoped to same repository, 90-day window, max 20 candidates.
- Matching is deterministic (documented algorithm).

**Edge cases:**
- No matches → empty list with message `no_similar_failures_found`.

**Metric:** Similar-failure match rate.

---

## US-007: View release-risk assessment

**Persona:** Release Manager / QA Engineer  
**Story:** As a release stakeholder, I want an explainable release-risk assessment so that I can make an informed advisory decision.

**Business value:** Connects failures to release readiness narrative.

**Priority:** Must  
**Dependencies:** US-005, US-006

**Acceptance criteria:**
- GET `/api/v1/releases/{id}/assessment` or nested under CI run returns risk_level, score, factors, missing_info, recommendation, explanation.
- Score computed deterministically — not LLM-generated.
- Recommendation is advisory (proceed / caution / hold) with rationale.

**Edge cases:**
- Incomplete data → risk includes `missing_info` entries and lower confidence band.

**Metric:** User review of assessment (qualitative in MVP).

---

## US-008: Submit classification feedback

**Persona:** QA Automation Engineer  
**Story:** As a QA engineer, I want to accept or correct a classification so that the system learns from human judgment.

**Business value:** Human-in-the-loop governance and eval data.

**Priority:** Must  
**Dependencies:** US-005

**Acceptance criteria:**
- POST `/api/v1/failures/{id}/feedback` accepts accept, category correction, component correction, note, resolved flag, cluster link.
- Stores original AI snapshot and correction diff.
- Returns 201 with feedback record ID.

**Edge cases:**
- Feedback on failure without classification → 409 Conflict.

**Metric:** Classification acceptance rate; correction rate.

---

## US-009: Authenticate and isolate org data

**Persona:** Any user  
**Story:** As a user, I want to log in and see only my organization's data so that repository information stays isolated.

**Business value:** Minimum viable security for demo and portfolio.

**Priority:** Must  
**Dependencies:** M1 auth

**Acceptance criteria:**
- JWT login returns token; protected routes require valid token.
- User cannot access other org CI runs (403/404).
- Role: at minimum `viewer` and `analyst` (can submit feedback).

**Edge cases:**
- Expired token → 401 with refresh guidance.

**Metric:** Unauthorized access attempts blocked (audit).

---

## US-010: Replay seed demo data

**Persona:** Portfolio reviewer / QA Engineer  
**Story:** As a demo operator, I want to seed realistic CI failure data so that the full workflow is demonstrable without live GitHub.

**Business value:** Reliable portfolio demo on free tier.

**Priority:** Must  
**Dependencies:** M1 seed command

**Acceptance criteria:**
- `make seed` or equivalent loads org, users, repos, 5+ CI runs with varied failures.
- Seed is idempotent or documented reset procedure exists.
- README lists demo credentials.

**Edge cases:**
- Re-seed on non-empty DB → documented behavior (reset or skip).

**Metric:** Demo setup time < 15 minutes.

---

## US-011: View operational metrics

**Persona:** QA Automation Engineer / Operator  
**Story:** As an operator, I want a metrics summary so that I can see processing health and AI fallback rates.

**Priority:** Should  
**Dependencies:** Observability instrumentation

**Acceptance criteria:**
- GET `/api/v1/metrics/summary` returns ingest success, processing latency, classification count, acceptance rate, fallback rate.
- Values computed from DB — not hardcoded.

**Metric:** Metrics API availability.

---

## US-012: Audit important actions

**Persona:** Operator  
**Story:** As an operator, I want an audit trail of webhooks and feedback so that actions are traceable.

**Priority:** Should  
**Dependencies:** US-001, US-008

**Acceptance criteria:**
- Audit events for webhook received, classification completed, feedback submitted.
- Each entry: actor, action, resource, timestamp, correlation_id.

**Metric:** Audit log completeness for critical flows.
