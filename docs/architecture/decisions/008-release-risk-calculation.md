# ADR-008: Release-Risk Calculation Design

## Status

Accepted

## Context

Release-risk must be explainable and trustworthy — not an LLM-generated guess.

## Decision

**Deterministic weighted factor model** producing risk_level, score (0–100), contributing factors, missing_info, and advisory recommendation.

## Factors and weights (initial)

| Factor | Weight | Scoring logic |
|--------|--------|---------------|
| Failed test count | 20% | min(count * 5, 20) |
| Critical test failures | 25% | critical tag or naming convention * 10 each, cap 25 |
| New vs known failures | 20% | 20 if no similar match; 5 if match with same category |
| Classification confidence | 15% | (1 - avg_confidence) * 15 |
| Flaky indication | 10% | 10 if category flaky or retry_number > 0 |
| Data completeness | 10% | Deduct if missing logs/stack |

## Risk levels

| Score | Level |
|-------|-------|
| 0–25 | low |
| 26–50 | medium |
| 51–75 | high |
| 76–100 | critical |

## Recommendations

| Level | Recommendation |
|-------|----------------|
| low | proceed |
| medium | caution |
| high | hold |
| critical | hold |

## Consequences

- Unit tests with golden cases.
- Formula documented and versioned (`risk_engine_version`).
- UI shows factor breakdown.

## Revisit conditions

- Product requires ML-based risk prediction with labeled release outcomes.
- Weights tuned from measured release incident correlation data.
