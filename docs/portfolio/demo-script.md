# Demo Script (with cold start)

**Duration:** ~8 minutes  
**Audience:** Hiring manager, QA lead, or technical product reviewer  
**Prerequisites:** Deployed URL or local stack; demo credentials from seed

## Before the demo (2 min)

1. **Wake the service** (Render free tier cold start ~30–60s):
   - Hit `/health` then `/ready` until both return 200.
   - Open dashboard URL; confirm login page loads.
2. **Credentials:** `analyst@demo.example.com` / `demo-pass-1`
3. **Fallback narrative:** If LLM keys not configured, classifications use rules — still valid for demo.

## Act 1 — The problem (1 min)

> "When CI fails on a release branch, teams manually read logs and debate whether to ship. This platform turns failure signals into classified incidents and an explainable risk score."

## Act 2 — Triage a failed run (3 min)

1. **Login** → navigate to **CI Runs**.
2. Open a **completed** run (not `pending`). Point out branch, conclusion, processing status.
3. **Release risk panel:** Walk through score, recommendation, and **six factors** — emphasize deterministic, not LLM.
4. **Failures table:** Open a failure detail page.
5. Show **classification** (category, summary, confidence, evidence).
6. **Similar failures:** Historical matches with same fingerprint — saves re-investigation time.
7. Submit **feedback** (accept or correct) — original AI record unchanged.

## Act 3 — Metrics and quality (2 min)

1. Open **Metrics** page — runs processed, failure categories, feedback counts.
2. Mention **eval suite:** 10 synthetic cases, CI-generated report, no invented accuracy numbers.
3. Optional: show `reports/eval-report.md` from local `python tests/evals/runner.py`.

## Act 4 — Architecture close (1 min)

> "Webhook ingest is idempotent. Worker classifies async. Risk is code, not chatbot. Everything runs on free tiers for portfolio cost target."

Highlight: modular monolith, Celery worker, Next.js UI, GitHub Actions CI.

## Admin encore (optional)

Login as `admin@demo.example.com` / `demo-pass-3` → **Admin replay** to ingest a new fixture live. Run processes synchronously — assessment appears after refresh.

## Troubleshooting during demo

| Issue | Quick fix |
|-------|-----------|
| Run stuck on pending | Mention worker; run `python -m api.process_pending` or use pre-seeded completed run |
| Cold start timeout | Pre-warm 2 min before meeting |
| Empty metrics | Run seed: `python -m api.seed` |

## Links to share afterward

- [Case study](./case-study.md)
- [README](../../README.md)
- [Deploy guide](../deploy/README.md)
