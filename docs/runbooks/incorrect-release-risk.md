# Runbook: Incorrect release-risk result

## Symptoms

- Release assessment recommendation (`proceed` / `caution` / `hold`) disagrees with team judgment.
- Risk score seems too high or too low for failure mix.
- Stakeholders question deterministic formula.

## Important context

Release-risk is **deterministic code**, not LLM output (ADR-008). Scores come from `packages/domain/domain/risk_engine.py` with six weighted factors.

## Quick checks

1. **Input failures:** Risk uses classified failures for the run — verify classifications first.
2. **Factors API:** `GET /api/v1/ci-runs/{id}/assessment` returns `factors[]` with contributions and `missing_info[]`.
3. **Golden tests:** `pytest tests/unit/test_risk_engine.py -v`

## Resolution steps

1. Walk through factor breakdown with reviewer — each factor has explicit `detail` text.
2. If classification wrong, submit analyst feedback (`POST /api/v1/failures/{id}/feedback`) — does not mutate AI record.
3. To tune weights: edit risk engine constants and update golden tests; re-run full test suite.
4. Document tuning rationale in PR — risk formula changes affect portfolio narrative.

## Not a bug

- Advisory recommendation only — platform does not block releases.
- Missing deploy metadata increases `missing_info` — expected for webhook-only MVP.

## Escalation

- Compare against golden fixtures in `tests/unit/test_risk_engine.py`.
- Product metrics: [07-product-metrics.md](../product/07-product-metrics.md)
