# Product Metrics

## Principles

- Do not claim improvement unless measured in the platform.
- Every metric includes definition, formula, data source, importance, and limitations.
- MVP instruments a subset; full dashboard may lag implementation.

---

## North-star metric

### Median time from CI failure ingestion to actionable classification

| Field | Value |
|-------|-------|
| **Definition** | Elapsed time from webhook/seed ingest timestamp to all failures in the run having a classification record available via API |
| **Formula** | `median(classification_completed_at - ingested_at)` per CI run |
| **Data source** | `ci_runs.ingested_at`, `classifications.completed_at` |
| **Why it matters** | Captures core product promise: faster triage |
| **Limitations** | Includes worker queue delay; cold starts skew first request; free LLM latency variable |

---

## Adoption metrics

### Weekly active users (WAU)

| Field | Value |
|-------|-------|
| **Definition** | Distinct users with ≥1 authenticated API/UI action in 7 days |
| **Formula** | `count(distinct user_id)` in rolling 7-day window |
| **Data source** | Audit log / session activity |
| **Why it matters** | Indicates whether team uses the platform |
| **Limitations** | MVP may only have demo users; meaningful post-pilot only |

### Repositories connected

| Field | Value |
|-------|-------|
| **Definition** | Count of repositories with ≥1 ingested CI run in 30 days |
| **Formula** | `count(distinct repository_id)` |
| **Data source** | `ci_runs` |
| **Why it matters** | Breadth of adoption |
| **Limitations** | Seed data inflates early counts — label demo vs live |

---

## Engagement metrics

### Classifications reviewed per week

| Field | Value |
|-------|-------|
| **Definition** | Count of failures where user viewed detail page or submitted feedback |
| **Formula** | `count(failure_views)` or `count(feedback_events)` |
| **Data source** | Frontend analytics or audit log |
| **Why it matters** | Distinguishes ingestion from actual triage usage |
| **Limitations** | View tracking requires frontend instrumentation |

### Feedback submission rate

| Field | Value |
|-------|-------|
| **Definition** | Percentage of classified failures receiving human feedback within 7 days |
| **Formula** | `feedback_count / classified_failure_count * 100` |
| **Data source** | `human_feedback`, `classifications` |
| **Why it matters** | Human-in-the-loop engagement |
| **Limitations** | Low volume in demo |

---

## Efficiency metrics

### Classification acceptance rate

| Field | Value |
|-------|-------|
| **Definition** | Percentage of feedback events that are accept (no correction) |
| **Formula** | `accept_count / total_feedback * 100` |
| **Data source** | `human_feedback.action` |
| **Why it matters** | Proxy for AI usefulness |
| **Limitations** | Users may not feedback on correct items; selection bias |

### Classification correction rate

| Field | Value |
|-------|-------|
| **Definition** | Percentage of feedback events with category or component correction |
| **Formula** | `correction_count / total_feedback * 100` |
| **Data source** | `human_feedback` |
| **Why it matters** | Identifies taxonomy/prompt improvement areas |
| **Limitations** | Requires sufficient feedback volume |

### Similar-failure match rate

| Field | Value |
|-------|-------|
| **Definition** | Percentage of failures with ≥1 similar match above score threshold |
| **Formula** | `failures_with_matches / total_failures * 100` |
| **Data source** | `similar_failure_links` |
| **Why it matters** | Validates retrieval utility |
| **Limitations** | Threshold choice affects rate; sparse history lowers matches |

---

## AI-quality metrics

### AI provider fallback rate

| Field | Value |
|-------|-------|
| **Definition** | Percentage of classifications not using primary provider (Groq) |
| **Formula** | `non_primary_classifications / total * 100` |
| **Data source** | `classifications.provider` |
| **Why it matters** | Free-tier health indicator |
| **Limitations** | High fallback may still produce acceptable output via Gemini/rules |

### Eval suite pass rate

| Field | Value |
|-------|-------|
| **Definition** | Percentage of eval cases meeting category and guardrail expectations |
| **Formula** | `passed_cases / total_cases * 100` |
| **Data source** | `tests/evals/` report output |
| **Why it matters** | Objective AI quality between prompt changes |
| **Limitations** | Synthetic data; not production distribution |

### Insufficient-information rate

| Field | Value |
|-------|-------|
| **Definition** | Percentage of classifications flagged insufficient_information |
| **Formula** | `insufficient_count / total * 100` |
| **Data source** | `classifications.insufficient_information` |
| **Why it matters** | Measures honest uncertainty vs overconfident guesses |
| **Limitations** | May increase if guardrails tightened (good) |

### Schema compliance rate

| Field | Value |
|-------|-------|
| **Definition** | Percentage of AI responses passing Pydantic validation on first attempt |
| **Formula** | `first_pass_valid / total_ai_calls * 100` |
| **Data source** | Classification service logs |
| **Why it matters** | Free models may need repair retries |
| **Limitations** | Repair retries excluded from first-pass numerator |

---

## Reliability metrics

### Webhook processing success rate

| Field | Value |
|-------|-------|
| **Definition** | Percentage of webhook requests successfully persisted and enqueued |
| **Formula** | `(ingested - ingest_errors) / total_webhooks * 100` |
| **Data source** | Webhook handler logs, audit |
| **Why it matters** | Pipeline entry reliability |
| **Limitations** | Seed ingest may use separate path |

### Worker processing success rate

| Field | Value |
|-------|-------|
| **Definition** | Percentage of CI runs reaching `completed` status |
| **Formula** | `completed_runs / total_runs * 100` |
| **Data source** | `ci_runs.status` |
| **Why it matters** | End-to-end pipeline health |
| **Limitations** | Permanent failures need separate tracking |

### Worker processing latency (p50 / p95)

| Field | Value |
|-------|-------|
| **Definition** | Time from enqueue to run status `completed` |
| **Formula** | Percentiles of `completed_at - enqueued_at` |
| **Data source** | `ci_runs` timestamps |
| **Why it matters** | User wait time for results |
| **Limitations** | LLM and cold start dominate tail |

---

## Cost metrics

### Model cost per processed run

| Field | Value |
|-------|-------|
| **Definition** | Sum of estimated API cost for all classifications in a CI run |
| **Formula** | `sum(classifications.estimated_cost_usd)` — **$0 for free tier** |
| **Data source** | `classifications` |
| **Why it matters** | Future paid adapter planning |
| **Limitations** | Free tier records tokens but cost=0 |

### Token usage per classification

| Field | Value |
|-------|-------|
| **Definition** | Input + output tokens per AI call |
| **Formula** | `input_tokens + output_tokens` |
| **Data source** | `classifications` |
| **Why it matters** | Quota management on free tiers |
| **Limitations** | Providers report tokens inconsistently |

---

## MVP instrumentation priority

1. Must instrument at launch: ingest success, worker latency, fallback rate, acceptance/correction rate, north-star timing.
2. Should instrument: similar-match rate, eval pass rate, schema compliance.
3. Could defer: WAU, view tracking (post demo hardening).
