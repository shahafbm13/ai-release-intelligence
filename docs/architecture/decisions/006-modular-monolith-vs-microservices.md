# ADR-006: Modular Monolith versus Microservices

## Status

Accepted

## Context

Solo developer MVP; need webhook ACK + async processing without operational overhead.

## Decision

**Modular monolith** — one codebase with API and worker processes sharing domain packages. **Not microservices.**

## Options considered

| Option | Advantages | Disadvantages |
|--------|------------|---------------|
| Modular monolith | Simple deploy, shared transactions, fast iteration | Single scale unit |
| Microservices | Independent scale | Ops burden, distributed debugging |
| Single process | Simplest | Webhook timeout risk |

## Consequences

- Clear package boundaries enable future extraction.
- Two processes minimum: API (fast) + worker (slow).
- On Render free tier: co-locate API + worker in one container.

## Revisit conditions

- Separate teams owning ingestion vs classification.
- Independent scaling requirements with proven bottlenecks.
