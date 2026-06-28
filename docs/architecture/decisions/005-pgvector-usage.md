# ADR-005: pgvector Usage

## Status

Accepted (deferred — not in MVP)

## Context

Similar-failure retrieval could use semantic embeddings for fuzzy matching.

## Decision

**Do not use pgvector in MVP.** Implement deterministic baseline matching first.

## Options considered

| Option | Advantages | Disadvantages |
|--------|------------|---------------|
| Deterministic matching | Zero cost, explainable, testable | Misses paraphrased errors |
| pgvector + embeddings | Better semantic recall | Cost/complexity; needs embedding pipeline |
| External vector DB | Scalable | Extra service |

## Baseline algorithm (MVP)

1. Filter same repository, 90 days.
2. Score: exact normalized message match (high), test name match (medium), error type match (low).
3. Return top 5 above threshold.

## Consequences

- Store match method and score on each link.
- Collect metrics on match rate before investing in embeddings.

## Revisit conditions

- Baseline match rate < 40% on seeded/historical data.
- User feedback indicates repeated misses for obviously similar failures.
