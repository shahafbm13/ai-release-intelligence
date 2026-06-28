# Definition of Done

## Feature done

A feature is **done** when all applicable items below are satisfied:

### Code
- [ ] Implementation matches approved user story acceptance criteria
- [ ] Business logic in services/domain — not in route handlers
- [ ] No secrets or credentials in code
- [ ] Temporary shortcuts marked with `# TECH DEBT:` comment and backlog ID

### Tests
- [ ] Unit tests for domain rules and pure functions
- [ ] Integration tests for API/DB/worker paths (if applicable)
- [ ] Contract tests for external payloads (if applicable)
- [ ] All existing tests pass locally and in CI

### AI features (additional)
- [ ] Pydantic schema validation on model output
- [ ] Fallback behavior tested
- [ ] Eval case added or updated if behavior changed
- [ ] Provider, prompt_version, tokens logged

### Documentation
- [ ] OpenAPI reflects new/changed endpoints
- [ ] README updated if setup or env vars changed
- [ ] ADR created or updated for architectural decisions
- [ ] Session log entry in [05-milestone-status.md](./05-milestone-status.md) if handoff-relevant decisions made

### Observability
- [ ] Structured logs with correlation_id
- [ ] Errors logged at appropriate level
- [ ] Metrics instrumented if listed in story

### Security
- [ ] Auth/authz enforced on new endpoints
- [ ] Input validated server-side
- [ ] CI logs masked before AI if feature touches logs

---

## Milestone done

A milestone is **done** when:

- [ ] All P0 backlog items for milestone complete
- [ ] Exit criteria from `02-milestones.md` met
- [ ] Demo scenario rehearsed successfully
- [ ] Known issues documented honestly
- [ ] Backlog updated for next milestone
- [ ] No blocker bugs for demo path
- [ ] [05-milestone-status.md](./05-milestone-status.md) and [HANDOFF.md](../HANDOFF.md) updated (milestone Done, exit criteria checked, session log)

---

## MVP done (Phase B complete)

MVP is **done** when:

- [ ] All M1–M6 milestones complete
- [ ] Public demo URL accessible (cold start documented)
- [ ] Full user journey: ingest → classify → similar → risk → feedback
- [ ] Metrics API returns computed values
- [ ] AI eval report generated (mocked CI minimum)
- [ ] Case study and portfolio docs complete
- [ ] Phase A non-goals verified excluded
- [ ] Post-launch review template filled with baseline metrics (no invented improvements)

---

## Not required for MVP done

- Pixel-perfect UI design
- 100% test coverage
- Always-on hosting
- Paid LLM quality parity
- Real GitHub production webhook
- Multi-org support
