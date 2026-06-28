# Launch and Rollout Plan

## Launch phases

### Phase 0: Local demo launch

**Goal:** Runnable on developer machine via Docker Compose.

**Steps:**
1. Clone repo; copy `.env.example` to `.env`.
2. Configure Groq/Gemini API keys (free).
3. `docker compose up`; run migrations and seed.
4. Walk through triage flow locally.

**Exit criteria:** E2E test passes locally; demo script validated.

---

### Phase 1: Seeded-data launch

**Goal:** Public URL serving pre-seeded demo without live GitHub dependency.

**Steps:**
1. Deploy to Render free tier + Neon + Upstash.
2. Run migrations and seed on deploy.
3. Document demo credentials in README (non-production passwords).
4. Verify wake-from-cold-start procedure.

**Exit criteria:** Reviewer can complete journey in < 15 minutes including cold start.

---

### Phase 2: Controlled GitHub integration (post-MVP / v1)

**Goal:** One demo repository sends real webhooks.

**Steps:**
1. Register webhook on demo repo with secret in Render env.
2. Map repository to org in platform.
3. Process 5 real failed runs; compare with seed behavior.

**Exit criteria:** Real run appears in dashboard within 2 minutes (warm).

---

## Observability checks (pre-launch)

- [ ] `/health` returns 200
- [ ] `/ready` confirms DB + Redis connectivity
- [ ] Structured logs include correlation_id
- [ ] Failed worker tasks visible in logs/metrics
- [ ] Fallback rate metric populated after test classifications

## Rollback strategy

| Scenario | Action |
|----------|--------|
| Bad deploy | Revert to previous Render deploy image |
| Bad migration | Run down migration; restore Neon branch snapshot if available |
| AI provider outage | Automatic rule fallback; no deploy rollback needed |
| Data corruption | Re-run seed reset script (demo environment only) |

## Known limitations (document publicly)

- Free hosting cold starts (~30–60s after idle).
- Free LLM quality below paid models; higher correction rate expected.
- Secret masking is best-effort, not guaranteed.
- Release-risk is advisory only.
- GitHub webhook requires enrichment for test failure details in MVP fixtures.
- Single-organization demo.

## Communication

- README: setup, limitations, demo script link.
- Case study: scope trade-offs and free-tier decisions.

## Success criteria for launch

- Complete user journey demonstrable on public URL.
- Metrics API returns real computed values (not placeholders).
- AI eval suite passes with mocked provider in CI.
