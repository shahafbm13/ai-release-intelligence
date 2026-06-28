# ADR-010: Deployment Choice

## Status

Accepted

## Context

MVP requires $0 operating cost, public demo URL, PostgreSQL, Redis, and acceptable cold starts.

## Decision

| Component | Platform |
|-----------|----------|
| API + Worker | Render free web service (co-located) |
| PostgreSQL | Neon free tier |
| Redis | Upstash free tier |
| CI | GitHub Actions free tier |
| Local | Docker Compose |

## Options considered

| Option | Advantages | Disadvantages |
|--------|------------|---------------|
| Render + Neon + Upstash | $0, simple | Cold starts, free limits |
| Railway | Easy DX | Limited free credits |
| AWS ECS/RDS | Production cred | Cost, complexity |
| Fly.io | Good free allowance | More config |

## Consequences

- Demo script includes service wake-up step.
- Pre-seeded classifications backup live AI demo.
- README documents spin-down behavior.
- AWS deferred until meaningful engineering narrative.

## Revisit conditions

- Free tier limits block demos consistently.
- Need always-on SLA for pilot users.
- Portfolio reviewer requires AWS specifically.
