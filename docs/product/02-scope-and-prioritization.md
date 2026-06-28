# Scope and Prioritization

## Product vision

Become the trusted internal platform that transforms CI failure signals into actionable, evidence-backed release intelligence — combining deterministic engineering rigor with AI-assisted triage.

## MVP objective

Deliver a polished, demo-ready **CI failure triage and release-risk assessment** workflow for a single organization, using seeded data and free-tier infrastructure, that a QA Automation Engineer can complete end-to-end in under 10 minutes.

## MVP non-goals

- Multi-organization tenancy
- Incident and deployment record ingestion
- Notifications (Slack, email)
- Automatic release blocking
- pgvector / semantic retrieval
- Always-on paid hosting
- Kubernetes
- Full commercial design system

## Version 1 goals (post-MVP)

- Controlled real GitHub webhook on one demo repository
- Improved classification quality (optional paid model adapter)
- GitHub OAuth login
- Enhanced flaky-test detection as risk factor
- Semantic similar-failure retrieval (pgvector) compared against baseline

## Future possibilities

- Multi-org SaaS with billing
- Integration with PagerDuty / incident tools
- Deployment correlation and change-scope analysis
- Team ownership mapping and routing
- Notification workflows
- Custom classification taxonomy per org
- AWS deployment for enterprise narrative

## Prioritization method

**MoSCoW** for MVP feature inclusion, with **RICE** used to rank Should-have vs Could-have when trade-offs arise.

RICE formula: `(Reach × Impact × Confidence) / Effort`

---

## Must-have (MVP)

| Feature | User problem | RICE note |
|---------|--------------|-----------|
| Seed/fixture CI ingestion | Develop and demo without live GitHub | High confidence, low effort |
| Webhook endpoint + signature validation | Production-ready ingestion pattern | High impact; fixtures first |
| Idempotent async processing (Celery) | Reliable failure handling | Core architecture |
| Failure normalization + secret masking | Safe, consistent AI input | Security + quality |
| AI classification (structured, fallback) | Faster triage | Core value |
| Deterministic similar-failure retrieval | Avoid re-investigation | Differentiator |
| Deterministic release-risk engine | Explainable release advice | Core differentiator |
| Human feedback loop | Trust + eval data | AI governance |
| Minimal Next.js dashboard | Review workflow | Required for demo |
| JWT auth + single-org isolation | Secure multi-repo access | Baseline security |
| Observability (logs, correlation IDs) | Operability | Production credibility |
| AI eval dataset (10 cases) | Quality measurement | Portfolio proof |
| Docker Compose + free-tier deploy | Runnable demo | Portfolio requirement |

## Should-have

| Feature | Rationale |
|---------|-----------|
| Audit log for webhooks and feedback | Compliance narrative |
| Metrics summary API | Operational visibility |
| Provider failover (Groq → Gemini → rules) | Free-tier reliability |
| Pre-seeded classifications for demo backup | Interview reliability |
| Demo wake-up script for cold starts | Free Render tier UX |

## Could-have

| Feature | Rationale |
|---------|-----------|
| Controlled real GitHub webhook | Stronger integration story |
| Flaky-test signal in risk engine | Uses historical pass/fail if data exists |
| Recorded demo video | Backup when rate-limited |
| OpenRouter as tertiary LLM adapter | Extra failover |

## Explicitly excluded (MVP)

| Feature | Reason |
|---------|--------|
| Multi-org | Engineering overhead; not needed for demo |
| Incident records | Scope creep |
| Deployment records | Scope creep |
| Notifications | Not core to triage loop |
| Auto release gate | Trust/risk; advisory only for MVP |
| pgvector | Baseline retrieval first |
| Paid hosting / OpenAI default | $0 constraint confirmed |
| LangGraph / Agents SDK | Over-engineering for single-step classification |
| Temporal | Celery sufficient for MVP workflows |

## Recommended MVP summary

**Option B — Triage + Release Risk MVP**

One org, multiple repos, seeded CI events, full triage loop (classify → similar → risk → feedback), free-tier deployment, honest limitations documented.

Estimated effort for one developer: **6–8 weeks** to polished MVP.
