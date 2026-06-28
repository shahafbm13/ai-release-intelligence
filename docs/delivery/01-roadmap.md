# Roadmap

## Horizon overview

| Horizon | Timeline | Theme |
|---------|----------|-------|
| MVP | Weeks 1–8 | CI triage + release risk on $0 stack |
| v1 | Weeks 9–12 | Real GitHub webhook, OAuth, quality hardening |
| v2 | Future | Multi-org, semantic retrieval, notifications |

## MVP roadmap (M0–M6)

```mermaid
gantt
  title MVP Roadmap
  dateFormat YYYY-MM-DD
  section Planning
  M0_Planning           :m0, 2026-06-17, 5d
  section Backend
  M1_Core               :m1, after m0, 7d
  M2_Ingest             :m2, after m1, 7d
  M3_Classification     :m3, after m2, 10d
  section Intelligence
  M4_Risk_Feedback      :m4, after m3, 10d
  section Delivery
  M5_UI_Deploy          :m5, after m4, 10d
  M6_Evals_Portfolio    :m6, after m5, 7d
```

## MVP deliverables

1. Full Phase A documentation (complete)
2. Runnable monorepo with API, worker, web
3. Seed demo with 5+ failure scenarios
4. Free-tier deployment with documented limitations
5. AI eval suite and case study materials

## v1 goals

- Controlled GitHub webhook on demo repo
- GitHub OAuth login
- Optional OpenAI adapter for quality comparison
- Improved flaky detection signal

## v2 possibilities

- Multi-organization support
- pgvector semantic retrieval
- Slack notifications
- Deployment correlation
- AWS deployment option

## Decision log

All major decisions in `docs/architecture/decisions/`.

## Roadmap review

Update at each milestone exit and in post-launch review template.
