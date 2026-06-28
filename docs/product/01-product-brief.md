# Product Brief

## Product name

**AI Release Intelligence Platform**

## One-sentence value proposition

Turn CI failure signals into evidence-backed classifications and explainable release-risk assessments so teams can triage faster and ship with clearer confidence.

## Problem statement

Engineering teams lose hours triaging failed CI runs because failure context is scattered across logs, test artifacts, PR history, and tribal knowledge. Release decisions are often made with incomplete understanding of whether failures are new regressions, flaky tests, environment issues, or known incidents.

## Why this problem matters

- Failed CI runs block merges and releases daily.
- Misclassification wastes engineering time and erodes trust in automation.
- Release managers lack a single, auditable view of risk tied to evidence.
- Generic AI chat tools produce unstructured answers without confidence, evidence, or feedback loops.
- Teams repeatedly investigate the same failure signatures without institutional memory.

## Target users

| Persona | MVP role |
|---------|----------|
| **QA Automation Engineer** | Primary — triages failures, validates classifications |
| Software Engineer | Secondary — views failures, submits feedback |
| Release Manager | Secondary — consumes release-risk assessments |
| Engineering Manager | Future — team-level trends |
| DevOps Engineer | Future — infrastructure failure patterns |
| Technical Product Owner | Evaluator — product narrative and scope |

## Primary persona (MVP)

**QA Automation Engineer**

Rationale: closest to the core workflow (investigate automation failures, classify root causes, advise on release readiness), strongest alignment with portfolio background, and highest frequency of the primary use case.

## Secondary personas (MVP)

- **Software Engineer** — views run details and corrects misclassifications.
- **Release Manager** — reads advisory release-risk output before a release decision.

## Primary use case (MVP)

**Pre-release CI failure triage for a single team**

When a GitHub Actions workflow fails, the platform ingests the run (via seed fixture or webhook), normalizes failures, produces an AI-assisted classification with evidence, finds similar historical failures using deterministic matching, computes an explainable release-risk score, and lets the QA engineer accept or correct the result.

## Current workflow without the product

1. CI fails; engineer receives Slack/email alert.
2. Engineer opens CI UI and raw logs across multiple tabs.
3. Engineer manually searches past runs and incident notes.
4. Engineer guesses root cause (regression, flake, env, infra).
5. Engineer reruns tests or debates release readiness without structured evidence.
6. No durable record of the classification decision.

## Pain points

| Pain point | Impact |
|------------|--------|
| Context switching across CI UI, logs, and history | Slow triage, cognitive load |
| Repeated investigation of same signatures | Wasted hours |
| Subjective release decisions | Risky or delayed releases |
| Unstructured AI answers | Low trust, no audit trail |
| No feedback loop on classifications | AI quality cannot improve |

## Proposed workflow with the product

1. CI event ingested (seed replay or webhook).
2. Failures normalized and secrets masked.
3. Background worker classifies each failure (free LLM with fallback chain).
4. Similar historical failures retrieved deterministically.
5. Release-risk engine computes advisory score from explainable factors.
6. QA engineer reviews classification, evidence, and risk in dashboard.
7. Engineer accepts or corrects classification; feedback stored immutably.
8. Metrics and eval data captured for quality monitoring.

## Product assumptions

- MVP serves **one organization** with **2–5 repositories**.
- Initial data comes from **realistic fixtures** mimicking GitHub Actions payloads.
- **Zero paid services** for demo: Groq/Gemini free APIs, Render/Neon/Upstash free tiers.
- Weaker AI quality and cold-start latency on free hosting are acceptable.
- Users authenticate via JWT with seeded demo users.
- Release-risk output is **advisory only** — no automatic release gate.
- Real GitHub webhook integration is optional post-MVP.

## Risks and unknowns

- Free-tier LLM rate limits and inconsistent structured output.
- AI misclassification despite guardrails.
- Sensitive data in CI logs despite masking.
- Prompt injection via malicious log content.
- Scope creep into full incident/deployment platform.
- Demo cold starts on Render free tier.

## Alternatives and competitors (conceptual)

| Alternative | Limitation relative to this product |
|-------------|-------------------------------------|
| GitHub Actions native summaries | No cross-run intelligence or release-risk engine |
| Datadog / Sentry | Observability-focused, not CI triage workflow |
| ChatGPT / IDE assistants | Unstructured, no audit trail or deterministic risk |
| ReportPortal / Launchable | Commercial; not a portfolio-owned platform narrative |
| Manual spreadsheets / Slack threads | No normalization, AI assist, or metrics |

## Why this project is useful as a portfolio project

Demonstrates **technical product ownership** (discovery, scope, metrics, rollout) and **production engineering** (webhooks, async processing, deterministic + AI separation, evals, observability) without repeating a shallow CRUD app or chatbot wrapper. Extends existing background in test automation, failure investigation, and AI-assisted classification.

## Decision log reference

See `docs/architecture/decisions/` for architectural choices and `docs/product/14-phase-a-review.md` for MVP approval summary.
