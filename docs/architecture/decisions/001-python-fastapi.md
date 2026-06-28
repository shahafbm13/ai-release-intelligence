# ADR-001: Python and FastAPI

## Status

Accepted

## Context

Need a backend for webhook ingestion, REST API, async task enqueue, and AI adapter integration. Team strength includes Python and FastAPI.

## Decision

Use **Python 3.12** with **FastAPI**, **Pydantic v2**, **SQLAlchemy 2**, and **Alembic**.

## Options considered

| Option | Advantages | Disadvantages |
|--------|------------|---------------|
| Python + FastAPI | Fast dev, typing, OpenAPI, ecosystem | GIL for CPU-bound work (not our bottleneck) |
| Node + NestJS | Shared language with frontend | Less aligned with background |
| Java + Spring | Enterprise familiarity | Heavier MVP velocity |

## Consequences

- Shared Python code between API and worker.
- OpenAPI auto-generation for frontend and contract tests.
- Alembic manages schema migrations.

## Revisit conditions

- Need for sub-millisecond latency at scale (unlikely in MVP).
- Team pivot to different primary language.
