# ADR-007: Authentication Approach

## Status

Accepted

## Context

MVP needs org-isolated authenticated access for dashboard and API. Portfolio demo requires reliable credentials.

## Decision

**JWT + bcrypt password auth** with seeded demo users. GitHub OAuth deferred to v1.1.

## Options considered

| Option | Advantages | Disadvantages |
|--------|------------|---------------|
| JWT + email/password | Simple, reliable demo | Not SSO |
| GitHub OAuth only | Nice for dev audience | Demo credential fragility |
| Session cookies | Familiar | CSRF handling |

## Consequences

- Login endpoint returns JWT; frontend stores in memory or httpOnly cookie.
- Roles: viewer, analyst, admin.
- OAuth can be added without breaking JWT clients.

## Revisit conditions

- Demo requires login-as GitHub user for credibility.
- Enterprise SSO requirement emerges.
