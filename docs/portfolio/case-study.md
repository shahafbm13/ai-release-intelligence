# Case Study: AI Release Intelligence Platform

## Problem

QA automation teams spend significant time triaging CI failures: reading logs, guessing root causes, and debating release readiness without structured evidence. Commercial tools solve slices of this problem but do not demonstrate end-to-end product ownership on a $0 stack.

## Solution

A modular monolith that ingests CI failure signals, classifies failures through a free LLM chain with deterministic fallbacks, surfaces similar historical failures, computes an explainable release-risk score, and captures human feedback for continuous improvement.

## Architecture highlights

- **FastAPI + Celery + PostgreSQL + Redis** — async processing with idempotent webhook ingest
- **Groq → Gemini → rules** classification chain with JSON repair and schema validation
- **Deterministic risk engine** — six weighted factors; not LLM-generated (ADR-008)
- **Immutable AI records** — corrections stored as separate feedback events
- **Next.js dashboard** — login, triage, metrics, admin replay

## Scope trade-offs (MVP)

| Included | Deferred |
|----------|----------|
| Seeded GitHub-shaped events | Live GitHub OAuth |
| Rule + free LLM classification | Paid OpenAI tier |
| Baseline similar-failure matcher | pgvector semantic search |
| Single-org demo | Multi-tenant SaaS |
| Advisory release risk | Auto release gate |

## Quality evidence (measured, not invented)

Metrics below come from the repo's test and eval tooling — run locally or in CI:

| Metric | Source | How to reproduce |
|--------|--------|------------------|
| Automated test count | `pytest tests/ -v` | Full suite with Docker Postgres + Redis |
| Eval pass rate | `python tests/evals/runner.py` | 10-case rules baseline dataset (`tests/evals/data/v1/`) |
| Risk engine golden tests | `pytest tests/unit/test_risk_engine.py` | Deterministic factor weights |
| E2E critical path | `pytest tests/e2e -v` | Ingest → classify → assess → feedback |

Do not cite specific pass rates in interviews until you have run the commands in your environment and recorded the output.

## Outcomes for users

1. **Faster triage** — failures arrive pre-classified with evidence refs and suggested actions.
2. **Explainable release advice** — risk panel shows factor contributions, not a black-box score.
3. **Governance** — analysts accept or correct classifications; audit trail preserved.

## What I would do next (v1)

- Real GitHub webhook on a demo repo (BL-100)
- Live eval workflow with Groq key for LLM-path accuracy
- pgvector experiment vs baseline matcher (BL-103)
- Slack notification spike for failed-run alerts

## Links

- [README](../../README.md)
- [Demo script](./demo-script.md)
- [Architecture overview](../architecture/08-ai-architecture.md)
- [Eval report generator](../../tests/evals/runner.py)
