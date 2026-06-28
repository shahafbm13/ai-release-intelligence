# ADR-003: Celery versus Temporal

## Status

Accepted

## Context

Webhook ingestion requires async processing for classification and risk computation. Workflow includes retries and idempotent tasks.

## Decision

Use **Redis + Celery** for MVP background processing.

## Options considered

| Option | Advantages | Disadvantages |
|--------|------------|---------------|
| Celery + Redis | Simple, well-known, sufficient for linear pipeline | Less visibility for complex sagas |
| Temporal | Durable workflows, visibility | Operational complexity, learning curve |
| ARQ / RQ | Lighter | Smaller ecosystem |

## Consequences

- Linear task chain: process_ci_run orchestrates steps in code.
- Retry/backoff configured per task.
- Revisit Temporal if workflows become multi-day sagas with compensation.

## Revisit conditions

- Need durable workflow state across deploys with complex branching.
- Multiple coordinated long-running human approval steps.
