# Product Requirements Document (PRD)

## Document status

Draft — Phase A. Pending final approval in `14-phase-a-review.md`.

## 1. Problem

Engineering teams lack a structured, evidence-backed workflow for triaging CI failures and assessing release risk. Context is fragmented; AI chat tools lack auditability and deterministic risk scoring.

## 2. Users

| User | Need |
|------|------|
| QA Automation Engineer (primary) | Fast, trustworthy failure triage |
| Software Engineer | View and correct classifications |
| Release Manager | Explainable release-risk summary |

## 3. Goals

- Reduce time-to-first-actionable-classification for failed CI runs.
- Provide explainable, advisory release-risk assessments.
- Capture human feedback for AI quality measurement.
- Demonstrate production-oriented architecture on $0 infrastructure.

## 4. Non-goals (MVP)

Multi-org, incidents, deployments, notifications, auto release gate, paid hosting default, semantic retrieval.

## 5. Scope summary

Single org, 2–5 repos, seeded CI events, full triage loop, minimal dashboard, free-tier deploy.

See [02-scope-and-prioritization.md](./02-scope-and-prioritization.md).

## 6. Requirements traceability

| Requirement area | Document |
|------------------|----------|
| User journeys | [03-user-journeys.md](./03-user-journeys.md) |
| User stories | [04-user-stories.md](./04-user-stories.md) |
| Functional | [05-functional-requirements.md](./05-functional-requirements.md) |
| Non-functional | [06-non-functional-requirements.md](./06-non-functional-requirements.md) |
| AI guardrails | [09-ai-behavior-and-guardrails.md](./09-ai-behavior-and-guardrails.md) |
| API contract | [11-api-consumer-contract.md](./11-api-consumer-contract.md) |

## 7. Metrics

North-star: median ingest-to-classification time.

See [07-product-metrics.md](./07-product-metrics.md).

## 8. Risks

Top risks: free-tier limits, AI misclassification, prompt injection, scope creep.

See [08-risk-register.md](./08-risk-register.md).

## 9. Dependencies

- Groq free API key
- Google Gemini free API key
- Neon Postgres free tier
- Upstash Redis free tier
- Render free web tier
- Docker for local development

## 10. Architecture summary

Modular monolith (FastAPI) + Celery worker; PostgreSQL; free LLM adapter chain.

See `docs/architecture/`.

## 11. Rollout plan

See [12-launch-and-rollout-plan.md](./12-launch-and-rollout-plan.md).

## 12. Milestones

See `docs/delivery/02-milestones.md`.

## 13. Open questions

- Final repo display name for GitHub.
- Whether to add GitHub OAuth in v1 or post-MVP.

## 14. Approval

| Role | Status | Date |
|------|--------|------|
| Product owner | Pending final Phase A sign-off | — |
