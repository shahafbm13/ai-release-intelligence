# ADR-002: PostgreSQL

## Status

Accepted

## Context

Need relational storage for CI runs, failures, classifications, feedback, audit events, and idempotency constraints.

## Decision

Use **PostgreSQL** (Neon free tier prod; Docker local).

## Options considered

| Option | Advantages | Disadvantages |
|--------|------------|---------------|
| PostgreSQL | ACID, JSONB, mature, free tier via Neon | Operational setup |
| SQLite | Simple local | Poor concurrent worker writes |
| MongoDB | Flexible docs | Weaker relational integrity for audit |

## Consequences

- Foreign keys enforce referential integrity.
- JSONB for factors and evidence_refs.
- pgvector available later on same engine if needed.

## Revisit conditions

- Extreme write volume requiring sharding (post-MVP).
- Need for multi-region active-active.
